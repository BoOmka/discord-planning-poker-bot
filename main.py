import os

import discord.ext
import discord_slash

import config
import handlers

intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot, auto_register=True)

start_options = [
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'comment',
        'description': 'Optional comment for your Vote',
        'required': False,
    }
]
vote_options = [
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'value',
        'description': 'Your vote',
        'required': True,
        'choices': [{'name': f'{x}', 'value': f'{x}'} for x in config.VOTE_CHOICES]
    }
]


# Order matters!

@slash.slash(name='ppvote', description='Shortcut for /poker vote', options=vote_options)
async def ppvote(ctx: discord_slash.SlashContext, value: str):
    return await handlers.vote(ctx=ctx, value=value)


@slash.subcommand(
    base='poker',
    name='vote',
    description='Cast a new vote or update existing for current voting',
    options=vote_options,
)
async def vote(ctx: discord_slash.SlashContext, value: str):
    return await handlers.vote(ctx=ctx, value=value)


@slash.subcommand(base='poker', name='withdraw', description='Withdraw your vote')
async def withdraw(ctx: discord_slash.SlashContext):
    await ctx.send(content='./withdraw stub', complete_hidden=True)


@slash.subcommand(base='poker', name='reveal', description="Reveal everyone's vote")
async def reveal(ctx: discord_slash.SlashContext):
    return await handlers.reveal(ctx=ctx)


@slash.subcommand(base='poker', name='start', description='(Re)Start a new vote in this channel', options=start_options)
async def start(ctx: discord_slash.SlashContext, comment: str = None):
    return await handlers.start(ctx=ctx, comment=comment)


def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise ValueError('Must provide DISCORD_TOKEN env')
    bot.run(token)


if __name__ == '__main__':
    main()
