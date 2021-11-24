import statistics
import typing as t

import discord
import discord_slash
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)
from discord import PartialEmoji
from discord_slash import ButtonStyle
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import spread_to_rows

import config
import config as c
import storage
from decorators import needs_active_vote
from enums import (
    ComponentType,
    ControlType,
    UnitSelect,
)
from storage import storage_singleton

FONT_SIZE = 30
SPACE = ' '
SPACE_WIDTH_PX = 15


def _get_string_length_px(string: str) -> int:
    im = Image.new("RGB", (3200, 400))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(c.DISCORD_FONT, size=FONT_SIZE)
    draw.text((0, 0), string, font=font)
    im = im.crop(im.getbbox())
    return im.width


def _px_to_spaces(width_px: int, space_width_px: int) -> int:
    return width_px // space_width_px


def _get_vote_value_or_emoji(vote_value: str) -> str:
    result = vote_value
    for key in config.VOTE_VALUES:
        if not isinstance(key, PartialEmoji):
            continue
        if vote_value == key:
            result = discord.PartialEmoji.__str__(key)
            break
    return result


def _make_vote_line(
        author: discord.User,
        vote: storage.Vote,
        mention: bool = False,
        additional_spacing: int = 0,
) -> str:
    name = author.mention if mention else author.display_name
    spacer = SPACE * additional_spacing

    value = _get_vote_value_or_emoji(vote.value)
    return f'{name}:{spacer}{SPACE}{value} {vote.unit or UnitSelect.sp.value.unit}'


def _vote_msg(message_storage: storage.MessageVoteStorage) -> str:
    vote_count = len(message_storage.valid_votes)
    if message_storage.is_revealed:
        reveal_status = '[REVEALED] '
        if vote_count == 1:
            value = next(iter(message_storage.votes.values())).value
            mean: float = _to_float(message_storage.valid_values, value)
            stdev: float = 0.0
        else:
            float_values = [
                _to_float(message_storage.valid_values, v.value)
                for v in message_storage.valid_votes.values()
            ]
            mean: float = statistics.mean(float_values)
            stdev: float = statistics.stdev(float_values)

        vote_values = ' '.join(_get_vote_value_or_emoji(v.value) for v in message_storage.valid_votes.values())

        vote_maxwidth = max(
            _get_string_length_px(_make_vote_line(author, vote))
            for author, vote in message_storage.valid_votes.items()
        )
        answers_per_user = []
        for author, vote in message_storage.valid_votes.items():
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
        voter_names = ', '.join(voter.mention for voter, vote in message_storage.votes.items() if vote.value)
        vote_details = f' ({voter_names})' if voter_names else ''

    comment = message_storage.comment if message_storage.comment else ""

    return (
        f'{reveal_status}Vote: {comment}\n'
        f'\n'
        f'Votes: `{vote_count}`\n'
        f'{vote_details}'
    )


def _to_float(valid_values: t.Dict[str, float], value: str) -> float:
    try:
        return float(valid_values[value])
    except ValueError:
        return 0.0


async def start(
        ctx: discord_slash.SlashContext,
        valid_values: t.Dict[str, float],
        comment: str = None,
        my_vote: str = None,
) -> None:
    await ctx.defer()
    guild_storage = storage_singleton.guild_storages.setdefault(ctx.guild, storage.GuildVoteStorage(guild=ctx.guild))
    channel_storage = guild_storage.channel_storages.setdefault(
        ctx.channel,
        storage.ChannelVoteStorage(channel=ctx.channel)
    )
    message_storage = channel_storage.message_storages[int(ctx.interaction_id)] = storage.MessageVoteStorage(
        channel=ctx.channel,
        author=ctx.author,
        comment=comment,
        interaction_id=int(ctx.interaction_id),
        valid_values=valid_values,
    )
    if my_vote is not None:
        message_storage.votes[ctx.author] = storage.Vote(author=ctx.author, value=my_vote)
    message_storage.message = await ctx.send(
        content=_vote_msg(message_storage),
        allowed_mentions=discord.AllowedMentions(users=False),
        components=_make_components(message_storage),
    )

    await message_storage.message.edit(suppress=True)


def _make_vote_button_rows(interaction_id: int, valid_values: t.Dict[str, float]) -> t.List[dict]:
    buttons = []
    for vote_var in valid_values.keys():
        if isinstance(vote_var, discord.PartialEmoji):
            button = manage_components.create_button(
                style=ButtonStyle.secondary,
                emoji=vote_var,
                custom_id=f"{c.COMPONENT_PREFIX}_{interaction_id}_{ComponentType.variant.value}_{vote_var.name}",
            )
        else:
            button = manage_components.create_button(
                style=ButtonStyle.secondary,
                label=vote_var,
                custom_id=f"{c.COMPONENT_PREFIX}_{interaction_id}_{ComponentType.variant.value}_{vote_var}",
            )
        buttons.append(button)
    return spread_to_rows(*buttons, max_in_row=c.DISCORD_MAX_BUTTONS_IN_ROW)


