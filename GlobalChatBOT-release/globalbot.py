import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await load_cogs()

async def load_cogs():
    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_name = os.path.join(root, filename).replace('./', '').replace('/', '.').replace('\\', '.').rstrip('.py')
                try:
                    await bot.load_extension(cog_name)
                    print(f'Loaded {cog_name}')
                except Exception as e:
                    print(f'Failed to load cog {cog_name}: {e}')

if __name__ == '__main__':
    bot.run(TOKEN)

