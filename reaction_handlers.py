import discord

import config
import handlers
import storage


async def handle_reaction(reaction: discord.Reaction, user: discord.User) -> None:
    channel_storage = storage.get_channel_storage_or_none(reaction.message.guild, reaction.message.channel)
    if not channel_storage:
        return
    if reaction.message.id == channel_storage.message.id:
        if str(reaction.emoji) in config.ALLOWED_VOTE_EMOJIS:
            value = config.ALLOWED_VOTE_EMOJIS[str(reaction.emoji)]
            await handlers.vote(channel_storage, user, value)
            await reaction.remove(user)
        if str(reaction.emoji) == config.REVEAL_EMOJI:
            revealed = await handlers.reveal(channel_storage)
            if revealed:
                await reaction.clear()
                for r in reaction.message.reactions:
                    if str(r.emoji) in config.SPACER_EMOJIS:
                        await r.clear()
            else:
                await reaction.remove(user)
