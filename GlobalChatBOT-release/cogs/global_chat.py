import discord
from discord.ext import commands
import re
import os

GLOBAL_CHAT_IDENTIFIER = 'aa8af3ebe14831a7cd1b6d1383a03755'

class GlobalChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.global_chat_channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_global_chat_channels()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_global_chat_channels()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.global_chat_channels = {k: v for k, v in self.global_chat_channels.items() if v.guild.id != guild.id}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.global_chat_channels:
            username_match = re.match(r"Username:\s*`(\w+)`", message.content)
            if username_match:
                username = username_match.group(1)
            else:
                username = message.author.name

            for channel_id, channel in self.global_chat_channels.items():
                if channel_id != message.channel.id:
                    try:
                        await channel.send(f"-# Username: `{username}` \n{message.content}")
                    except Exception as e:
                        print(f"Failed to send message to channel {channel.name} in guild {channel.guild.name}: {e}")

    async def update_global_chat_channels(self):
        self.global_chat_channels = {}
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.topic and GLOBAL_CHAT_IDENTIFIER in channel.topic:
                    self.global_chat_channels[channel.id] = channel
                    print(f"Found global-chat channel: {channel.name} in guild: {guild.name}")

async def setup(bot):
    await bot.add_cog(GlobalChat(bot))

