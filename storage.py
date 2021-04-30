import dataclasses
import typing

import discord
import discord_slash


@dataclasses.dataclass
class Vote:
    author: discord.User
    value: str


@dataclasses.dataclass
class ChannelVoteStorage:
    channel: typing.Optional[discord.TextChannel]
    author: discord.User
    comment: typing.Optional[str]
    votes: typing.Dict[discord.User, Vote] = dataclasses.field(default_factory=dict)
    message: typing.Optional[discord.Message] = None
    is_revealed: bool = False


@dataclasses.dataclass
class GuildVoteStorage:
    guild: discord.Guild
    channel_storages: typing.Dict[discord.TextChannel, ChannelVoteStorage] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class VoteStorage:
    guild_storages: typing.Dict[discord.TextChannel, GuildVoteStorage] = dataclasses.field(default_factory=dict)


storage_singleton = VoteStorage()


def get_channel_storage_or_none_by_ctx(ctx: discord_slash.SlashContext) -> typing.Optional[ChannelVoteStorage]:
    return get_channel_storage_or_none(ctx.guild, ctx.channel)


def get_channel_storage_or_none(
        guild: discord.Guild,
        channel: discord.TextChannel,
) -> typing.Optional[ChannelVoteStorage]:
    try:
        channel_storage = storage_singleton.guild_storages[guild].channel_storages[channel]
    except KeyError:
        channel_storage = None
    return channel_storage
