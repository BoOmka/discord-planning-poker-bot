import typing

import discord

from app.models import CustomPartialEmoji


FIBONACCI_VALUES: typing.Dict[typing.Union[str, discord.PartialEmoji], float] = {
    "0": 0,
    "½": 0.5,
    "1": 1,
    "2": 2,
    "3": 3,
    "5": 5,
    "8": 8,
    "13": 13,
    "21": 21,
    CustomPartialEmoji(name="graphql", id=811165209409880104): 100,
}

PERCENT_VALUES: typing.Dict[str, float] = {
    "0%": 0,
    "10%": 10,
    "20%": 20,
    "30%": 30,
    "40%": 40,
    "50%": 50,
    "60%": 60,
    "70%": 70,
    "80%": 80,
    "90%": 90,
    "100%": 100,
}


DISCORD_FONT = "fonts/Whitney-Medium.ttf"
DISCORD_MAX_BUTTONS_IN_ROW = 5

ACK_NORMAL_DELETE_AFTER_SECONDS = 15
ACK_EAT_DELETE_AFTER_SECONDS = 0

COMPONENT_PREFIX = "pp"
