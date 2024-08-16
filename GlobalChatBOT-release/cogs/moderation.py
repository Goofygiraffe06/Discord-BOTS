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

        current_lower = current.lower()
        muted_user_ids = set(load_muted_users(interaction.guild.id))  # Load muted users

        # Filter members by name matching the current input, exclude bots and non-muted users
        choices = [
            app_commands.Choice(name=f"{member.name} ({member.id})", value=str(member.id))
            for member in interaction.guild.members
            if current_lower in member.name.lower() and not member.bot and member.id in muted_user_ids
        ]
        return choices

    @app_commands.command(name="mute", description="Mute a user in the server")
    @app_commands.describe(user="User to mute (by username or ID)")
    @app_commands.autocomplete(user=autocomplete_user)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mute(self, interaction: discord.Interaction, user: str):
        guild = interaction.guild
        try:
            user_id = int(user)  # Convert to integer
        except ValueError:
            await interaction.response.send_message("Invalid user ID.", ephemeral=True)
            return

        member = guild.get_member(user_id)
        if not member:
            await interaction.response.send_message("User not found in this server.", ephemeral=True)
            return

        muted_user_ids = load_muted_users(guild.id)
        if user_id not in muted_user_ids:
            muted_user_ids.append(user_id)
            save_muted_users(guild.id, muted_user_ids)
            await interaction.response.send_message(f"User `{member.name}` ({user_id}) has been muted.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{member.name}` ({user_id}) is already muted.", ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a user in the server")
    @app_commands.describe(user="User to unmute (by username or ID)")
    @app_commands.autocomplete(user=autocomplete_user)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, user: str):
        guild = interaction.guild
        try:
            user_id = int(user)  # Convert to integer
        except ValueError:
            await interaction.response.send_message("Invalid user ID.", ephemeral=True)
            return

        member = guild.get_member(user_id)
        if not member:
            await interaction.response.send_message("User not found in this server.", ephemeral=True)
            return

        muted_user_ids = load_muted_users(guild.id)
        if user_id in muted_user_ids:
            muted_user_ids.remove(user_id)
            save_muted_users(guild.id, muted_user_ids)
            await interaction.response.send_message(f"User `{member.name}` ({user_id}) has been unmuted.", ephemeral=True)
        else:
            await interaction.response.send_message(f"User `{member.name}` ({user_id}) is not muted.", ephemeral=True)

    @app_commands.command(name="mutelist", description="List all muted users in the server")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def mutelist(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        muted_user_ids = load_muted_users(guild_id)

        if muted_user_ids:
            muted_users_info = []
            for user_id in muted_user_ids:
                member = interaction.guild.get_member(user_id)
                if member:
                    muted_users_info.append(f"{member.name} [{user_id}]")
                else:
                    muted_users_info.append(f"Unknown User [{user_id}]")

            muted_users_string = "\n".join(muted_users_info)
            await interaction.response.send_message(f"Muted users in this server:\n{muted_users_string}", ephemeral=True)
        else:
            await interaction.response.send_message("No users are currently muted in this server.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
    await bot.tree.sync()  # Syncs the commands with Discord

