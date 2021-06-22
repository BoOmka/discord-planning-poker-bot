import typing

import discord

VOTE_VALUES: typing.Dict[typing.Union[str, discord.PartialEmoji], float] = {
    "0": 0,
    "½": 0.5,
    "1": 1,
    "2": 2,
    "3": 3,
    "5": 5,
    "8": 8,
    "13": 13,
    "21": 21,
    discord.PartialEmoji(name="graphql", id=811165209409880104): 100,
}
VOTE_VALUES_REDUCED: typing.Dict[str, float] = {
    (k.name if isinstance(k, discord.PartialEmoji) else k): v
    for k, v in VOTE_VALUES.items()
}

DISCORD_FONT = "fonts/Whitney-Medium.ttf"
DISCORD_MAX_BUTTONS_IN_ROW = 5

ACK_NORMAL_DELETE_AFTER_SECONDS = 15
ACK_EAT_DELETE_AFTER_SECONDS = 0

COMPONENT_PREFIX = "pp"
