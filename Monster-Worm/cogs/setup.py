import discord
from .db_utils import db_init, update_config
from discord.ext import commands
import logging
from discord.ext.commands import has_permissions, CheckFailure

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask.app").setLevel(logging.ERROR)


# Shared Configuration Object to hold our configuration
class Config:
    def __init__(self, con):
        self.con = con

    def get(self, key, default=None):
        config = fetch_config(self.con)
        if config:
            return config.get(key, default)
        else:
            return default

    def set(self, key, value):
        update_config(self.con, key, value)
        self.con.commit()

class OsintChannelSelect(discord.ui.Select):
    def __init__(self, channels, config):
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
            if isinstance(channel, discord.TextChannel)
        ]
        super().__init__(
            placeholder="Select the OSINT Bot channel...", options=options, row=0
        )
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        self.config.set("osint_bot_channel", int(self.values[0]))
        await interaction.response.send_message(
            f"Selected Channel: <#{self.values[0]}>", ephemeral=True
        )

class ActivityMusicChannelSelect(discord.ui.Select):
    def __init__(self, channels, config):
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
            if isinstance(channel, discord.TextChannel)
        ]
        super().__init__(
            placeholder="Select the Activity and Music Bot channel...", options=options, row=1
        )
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        self.config.set("activity_music_bot_channel", int(self.values[0]))
        await interaction.response.send_message(
            f"Selected Channel: <#{self.values[0]}>", ephemeral=True
        )

class LightshotChannelSelect(discord.ui.Select):
    def __init__(self, channels, config):
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
            if isinstance(channel, discord.TextChannel)
        ]
        super().__init__(
            placeholder="Select the Lightshot Bot channel...", options=options, row=2
        )
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        self.config.set("lightshot_bot_channel", int(self.values[0]))
        await interaction.response.send_message(
            f"Selected Channel: <#{self.values[0]}>", ephemeral=True
        )

class NmapChannelSelect(discord.ui.Select):
    def __init__(self, channels, config):
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
            if isinstance(channel, discord.TextChannel)
        ]
        super().__init__(
            placeholder="Select the Nmap Bot channel...", options=options, row=3
        )
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        self.config.set("nmap_bot_channel", int(self.values[0]))
        await interaction.response.send_message(
            f"Selected Channel: <#{self.values[0]}>", ephemeral=True
        )

class WhoStaredChannelSelect(discord.ui.Select):
    def __init__(self, channels, config):
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channels
            if isinstance(channel, discord.TextChannel)
        ]
        super().__init__(
            placeholder="Select the WhoStared Bot channel...", options=options, row=4
        )
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        self.config.set("whostared_bot_channel", int(self.values[0]))
        await interaction.response.send_message(
            f"Selected Channel: <#{self.values[0]}>", ephemeral=True
        )


class SetupView(discord.ui.View):
    def __init__(self, channels, config):
        super().__init__()
        self.add_item(OsintChannelSelect(channels, config))
        self.add_item(ActivityMusicChannelSelect(channels, config))
        self.add_item(LightshotChannelSelect(channels, config))
        self.add_item(NmapChannelSelect(channels, config))
        self.add_item(WhoStaredChannelSelect(channels, config))

class Setup(commands.Cog):
    def __init__(self, bot, con):
        self.bot = bot
        self.con = con
        self.config = Config(con)

    @discord.app_commands.command(
        name="setup", description="Configure bot settings for the server."
    )
    @has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction) -> None:
        try:    
            logging.info(
                f"Setup command invoked by {interaction.user.name} (ID: {interaction.user.id}) in server: {interaction.guild.name} (ID: {interaction.guild.id})"
            )
            channels = interaction.guild.channels
            view = SetupView(channels, self.config)
            await interaction.response.send_message(
                "Please select the appropriate role and channel:", view=view, ephemeral=True
            )
        except Exception as e:
            logging.error(e)

    @setup.error
    async def setup_error(self, interaction, error):
        if isinstance(error, CheckFailure):
            await interaction.response.send_message(
                "You don't have permission to use this command!", ephemeral=True
            )
            logging.warning(
                f"Unauthorized setup attempt by {interaction.user.name} (ID: {interaction.user.id}) in server: {interaction.guild.name} (ID: {interaction.guild.id})"
            )
            return


async def setup(bot) -> None:
    con = db_init()
    await bot.add_cog(Setup(bot, con))
