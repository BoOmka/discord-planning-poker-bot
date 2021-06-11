import statistics
import typing as t

import discord
import discord_slash
from PIL import Image, ImageDraw, ImageFont

import config
import storage
from decorators import needs_active_vote
from storage import storage_singleton

FONT_SIZE = 30
SPACE = ' '
SPACE_WIDTH_PX = 15


def _get_string_length_px(string: str) -> int:
    im = Image.new("RGB", (3200, 400))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(config.DISCORD_FONT, size=FONT_SIZE)
    draw.text((0, 0), string, font=font)
    im = im.crop(im.getbbox())
    return im.width


def _px_to_spaces(width_px: int, space_width_px: int) -> int:
    return width_px // space_width_px


def _make_vote_line(
        author: discord.User,
        vote: storage.Vote,
        mention: bool = False,
        additional_spacing: int = 0,
) -> str:
    name = author.mention if mention else author.display_name
    spacer = SPACE * additional_spacing
    return f'{name}:{spacer}{SPACE}{vote.value}'


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

        vote_maxwidth = max(
            _get_string_length_px(_make_vote_line(author, vote))
            for author, vote in channel_storage.votes.items()
        )
        answers_per_user = []
        for author, vote in channel_storage.votes.items():
            maxwidth_diff_px = vote_maxwidth - _get_string_length_px(_make_vote_line(author, vote))
            spacing = _px_to_spaces(maxwidth_diff_px, SPACE_WIDTH_PX)
            answers_per_user.append(_make_vote_line(author, vote, mention=True, additional_spacing=spacing))
        answers_per_user_str = f'\n'.join(answers_per_user)
        vote_details = (
            f'{vote_values} (Mean={mean:.2f}, SD={stdev:.2f})\n'
            f'||{answers_per_user_str}||'
        )
    else:
        reveal_status = ''
        voter_names = ', '.join(voter.mention for voter in channel_storage.votes.keys())
        vote_details = f' ({voter_names})' if voter_names else ''

    comment = channel_storage.comment if channel_storage.comment else ""

    return (
        f'{reveal_status}Vote: {comment}\n'
        f'Click numbers to vote. Click {config.REVEAL_EMOJI} to reveal.\n'
        f'\n'
        f'Votes: `{vote_count}`\n'
        f'{vote_details}'
    )


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return config.CUSTOM_VOTE_VALUES.get(value, 100.0)


async def start(ctx: discord_slash.SlashContext, comment: str = None, my_vote: str = None) -> None:
    await ctx.defer()
    guild_storage = storage_singleton.guild_storages.setdefault(ctx.guild, storage.GuildVoteStorage(guild=ctx.guild))
    channel_storage = guild_storage.channel_storages[ctx.channel] = storage.ChannelVoteStorage(
        channel=ctx.channel, author=ctx.author, comment=comment,
    )
    if my_vote is not None:
        channel_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=my_vote)
    channel_storage.message = await ctx.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False),
    )

    await channel_storage.message.edit(suppress=True)
    await _add_vote_emojis(channel_storage)


async def _add_vote_emojis(channel_storage):
    for emoji in config.ALLOWED_VOTE_EMOJIS.keys():
        try:
            await channel_storage.message.add_reaction(emoji)
        except:
            pass
    for emoji in config.SPACER_EMOJIS:
        await channel_storage.message.add_reaction(emoji)
    await channel_storage.message.add_reaction(config.REVEAL_EMOJI)


@needs_active_vote
async def vote_ctx(ctx: discord_slash.SlashContext, value: str) -> None:
    await ctx.defer(hidden=True)
    await ctx.send(content='Your vote is accepted!', hidden=True)

    channel_storage = storage.get_channel_storage_or_none_by_ctx(ctx)

    try:
        await vote(channel_storage, ctx.author, value)
    except discord.errors.NotFound:
        await ctx.send(content='This vote has ended!', hidden=True)


async def vote(channel_storage: storage.ChannelVoteStorage, user: discord.User, value: str) -> None:
    channel_storage.votes[user] = storage.Vote(author=user, value=value)
    await channel_storage.message.edit(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def reveal_ctx(ctx: discord_slash.SlashContext) -> None:
    channel_storage = storage.get_channel_storage_or_none_by_ctx(ctx)

    if not channel_storage.votes:
        await ctx.send(
            content=(
                f'Cannot reveal votes if there are none! :crying_cat_face:'
            ),
            hidden=True
        )
        return
    on_404_coro = ctx.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )
    await reveal(channel_storage, on_404_coro)
    await ctx.send(content='Vote revealed!', hidden=True)


async def reveal(channel_storage: storage.ChannelVoteStorage, on_404_coro: t.Optional[t.Coroutine] = None) -> bool:
    channel_storage.is_revealed = True
    try:
        await channel_storage.message.edit(
            content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
        )
        await channel_storage.message.clear_reaction(config.REVEAL_EMOJI)
        for emoji in config.SPACER_EMOJIS:
            await channel_storage.message.clear_reaction(emoji)
        return True
    except discord.errors.NotFound:
        try:
            await channel_storage.message.delete()
        except discord.errors.NotFound:
            return True
        if on_404_coro:
            channel_storage.message = await on_404_coro
    except statistics.StatisticsError:
        return False


@needs_active_vote
async def withdraw(ctx: discord_slash.SlashContext) -> None:
    await ctx.defer(hidden=True)
    channel_storage = storage.get_channel_storage_or_none_by_ctx(ctx)

    try:
        del channel_storage.votes[ctx.author]
    except KeyError:
        await ctx.send(content="You didn't vote yet.", hidden=True)
        return

    await ctx.send(content='Your vote is withdrawn!', hidden=True)
    await channel_storage.message.edit(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )


@needs_active_vote
async def bump(ctx: discord_slash.SlashContext) -> None:
    await ctx.defer()
    channel_storage = storage.get_channel_storage_or_none_by_ctx(ctx)

    old_message = channel_storage.message
    channel_storage.message = await ctx.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False),
    )
    try:
        await old_message.delete()
    except discord.errors.NotFound:
        pass
    await _add_vote_emojis(channel_storage)
