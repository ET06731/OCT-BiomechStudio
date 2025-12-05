from enum import IntEnum
from typing import Dict


class Label(IntEnum):
    Background = 0
    ILM = 1
    OPL_Henles = 2
    IS_OS = 3
    IBRPE = 4
    OBRPE = 5


LABEL_COLORS: Dict[Label, str] = {
    Label.Background: "#000000",
    Label.ILM: "#FF0000",
    Label.OPL_Henles: "#00FF00",
    Label.IS_OS: "#FFFF00",
    Label.IBRPE: "#0000FF",
    Label.OBRPE: "#800080",
}
