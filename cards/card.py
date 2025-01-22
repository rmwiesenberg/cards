from sqlmodel import SQLModel, Field


class Face(SQLModel, table=True):
    card: str = Field(primary_key=True)
    idx: int = Field(primary_key=True)

    name: str
    type_line: str = Field(default='')

    cmc: int = Field(default=None, nullable=True)

class Card(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    name: str
    lang: str

    layout: str

    set: str
    set_name: str

    front_img_uri: str = Field(default='')
    back_img_uri: str = Field(default='')

    color_identity_white: bool
    color_identity_blue: bool
    color_identity_black: bool
    color_identity_red: bool
    color_identity_green: bool
