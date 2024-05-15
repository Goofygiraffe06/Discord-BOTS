import logging 
import discord
from discord.ext import commands

class onReady(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"We have logged in as {self.bot.user}")
        try:
            synced = await self.bot.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)...")
        except Exception as e:
            logging.error(f"Error syncing commands!: {e}")