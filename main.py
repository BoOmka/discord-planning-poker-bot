import os

import discord.ext
import discord_slash

intents = discord.Intents.all()
bot = discord.ext.commands.Bot(command_prefix="/", intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot)


def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise ValueError('Must provide DISCORD_TOKEN env')
    bot.run(token)


if __name__ == '__main__':
    main()
