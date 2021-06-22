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

ALLOWED_VOTE_EMOJIS: typing.Dict[typing.Union[str, discord.Emoji], str] = {
    "0️⃣": "0",
    "<:half:837685500612444201>": "0.5",
    "1️⃣": "1",
    "2️⃣": "2",
    "3️⃣": "3",
    "5️⃣": "5",
    "8️⃣": "8",
    "<:thirteen:837685478605586442>": "13",
    "<:twentyone:852888122000932876>": "21",
    "<:graphql:811165209409880104>": ":graphql:",
    "<:this_is_the_way:819929485746634772>": ":this_is_the_way:",
}
CUSTOM_VOTE_VALUES: typing.Dict[str, float] = {
    ":graphql:": 100.0,
    ":this_is_the_way:": 0.0,
}
SPACER_EMOJIS: typing.List[str] = ["▪"]
DISCORD_FONT = "fonts/Whitney-Medium.ttf"
DISCORD_MAX_BUTTONS_IN_ROW = 5

ACK_NORMAL_DELETE_AFTER_SECONDS = 15
ACK_EAT_DELETE_AFTER_SECONDS = 0

COMPONENT_PREFIX = "pp"