from dataclasses import dataclass

import discord_slash

import config
import handlers
from enums import (
    ComponentType,
    ControlType,
    SelectType,
    UnitSelect,
)
from storage import get_message_storage_or_none


@dataclass
class Control:
    interaction_id: int


@dataclass
class VariantButton(Control):
    value: str


@dataclass
class ControlButton(Control):
    control_type: ControlType


@dataclass
class Select(Control):
    select_type: SelectType


def parse_custom_id(custom_id: str) -> Control:
    _, interaction_id_raw, component_type_raw, value_raw = custom_id.split("_", 3)
    component_type = ComponentType[component_type_raw]
    interaction_id = int(interaction_id_raw)
    if component_type == ComponentType.variant:
        return VariantButton(interaction_id=interaction_id, value=value_raw)
    elif component_type == ComponentType.control:
        return ControlButton(interaction_id=interaction_id, control_type=ControlType[value_raw])
    elif component_type == ComponentType.select:
        return Select(interaction_id=interaction_id, select_type=SelectType[value_raw])


async def handle_component(ctx: discord_slash.ComponentContext) -> None:
    await ctx.defer(edit_origin=True)
    if not ctx.custom_id.startswith(f"{config.COMPONENT_PREFIX}_"):
        return

    control = parse_custom_id(ctx.custom_id)
    message_storage = get_message_storage_or_none(ctx.guild, ctx.channel, control.interaction_id)
    unit = UnitSelect[ctx.selected_options[0]].value.unit if ctx.selected_options else ""
    if isinstance(control, ControlButton):
        if control.control_type == ControlType.reveal:
            await handlers.reveal(message_storage)
        elif control.control_type == ControlType.unvote:
            await handlers.withdraw(message_storage, author=ctx.author)
    elif isinstance(control, VariantButton):
        await handlers.vote(message_storage, user=ctx.author, unit=unit, value=control.value)
    elif isinstance(control, Select):
        await handlers.vote(message_storage, user=ctx.author, unit=unit)
    # await ctx.send(content="Vote accepted", hidden=True)
