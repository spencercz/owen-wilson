import discord
from discord import app_commands
import aiohttp
import os
import asyncio

async def get_wow():
    '''
    Uses Owen Wilson Wow API to get a random "Wow" sound byte.
    Returns the info for the wow, including the URL of its MP3 file.
    '''
    url = "https://owen-wilson-wow-api.onrender.com/wows/random"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

def convert_date(date):
    '''
    Assumes date format YYYY-MM-DD and converts to Month Day, Year
    '''
    _DATE_DICT = {
        "01" : "January",
        "02" : "February",
        "03" : "March",
        "04" : "April",
        "05" : "May",
        "06" : "June",
        "07" : "July",
        "08" : "August",
        "09" : "September",
        "10" : "October",
        "11" : "November",
        "12" : "December",
    }
    year = date[:4]
    month = date[5:7]
    day = date[8:]
    return f"{_DATE_DICT[month]} {day}, {year}"

class OwenClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Registers the slash commands with Discord
        await self.tree.sync()

# API keys and bot initialization
TOKEN = os.getenv("WILSON")
bot = OwenClient()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.tree.command(name='wow', description="Owen Wilson says wow.")
@app_commands.describe(hide="Only show the movie info to you (default: True)")
@app_commands.guild_only()
async def wow(interaction: discord.Interaction, hide: bool = True):
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message("Wow! You're not in a voice channel.", ephemeral=True)
        return
    channel = interaction.user.voice.channel
    await interaction.response.defer(ephemeral=hide, thinking=True)
    info = await get_wow()

    vc = interaction.guild.voice_client
    if vc is None:
        vc = await channel.connect()
    else:
        await vc.move_to(channel)
    try:
        vc.play(discord.FFmpegPCMAudio(source=info[0]["audio"]))
        while vc.is_playing():
            await asyncio.sleep(1)
    finally:
        await vc.disconnect()

    await interaction.followup.send(f'This wow is from the movie {info[0]["movie"]}, released on {convert_date(info[0]["release_date"])}. Owen Wilson, playing the character {info[0]["character"]}, said it at {info[0]["timestamp"]}. The full line was \"{info[0]["full_line"]}\"', ephemeral=hide)

bot.run(TOKEN)
