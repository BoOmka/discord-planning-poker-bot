import os

import discord.ext
import discord_slash

intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot, auto_register=True)

VOTE_OPTIONS = [
    {
        'type': discord_slash.SlashCommandOptionType.STRING,
        'name': 'value',
        'description': 'Your vote',
        'required': True,
        'choices': [
            {'name': '0', 'value': '0'},
            {'name': '0.5', 'value': '0.5'},
            {'name': '1', 'value': '1'},
            {'name': '2', 'value': '2'},
            {'name': '3', 'value': '3'},
            {'name': '5', 'value': '5'},
            {'name': '8', 'value': '8'},
            {'name': '13', 'value': '13'},
        ]
    }
]


@slash.subcommand(base='poker', name='start', description='(Re)Start a new vote in this channel')
async def start(ctx: discord_slash.SlashContext):
    await ctx.send(content='./start stub', complete_hidden=True)


async def _vote(ctx: discord_slash.SlashContext, value: str):
    await ctx.send(content=f'./vote stub. value={value}', complete_hidden=True)


@slash.subcommand(
    base='poker',
    name='vote',
    description='Cast a new vote or update existing for current voting',
    options=VOTE_OPTIONS,
)
async def vote(ctx: discord_slash.SlashContext, value: str):
    await _vote(ctx=ctx, value=value)


@slash.slash(name='ppvote', description='Shortcut for /poker vote', options=VOTE_OPTIONS)
async def vote(ctx: discord_slash.SlashContext, value: str):
    await _vote(ctx=ctx, value=value)


@slash.subcommand(base='poker', name='reveal', description="Reveal everyone's vote")
async def reveal(ctx: discord_slash.SlashContext):
    await ctx.send(content='./reveal stub', complete_hidden=True)


def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise ValueError('Must provide DISCORD_TOKEN env')
    bot.run(token)


if __name__ == '__main__':
    main()
