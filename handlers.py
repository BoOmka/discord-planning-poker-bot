import statistics

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
        f'\n'
        f'Votes: `{vote_count}`\n'
        f'{vote_details}'
    )


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 100.0


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


@needs_active_vote
async def vote(ctx: discord_slash.SlashContext, value: str) -> None:
    await ctx.defer(hidden=True)
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    await ctx.send(content='Your vote is accepted!', hidden=True)

    channel_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=value)
    try:
        await channel_storage.message.edit(
            content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
        )
    except discord.errors.NotFound:
        await ctx.send(content='This vote has ended!', hidden=True)


@needs_active_vote
async def reveal(ctx: discord_slash.SlashContext) -> None:
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    if not channel_storage.votes:
        await ctx.send(
            content=(
                f'Cannot reveal votes if there are none! :crying_cat_face:'
            ),
            hidden=True,
            delete_after=config.ACK_NORMAL_DELETE_AFTER_SECONDS
        )
        return

    channel_storage.is_revealed = True
    try:
        await channel_storage.message.edit(
            content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
        )
    except discord.errors.NotFound:
        try:
            await channel_storage.message.delete()
        except discord.errors.NotFound:
            pass
        channel_storage.message = await ctx.send(
            content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False)
        )
    await ctx.send(content='Vote revealed!', hidden=True)


@needs_active_vote
async def withdraw(ctx: discord_slash.SlashContext) -> None:
    await ctx.defer(hidden=True)
    channel_storage = await storage.get_channel_storage_or_none(ctx)

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
    channel_storage = await storage.get_channel_storage_or_none(ctx)

    old_message = channel_storage.message
    channel_storage.message = await ctx.send(
        content=_vote_msg(channel_storage), allowed_mentions=discord.AllowedMentions(users=False),
    )
    try:
        await old_message.delete()
    except discord.errors.NotFound:
        pass
