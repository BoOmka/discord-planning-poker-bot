import os

import discord.ext
import discord_slash

import config
import handlers
import reaction_handlers

intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot, sync_commands=True)

start_options = [
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'comment',
        'description': 'Optional comment for your Vote',
        'required': False,
    },
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'my_vote',
        'description': 'Answer your vote right away',
        'required': False,
        'choices': [{'name': f'{x}', 'value': f'{x}'} for x in config.ALLOWED_VOTE_EMOJIS.values()]
    }
]
vote_options = [
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'value',
        'description': 'Your vote',
        'required': True,
        'choices': [{'name': f'{x}', 'value': f'{x}'} for x in config.ALLOWED_VOTE_EMOJIS.values()]
    }
]


# Order matters!

@slash.slash(name='ppvote', description='Shortcut for /poker vote', options=vote_options)
async def ppvote(ctx: discord_slash.SlashContext, value: str):
    return await handlers.vote_ctx(ctx=ctx, value=value)


@slash.subcommand(
    base='poker',
    name='vote',
    description='Cast a new vote or update existing for current voting',
    options=vote_options,
)
async def vote(ctx: discord_slash.SlashContext, value: str):
    return await handlers.vote_ctx(ctx=ctx, value=value)


@slash.subcommand(base='poker', name='withdraw', description='Withdraw your vote')
async def withdraw(ctx: discord_slash.SlashContext):
    return await handlers.withdraw(ctx=ctx)


@slash.subcommand(base='poker', name='reveal', description="Reveal everyone's vote")
async def reveal(ctx: discord_slash.SlashContext):
    return await handlers.reveal_ctx(ctx=ctx)


@slash.subcommand(base='poker', name='start', description='(Re)Start a new vote in this channel', options=start_options)
async def start(ctx: discord_slash.SlashContext, comment: str = None, my_vote: str = None):
    return await handlers.start(ctx=ctx, comment=comment, my_vote=my_vote)


@slash.subcommand(
    base='poker', name='bump', description='Re-send vote message (in case it went far away due to other messages)'
)
async def bump(ctx: discord_slash.SlashContext):
    return await handlers.bump(ctx=ctx)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if not user.bot:
        return await reaction_handlers.handle_reaction(reaction, user)


def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise ValueError('Must provide DISCORD_TOKEN env')
    bot.run(token)


if __name__ == '__main__':
    main()
