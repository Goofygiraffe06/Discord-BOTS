import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_times = {}
        self.check_channels.start()
        self.prune_message_history.start()

    @tasks.loop(minutes=1)
    async def check_channels(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.topic and "aa8af3ebe14831a7cd1b6d1383a03755" in channel.topic:
                    if channel.id not in self.bot.get_cog('GlobalChat').global_chat_channels:
                        self.bot.get_cog('GlobalChat').global_chat_channels[channel.id] = channel
                        print(f"Added new global-chat channel: {channel.name} in guild: {guild.name}")

    @tasks.loop(minutes=10)
    async def prune_message_history(self):
        now = datetime.now(timezone.utc)
        prune_before = now - timedelta(minutes=20)
        for key in list(self.user_message_times.keys()):
            self.user_message_times[key] = [timestamp for timestamp in self.user_message_times[key] if timestamp > prune_before]

    @check_channels.before_loop
    @prune_message_history.before_loop
    async def before_pruning(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Tasks(bot))

