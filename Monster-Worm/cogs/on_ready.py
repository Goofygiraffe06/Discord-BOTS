import logging
import discord
from discord.ext import commands
from .db_utils import db_init

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"We have logged in as {self.bot.user}")
        try:
            synced = await self.bot.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)...")
            logging.info("Initializing Database...")
            db_init()
            logging.info(commands.Cog.get_listeners(self))
        except Exception as e:
            logging.error(f"Error syncing commands!: {e}")

async def setup(bot) -> None:
    await bot.add_cog(OnReady(bot))