def _make_controls_row(interaction_id: int, reveal_disabled: bool = False) -> dict:
    buttons = [
        manage_components.create_button(
            style=ButtonStyle.success,
            label="Reveal",
            disabled=reveal_disabled,
            custom_id=f"{c.COMPONENT_PREFIX}_{interaction_id}_{ComponentType.control.value}_{ControlType.reveal.value}",
        ),
        manage_components.create_button(
            style=ButtonStyle.danger,
            label="Unvote",
            custom_id=f"{c.COMPONENT_PREFIX}_{interaction_id}_{ComponentType.control.value}_{ControlType.unvote.value}",
        )
    ]
    return manage_components.create_actionrow(*buttons)


def _make_unit_select_row(interaction_id: int) -> dict:
    return manage_components.create_actionrow(
        manage_components.create_select(
            [
                manage_components.create_select_option(option.value.name, value=option.name, emoji=option.value.emoji)
                for option in UnitSelect
            ],
            placeholder="Переключить единицы измерения",
            custom_id=f"{c.COMPONENT_PREFIX}_{interaction_id}_{ComponentType.select.value}_unit",
        )
    )


def _make_components(message_storage: storage.MessageVoteStorage) -> t.List[dict]:
    reveal_disabled = message_storage.is_revealed or not message_storage.valid_votes
    return (
            _make_vote_button_rows(message_storage.interaction_id, message_storage.valid_values)
            + [_make_unit_select_row(message_storage.interaction_id)]
            + [_make_controls_row(message_storage.interaction_id, reveal_disabled=reveal_disabled)]
    )


@needs_active_vote
async def vote_ctx(ctx: discord_slash.SlashContext, value: str) -> None:
    await ctx.defer(hidden=True)
    await ctx.send(content='Your vote is accepted!', hidden=True)

    message_storage = storage.get_message_storage_or_none_by_ctx(ctx)

    try:
        await vote(message_storage, ctx.author, value)
    except discord.errors.NotFound:
        await ctx.send(content='This vote has ended!', hidden=True)


async def vote(
        message_storage: storage.MessageVoteStorage,
        user: discord.User,
        unit: str,
        value: t.Optional[str] = None,
) -> None:
    if value:
        unit = unit or (message_storage.votes[user].unit if user in message_storage.votes else "")
        message_storage.votes[user] = storage.Vote(author=user, value=value, unit=unit)
    elif unit:
        value = value or (message_storage.votes[user].value if user in message_storage.votes else "")
        message_storage.votes[user] = storage.Vote(author=user, value=value, unit=unit)
    else:
        return
    await message_storage.message.edit(
        content=_vote_msg(message_storage),
        allowed_mentions=discord.AllowedMentions(users=False),
        components=_make_components(message_storage),
    )


@needs_active_vote
async def reveal_ctx(ctx: discord_slash.SlashContext) -> None:
    message_storage = storage.get_message_storage_or_none_by_ctx(ctx)

    if not message_storage.votes:
        await ctx.send(
            content=(
                f'Cannot reveal votes if there are none! :crying_cat_face:'
            ),
            hidden=True
        )
        return
    on_404_coro = ctx.send(
        content=_vote_msg(message_storage), allowed_mentions=discord.AllowedMentions(users=False)
    )
    await reveal(message_storage, on_404_coro)
    await ctx.send(content='Vote revealed!', hidden=True)


async def reveal(message_storage: storage.MessageVoteStorage, on_404_coro: t.Optional[t.Coroutine] = None) -> bool:
    if not message_storage.votes:
        return False
    message_storage.is_revealed = True
    try:
        await message_storage.message.edit(
            content=_vote_msg(message_storage),
            allowed_mentions=discord.AllowedMentions(users=False),
            components=_make_components(message_storage),
        )
        return True
    except discord.errors.NotFound:
        try:
            await message_storage.message.delete()
        except discord.errors.NotFound:
            return True
        if on_404_coro:
            message_storage.message = await on_404_coro
    except statistics.StatisticsError:
        return False


@needs_active_vote
async def withdraw_ctx(ctx: discord_slash.SlashContext) -> None:
    await ctx.defer(hidden=True)
    message_storage = storage.get_message_storage_or_none_by_ctx(ctx)

    await withdraw(
        message_storage,
        author=ctx.author,
        on_404_coro=ctx.send(content="You didn't vote yet.", hidden=True),
    )
    await ctx.send(content='Your vote is withdrawn!', hidden=True)


async def withdraw(
        message_storage: storage.MessageVoteStorage,
        author: discord.User,
        on_404_coro: t.Optional[t.Coroutine] = None,
) -> None:
    try:
        del message_storage.votes[author]
        if not message_storage.votes:
            message_storage.is_revealed = False
    except KeyError:
        if on_404_coro:
            await on_404_coro
        return
    await message_storage.message.edit(
        content=_vote_msg(message_storage),
        allowed_mentions=discord.AllowedMentions(users=False),
        components=_make_components(message_storage),
    )


@needs_active_vote
async def bump(ctx: discord_slash.SlashContext) -> None:
    await ctx.defer()
    message_storage = storage.get_message_storage_or_none_by_ctx(ctx)

    old_message = message_storage.message
    message_storage.message = await ctx.send(
        content=_vote_msg(message_storage),
        allowed_mentions=discord.AllowedMentions(users=False),
        components=_make_components(message_storage),
    )
    try:
        await old_message.delete()
    except discord.errors.NotFound:
        pass
