import typing

import discord

VOTE_CHOICES = [0, 0.5, 1, 2, 3, 5, 8, 13, ":graphql:"]
ALLOWED_VOTE_EMOJIS: typing.Dict[typing.Union[str, discord.Emoji], str] = {
    "0️⃣": "0",
    "1️⃣": "1",
    "2️⃣": "2",
    "3️⃣": "3",
    "5️⃣": "5",
    "8️⃣": "8",
    # "graphql": ":graphql:",
}
REVEAL_EMOJI: str = "🏁"
DISCORD_FONT = "fonts/Whitney-Medium.ttf"

ACK_NORMAL_DELETE_AFTER_SECONDS = 15
ACK_EAT_DELETE_AFTER_SECONDS = 0
