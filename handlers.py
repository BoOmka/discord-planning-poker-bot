import statistics
import typing

import discord
import discord_slash

import storage
from decorators import needs_active_vote
from storage import storage_singleton


def _vote_msg(channel_storage: storage.ChannelVoteStorage) -> str:
    vote_count = len(channel_storage.votes)
    if channel_storage.is_revealed:
        reveal_status = '[REVEALED] '
        if vote_count == 1:
            value = next(iter(channel_storage.votes.values())).value
            mean: float = _to_float(value)
            stdev: float = _to_float(value)
        else:
            float_values = [_to_float(v.value) for v in channel_storage.votes.values()]
            mean: float = statistics.mean(float_values)
            stdev: float = statistics.stdev(float_values)

        vote_values = ' '.join(v.value for v in channel_storage.votes.values())
        answers_per_user = (
            f'\n'.join(f'{author.mention}: {vote.value}' for author, vote in channel_storage.votes.items())
        )
        vote_details = (
            f'{vote_values} (Mean={mean:.2f}, SD={stdev:.2f})\n'
            f'||{answers_per_user}||'
        )
    else:
        reveal_status = ''
        voter_names = ', '.join(voter.mention for voter in channel_storage.votes.keys())
        vote_details = f' ({voter_names})' if voter_names else ''

    comment = channel_storage.comment if channel_storage.comment else ""

    return (
        f'{reveal_status}Vote by {channel_storage.author.mention}: {comment}\n'
        f'\n'
        f'Votes: `{vote_count}`\n'
        f'{vote_details}'
    )


def _to_float(value: str) -> float:
    return float(value)


async def start(ctx: discord_slash.SlashContext, comment: str = None, my_vote: str = None) -> None:
    guild_storage = storage_singleton.guild_storages.setdefault(ctx.guild, storage.GuildVoteStorage(guild=ctx.guild))
    channel_storage = guild_storage.channel_storages[ctx.channel] = storage.ChannelVoteStorage(
        channel=ctx.channel, author=ctx.author, comment=comment,
    )
    if my_vote is not None:
        channel_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=my_vote)
    channel_storage.message = await ctx.channel.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False),
    )
    await channel_storage.message.edit(suppress=True)


@needs_active_vote
async def vote(ctx: discord_slash.SlashContext, value: str) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    await ctx.send(content='Your vote is accepted!', complete_hidden=True)

    channel_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=value)
    await channel_storage.message.edit(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def reveal(ctx: discord_slash.SlashContext) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    if not channel_storage.votes:
        await ctx.send(
            content=(
                f'Cannot reveal votes if there are none! :crying_cat_face:'
            ),
            complete_hidden=True
        )
        return

    channel_storage.is_revealed = True
    await channel_storage.message.edit(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def withdraw(ctx: discord_slash.SlashContext) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    try:
        del channel_storage.votes[ctx.author]
    except KeyError:
        await ctx.send(content="You didn't vote yet.", complete_hidden=True)
        return

    await ctx.send(content='Your vote is withdrawn!', complete_hidden=True)
    await channel_storage.message.edit(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def bump(ctx: discord_slash.SlashContext) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    old_message = channel_storage.message
    channel_storage.message = await ctx.channel.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False),
    )
    await old_message.delete()
