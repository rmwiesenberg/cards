import logging
from sqlmodel import select

import cv2

from cards.db import get_engine, get_num_cards
from cards.img import get_cam

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    engine = get_engine()
    logging.info(f"Ready with {get_num_cards(engine)} cards")
