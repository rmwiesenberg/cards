import json
import logging
import lzma
from pathlib import Path
from typing import Union

from sqlalchemy import Engine
from sqlmodel import Session, create_engine, select, func
from tqdm import tqdm

from cards.card import Card, Face
from cards.common import DATA_DIR, JSON

CARD_FILE_GLOB = "all-cards-*.json"
DB_FILE_NAME = "all-cards.db"
DB_FILE_PATH = Path(DATA_DIR) / DB_FILE_NAME
DB_FILE_LZMA_NAME = "all-cards.db.xz"
DB_FILE_LZMA_PATH = Path(DATA_DIR) / DB_FILE_LZMA_NAME
VERSION_FILE_PATH = Path(DATA_DIR) / "VERSION"

def get_engine(with_unpack: bool = True) -> Engine:
    if with_unpack and not DB_FILE_PATH.exists():
        logging.info(f"DB file {DB_FILE_PATH} not found. Unpacking from {DB_FILE_LZMA_PATH}...")
        with lzma.open(DB_FILE_LZMA_PATH, "r") as f:
            DB_FILE_PATH.write_bytes(f.read())
        logging.info(f"DB unpack complete to {DB_FILE_PATH}")

    return create_engine("sqlite:///" + str(DB_FILE_PATH))

def get_num_cards(engine: Engine) -> int:
    with Session(engine) as session:
        return session.exec(select(Card.id, func.count(Card.id))).first()[1]

def _init_db() -> Engine:
    DB_FILE_PATH.unlink(missing_ok=True)
    engine = get_engine(with_unpack=False)

    Card.metadata.create_all(engine)
    Face.metadata.create_all(engine)
    return engine

def _compress_db() -> None:
    if not DB_FILE_PATH.exists():
        logging.warning(f"DB file {DB_FILE_PATH} not found, not compressing")
        return

    DB_FILE_LZMA_PATH.unlink(missing_ok=True)
    with lzma.open(DB_FILE_LZMA_PATH, "w") as f:
        f.write(DB_FILE_PATH.read_bytes())

def _unpack_color_identity(data: JSON) -> JSON:
    color_identities = data["color_identity"]
    return {
        "color_identity_white": "W" in color_identities,
        "color_identity_blue": "U" in color_identities,
        "color_identity_black": "B" in color_identities,
        "color_identity_red": "R" in color_identities,
        "color_identity_green": "G" in color_identities,
    }

def _unpack_card(data: JSON) -> (Card, Union[tuple[Face], tuple[Face, Face]]):
    data.update(_unpack_color_identity(data))

    if "card_faces" in data:
        if "image_uris" in data["card_faces"][0]:
            data["front_img_uri"] = data["card_faces"][0].pop("image_uris")["png"]
            data["back_img_uri"] = data["card_faces"][1].pop("image_uris")["png"]
        elif "image_uris" in data:
            data["front_img_uri"] = data.pop("image_uris")["png"]

        return Card(**data), tuple(Face(card=data["id"], idx=idx, **f) for idx, f in enumerate(data["card_faces"]))
    else:
        data["front_img_uri"] = data.pop("image_uris")["png"]
        return Card(**data), (Face(card=data["id"], idx=0, **data),)

def _unpack_cards() -> Path:
    card_file: Path = None
    for file in DATA_DIR.glob(CARD_FILE_GLOB):
        if card_file is None:
            card_file = file
            break

    if card_file is None:
        raise FileNotFoundError(f"Could not find file matching {CARD_FILE_GLOB} in {DATA_DIR}")

    engine = _init_db()
    version = card_file.name.split("-")[-1].split(".")[0]

    VERSION_FILE_PATH.write_text(version)

    with Session(engine) as session:
        for line in tqdm(card_file.open()):
            if not line.startswith("{"):
                continue

            entry = json.loads(line.strip().rstrip(","))
            if entry["object"] != "card":
                continue

            card, faces = _unpack_card(entry)
            session.add(card)
            for face in faces:
                session.add(face)

        logging.info("Finishing db write...")
        session.commit()
        logging.info("Compressing db...")
        _compress_db()
        logging.info("Done unpacking!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    num_cards = _unpack_cards()
