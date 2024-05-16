import logging
import discord
from discord.ext import commands
from discord import ui
from .db_utils import db_init, fetch_config  
import requests
import re

con = db_init()
api_token = 'YOUR_PICARTA_TOKEN'

url = "https://picarta.ai/classify"
headers = {"Content-Type": "application/json"}

class AiOsint(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        self.config = fetch_config(con)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message):
        try:
            if str(message.channel.id) == self.config['osint_bot_channel'] and message.attachments:
                for attachment in message.attachments:
                    img_url = attachment.url
                    result = await self.classify_image(img_url) 
                    await message.channel.send(embed=self.embed_result(result))
        except Exception as e:
            logging.error(f"Error in function locate:ai_osint.py: {e}")

    async def classify_image(self, img_url):
        payload = {"TOKEN": api_token, "IMAGE": img_url}
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while fetching image classification: {e}")
            return None

    def embed_result(self, result):
        if result:
            embed = discord.Embed(title=":mag: Image OSINT Results :mag_right:", color=0x00ff00)
            embed.add_field(name="Country", value=result.get('ai_country', 'Unknown'))
            embed.add_field(name="City", value=result.get('city', 'Unknown'))
            embed.add_field(name="Province", value=result.get('province', 'Unknown'))
            embed.add_field(name="Latitude", value=result.get('ai_lat', 'Unknown'))
            embed.add_field(name="Longitude", value=result.get('ai_lon', 'Unknown'))
        else:
            embed = discord.Embed(title="Image Classification Result", description="Failed to classify the image", color=0xff0000)
        return embed

    @discord.app_commands.command(
        name="locate",
        description="Locate an image using OSINT.",
    )
    async def locate(self, interaction: discord.Interaction, url: str) -> None:
        clean_url = validate_and_process_url(url)
        if clean_url:
            result = await self.classify_image(clean_url) 
            await interaction.response.send_message(embed=self.embed_result(result), ephemeral=True)
        else:
        	await interaction.response.send_message("Invalid URL supplied.", ephemeral=True)

def validate_and_process_url(url):
    pattern = r'\.(jpg|jpeg|png)$'
    clean_url = re.sub(r'\?.+$', '', url)
    if re.search(pattern, clean_url, re.IGNORECASE):
        return clean_url
    return None

async def setup(bot) -> None:
    await bot.add_cog(AiOsint(bot))  
