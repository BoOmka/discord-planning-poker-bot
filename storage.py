import dataclasses
import typing

import discord


@dataclasses.dataclass
class Vote:
    author: discord.User
    value: str


@dataclasses.dataclass
class ChannelVoteStorage:
    channel: discord.TextChannel
    author: discord.User
    comment: typing.Optional[str]
    votes: typing.Dict[discord.User, Vote] = dataclasses.field(default_factory=dict)
    message: typing.Optional[discord.Message] = None


@dataclasses.dataclass
class GuildVoteStorage:
    guild: discord.Guild
    channel_storages: typing.Dict[discord.TextChannel, ChannelVoteStorage] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class VoteStorage:
    guild_storages: typing.Dict[discord.TextChannel, GuildVoteStorage] = dataclasses.field(default_factory=dict)
