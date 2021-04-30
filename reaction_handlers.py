import discord

import config
import handlers
import storage


async def handle_reaction(reaction: discord.Reaction, user: discord.User):
    channel_storage = storage.get_channel_storage_or_none(reaction.message.guild, reaction.message.channel)
    if reaction.message.id == channel_storage.message.id:
        if reaction.emoji in config.ALLOWED_VOTE_EMOJIS:
            value = config.ALLOWED_VOTE_EMOJIS[reaction.emoji]
            await handlers.vote(channel_storage, user, value)
            await reaction.remove(user)
        if reaction.emoji == config.REVEAL_EMOJI:
            await handlers.reveal(channel_storage)
            await reaction.clear()
