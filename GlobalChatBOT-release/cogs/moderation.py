import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from typing import List

MUTE_DIR = 'mutes'

def load_muted_users(guild_id):
    file_path = os.path.join(MUTE_DIR, f'{guild_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_muted_users(guild_id, data):
    file_path = os.path.join(MUTE_DIR, f'{guild_id}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_user(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        if not interaction.guild:
            return []

        choices = [
            app_commands.Choice(name=user.name, value=user.name)
            for user in interaction.guild.members
            if current.lower() in user.name.lower() and not user.bot
        ]
        return choices

    async def get_member_by_username(self, guild: discord.Guild, username: str) -> discord.Member:
        for member in guild.members:
            if member.name.lower() == username.lower() and not member.bot:
                return member
        return None

    @app_commands.command(name="mute", description="Mute a user in the server")
    @app_commands.describe(username="Name of the user to mute")
    @app_commands.autocomplete(username=autocomplete_user)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, interaction: discord.Interaction, username: str):
        guild = interaction.guild
        member = await self.get_member_by_username(guild, username)

        if member is None:
            await interaction.response.send_message(f"User `{username}` does not exist in this server.", ephemeral=True)
            return

        muted_usernames = load_muted_users(guild.id)
        if username not in muted_usernames:
            muted_usernames.append(username)
            save_muted_users(guild.id, muted_usernames)
            await interaction.response.send_message(f"User `{username}` has been muted in this server.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{username}` is already muted in this server.", ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a user in the server")
    @app_commands.describe(username="Name of the user to unmute")
    @app_commands.autocomplete(username=autocomplete_user)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, username: str):
        guild = interaction.guild
        member = await self.get_member_by_username(guild, username)

        if member is None:
            await interaction.response.send_message(f"User `{username}` does not exist in this server.", ephemeral=True)
            return

        muted_usernames = load_muted_users(guild.id)
        if username in muted_usernames:
            muted_usernames.remove(username)
            save_muted_users(guild.id, muted_usernames)
            await interaction.response.send_message(f"User `{username}` has been unmuted in this server.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{username}` is not muted in this server.", ephemeral=True)

    @app_commands.command(name="mutelist", description="List all muted users in the server")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mutelist(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        muted_usernames = load_muted_users(guild_id)

        if muted_usernames:
            muted_users_string = "\n".join(muted_usernames)
            await interaction.response.send_message(f"Muted users in this server:\n{muted_users_string}", ephemeral=True)
        else:
            await interaction.response.send_message("No users are currently muted in this server.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
    await bot.tree.sync()  # Syncs the commands with Discord

