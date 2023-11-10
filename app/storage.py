import dataclasses
import typing

import discord
import discord_slash


@dataclasses.dataclass
class Vote:
    author: discord.User
    value: str
    unit: str


@dataclasses.dataclass
class MessageVoteStorage:
    channel: typing.Optional[discord.TextChannel]
    author: discord.User
    comment: typing.Optional[str]
    interaction_id: int
    valid_values: typing.Dict[str, float]
    votes: typing.Dict[discord.User, Vote] = dataclasses.field(default_factory=dict)
    message: typing.Optional[discord.Message] = None
    is_revealed: bool = False

    @property
    def valid_votes(self) -> typing.Dict[discord.User, Vote]:
        return {k: v for k, v in self.votes.items() if v.value}


@dataclasses.dataclass
class ChannelVoteStorage:
    channel: typing.Optional[discord.TextChannel]
    message_storages: typing.Dict[int, MessageVoteStorage] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class GuildVoteStorage:
    guild: discord.Guild
    channel_storages: typing.Dict[discord.TextChannel, ChannelVoteStorage] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class VoteStorage:
    guild_storages: typing.Dict[discord.TextChannel, GuildVoteStorage] = dataclasses.field(default_factory=dict)


storage_singleton = VoteStorage()


def get_message_storage_or_none_by_ctx(ctx: discord_slash.SlashContext) -> typing.Optional[MessageVoteStorage]:
    return get_last_message_storage_or_none(ctx.guild, ctx.channel)


def _get_channel_storage(
        guild: discord.Guild,
        channel: discord.TextChannel,
) -> ChannelVoteStorage:
    return storage_singleton.guild_storages[guild].channel_storages[channel]


def get_last_message_storage_or_none(
        guild: discord.Guild,
        channel: discord.TextChannel,
) -> typing.Optional[MessageVoteStorage]:
    channel_storage = _get_channel_storage(guild, channel)
    try:
        return list(channel_storage.message_storages.values())[-1]
    except KeyError:
        return None


def get_message_storage_or_none(
        guild: discord.Guild,
        channel: discord.TextChannel,
        interaction_id: int,
) -> typing.Optional[MessageVoteStorage]:
    channel_storage = _get_channel_storage(guild, channel)
    return channel_storage.message_storages.get(interaction_id, None)
