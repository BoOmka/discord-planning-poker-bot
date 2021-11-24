import enum

from models import (
    CustomPartialEmoji,
    UnitSelectOption,
)


class ComponentType(enum.Enum):
    variant = "variant"
    control = "control"
    select = "select"


class ControlType(enum.Enum):
    reveal = "reveal"
    unvote = "unvote"


class SelectType(enum.Enum):
    unit = "unit"


class UnitSelect(enum.Enum):
    sp = UnitSelectOption("Storypoints", "sp", "🌟")
    tomato = UnitSelectOption("Помидорки", "🍅", "🍅")
    hours = UnitSelectOption("Часы", "ч.", "🕐")
    graphql = UnitSelectOption(
        "GraphQL",
        "<:graphql:811165209409880104>",
        CustomPartialEmoji(name="graphql", id=811165209409880104),
    )
    gmv = UnitSelectOption("Млн/месяц прироста GMV", "млн/месяц прироста GMV", "💸")
