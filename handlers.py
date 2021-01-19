import statistics
import typing

import discord
import discord_slash

import storage
from decorators import needs_active_vote
from storage import storage_singleton


def _vote_msg(author: discord.User, votes: typing.Dict[discord.User, storage.Vote], comment: str = None) -> str:
    vote_count = len(votes)
    voter_names = ", ".join(voter.mention for voter in votes.keys())
    voter_names_str = f' ({voter_names})' if voter_names else ""
    return (
        f'Vote by {author.mention}: {comment if comment else ""}\n'
        f'\n'
        f'Votes: `{vote_count}`{voter_names_str}'
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
    await ctx.send(content='Vote started', hidden=True)
    channel_storage.message = await ctx.channel.send(
        _vote_msg(ctx.author, channel_storage.votes, comment),
        allowed_mentions=discord.AllowedMentions(users=False),
    )
    await channel_storage.message.edit(suppress=True)


@needs_active_vote
async def vote(ctx: discord_slash.SlashContext, value: str) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    await ctx.send(content='Your vote is accepted!', complete_hidden=True)

    channel_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=value)
    await channel_storage.message.edit(
        content=_vote_msg(author=channel_storage.author, votes=channel_storage.votes, comment=channel_storage.comment),
        allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def reveal(ctx: discord_slash.SlashContext) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    values_len = len(channel_storage.votes)
    if values_len == 0:
        await ctx.send(
            content=(
                f'Cannot reveal votes if there are none! :crying_cat_face:'
            ),
            complete_hidden=True
        )
        return
    elif values_len == 1:
        value = next(iter(channel_storage.votes.values())).value
        mean: float = _to_float(value)
        stdev: float = _to_float(value)
    else:
        float_values = [_to_float(v.value) for v in channel_storage.votes.values()]
        mean: float = statistics.mean(float_values)
        stdev: float = statistics.stdev(float_values)

    vote_values = ' '.join(v.value for v in channel_storage.votes.values())
    vote_name_clarification = f' for vote "{channel_storage.comment}"' if channel_storage.comment else ''
    answers_per_user = f'\n'.join(f'{author.mention}: {vote.value}' for author, vote in channel_storage.votes.items())

    await ctx.send(
        content=(
            f'Answers{vote_name_clarification} are revealed!\n'
            f'{vote_values} (Mean={mean:.2f}, SD={stdev:.2f})\n'
            f'||{answers_per_user}||'
        ),
        allowed_mentions=discord.AllowedMentions(users=False)
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
        content=_vote_msg(author=channel_storage.author, votes=channel_storage.votes, comment=channel_storage.comment),
        allowed_mentions=discord.AllowedMentions(users=False)
    )
