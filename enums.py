import enum


class ComponentType(enum.Enum):
    variant = "variant"
    control = "control"


class ControlType(enum.Enum):
    reveal = "reveal"
    unvote = "unvote"
