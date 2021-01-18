import typing

import discord
import discord_slash

import storage

storage_singleton = storage.VoteStorage()


def _vote_msg(author: discord.User, votes: typing.Dict[discord.User, storage.Vote], comment: str = None) -> str:
    vote_count = len(votes)
    voter_names = ", ".join(voter.mention for voter in votes.keys())
    voter_names_str = f' ({voter_names})' if voter_names else ""
    return (
        f'Vote by {author.mention}: {comment if comment else ""}\n'
        f'\n'
        f'Votes: `{vote_count}`{voter_names_str}'
    )


async def start(ctx: discord_slash.SlashContext, comment: str = None) -> None:
    guild_storage = storage_singleton.guild_storages.setdefault(ctx.guild, storage.GuildVoteStorage(guild=ctx.guild))
    channel_storage = guild_storage.channel_storages[ctx.channel] = storage.ChannelVoteStorage(
        channel=ctx.channel, author=ctx.author, comment=comment,
    )
    await ctx.send(content='Vote started', hidden=True)
    channel_storage.message = await ctx.channel.send(
        _vote_msg(ctx.author, {}, comment),
        allowed_mentions=discord.AllowedMentions(users=False),
    )
    await channel_storage.message.edit(suppress=True)


async def vote(ctx: discord_slash.SlashContext, value: str) -> None:
    try:
        channel_storage = storage_singleton.guild_storages[ctx.guild].channel_storages[ctx.channel]
    except KeyError:
        await ctx.send(
            content="There's no active vote in this channel. You can start one by typing `/poker start`",
            complete_hidden=True
        )
        return

    await ctx.send(content='Your vote is accepted!', complete_hidden=True)

    channel_storage.votes.setdefault(ctx.author, storage.Vote(author=ctx.author, value=value))
    await channel_storage.message.edit(
        content=_vote_msg(author=channel_storage.author, votes=channel_storage.votes, comment=channel_storage.comment),
        allowed_mentions=discord.AllowedMentions(users=False)
    )


async def reveal(ctx: discord_slash.SlashContext) -> None:
    try:
        channel_storage = storage_singleton.guild_storages[ctx.guild].channel_storages[ctx.channel]
    except KeyError:
        await ctx.send(
            content="There's no active vote in this channel. You can start one by typing `/poker start`",
            complete_hidden=True
        )
        return

    vote_values = ' '.join(v.value for v in channel_storage.votes.values())
    vote_name_clarification = f' for vote "{channel_storage.comment}"' if channel_storage.comment else ''
    answers_per_user = f'\n'.join(f'{author.mention}: {vote.value}' for author, vote in channel_storage.votes.items())
    await ctx.send(
        content=(
            f'Answers{vote_name_clarification} are revealed!\n'
            f'{vote_values}\n'
            f'||{answers_per_user}||'
        ),
        allowed_mentions=discord.AllowedMentions(users=False)
    )
