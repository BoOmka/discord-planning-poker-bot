import typing

import discord

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
SPACER_EMOJIS: typing.List[str] = ["▪"]
REVEAL_EMOJI: str = "🏁"
DISCORD_FONT = "fonts/Whitney-Medium.ttf"

ACK_NORMAL_DELETE_AFTER_SECONDS = 15
ACK_EAT_DELETE_AFTER_SECONDS = 0
