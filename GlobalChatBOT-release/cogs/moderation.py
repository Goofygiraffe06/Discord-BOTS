import discord
from discord.ext import commands
from discord import app_commands
import os
import json

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

    @app_commands.command(name="mute")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, interaction: discord.Interaction, username: str):
        guild = interaction.guild
        muted_usernames = load_muted_users(guild.id)
        if username not in muted_usernames:
            muted_usernames.append(username)
            save_muted_users(guild.id, muted_usernames)
            await interaction.response.send_message(f"User `{username}` has been muted in this server.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{username}` is already muted in this server.", ephemeral=True)

    @app_commands.command(name="unmute")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, username: str):
        guild = interaction.guild
        muted_usernames = load_muted_users(guild.id)
        if username in muted_usernames:
            muted_usernames.remove(username)
            save_muted_users(guild.id, muted_usernames)
            await interaction.response.send_message(f"User `{username}` has been unmuted in this server.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{username}` is not muted in this server.", ephemeral=True)

    @app_commands.command(name="mutelist")
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

