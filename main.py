import os
import typing

import discord.ext
import discord_slash
from discord_slash.utils.manage_commands import (
    create_choice,
    create_option,
)

import component_handlers
import config
import handlers
from models import CustomPartialEmoji

intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot, sync_commands=True)

VOTE_START_COMMENT_OPTION = create_option(
    name="comment",
    description="Optional comment for your Vote",
    option_type=discord_slash.SlashCommandOptionType.STRING,
    required=False,
)
VOTE_START_MY_VOTE_OPTION = create_option(
    name="my_vote",
    description="Answer your vote right away",
    option_type=discord_slash.SlashCommandOptionType.STRING,
    required=False,
    choices=[create_choice(str(x), str(x)) for x in config.VOTE_VALUES],
)
VOTE_START_BINARY_FIRST_VALUE_OPTION = create_option(
    name="first_value",
    description='First option value (default: "Yes")',
    option_type=discord_slash.SlashCommandOptionType.STRING,
    required=False,
)
VOTE_START_BINARY_SECOND_VALUE_OPTION = create_option(
    name="second_value",
    description='First option value (default: "No")',
    option_type=discord_slash.SlashCommandOptionType.STRING,
    required=False,
)


# Order matters!
@slash.subcommand(
    base="poker",
    subcommand_group="start",
    name="fibonacci",
    description="Start a new vote with fibonacci-like options in this channel",
    options=[
        VOTE_START_COMMENT_OPTION,
        VOTE_START_MY_VOTE_OPTION,
    ],
)
async def start(ctx: discord_slash.SlashContext, comment: str = None, my_vote: str = None):
    return await handlers.start(ctx=ctx, valid_values=config.VOTE_VALUES, comment=comment, my_vote=my_vote)


def _convert_option_to_emoji(option: str) -> typing.Union[CustomPartialEmoji, str]:
    if option.startswith("<") and option.endswith(">"):
        try:
            name, emoji_id = option.strip("<:>").rsplit(':', 1)
        except:
            return option
        return CustomPartialEmoji(id=emoji_id, name=name)
    return option


@slash.subcommand(
    base="poker",
    subcommand_group="start",
    name="binary",
    description="Start a new binary vote in this channel",
    options=[
        VOTE_START_COMMENT_OPTION,
        VOTE_START_BINARY_FIRST_VALUE_OPTION,
        VOTE_START_BINARY_SECOND_VALUE_OPTION,
        VOTE_START_MY_VOTE_OPTION,
    ],
)
async def start_binary(
        ctx: discord_slash.SlashContext,
        comment: str = None,
        first_value: str = "Yes",
        second_value: str = "No",
        my_vote: str = None,
):
    first_value = _convert_option_to_emoji(first_value)
    second_value = _convert_option_to_emoji(second_value)
    return await handlers.start(
        ctx=ctx,
        valid_values={first_value: 1.0, second_value: 0.0},
        comment=comment,
        my_vote=my_vote,
    )


@slash.subcommand(
    base='poker', name='bump', description='Re-send vote message (in case it went far away due to other messages)'
)
async def bump(ctx: discord_slash.SlashContext):
    return await handlers.bump(ctx=ctx)


@bot.event
async def on_component(ctx: discord_slash.ComponentContext) -> None:
    await component_handlers.handle_component(ctx)


def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise ValueError('Must provide DISCORD_TOKEN env')
    bot.run(token)


if __name__ == '__main__':
    main()
