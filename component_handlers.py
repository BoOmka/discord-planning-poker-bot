from dataclasses import dataclass

import discord_slash

import config
import handlers
from enums import (
    ComponentType,
    ControlType,
)
from storage import get_message_storage_or_none


@dataclass
class Button:
    interaction_id: int


@dataclass
class VariantButton(Button):
    value: str


@dataclass
class ControlButton(Button):
    control_type: ControlType


def parse_custom_id(custom_id: str) -> Button:
    _, interaction_id_raw, component_type_raw, value_raw = custom_id.split("_", 3)
    component_type = ComponentType[component_type_raw]
    interaction_id = int(interaction_id_raw)
    if component_type == ComponentType.variant:
        return VariantButton(interaction_id=interaction_id, value=value_raw)
    elif component_type == ComponentType.control:
        return ControlButton(interaction_id=interaction_id, control_type=ControlType[value_raw])


async def handle_component(ctx: discord_slash.ComponentContext) -> None:
    await ctx.defer(edit_origin=True)
    if not ctx.custom_id.startswith(f"{config.COMPONENT_PREFIX}_"):
        return

    button = parse_custom_id(ctx.custom_id)
    message_storage = get_message_storage_or_none(ctx.guild, ctx.channel, button.interaction_id)
    if isinstance(button, ControlButton):
        if button.control_type == ControlType.reveal:
            await handlers.reveal(message_storage)
        elif button.control_type == ControlType.unvote:
            await handlers.withdraw(message_storage, author=ctx.author)
    elif isinstance(button, VariantButton):
        await handlers.vote(message_storage, user=ctx.author, value=button.value)
    # await ctx.send(content="Vote accepted", hidden=True)
