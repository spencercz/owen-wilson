import discord
import requests
import os
import asyncio

def download_file(url):
    '''
    Downloads the MP3 file from the given URL and places it in the same directory as this file.
    Designed specifically for MP3 files for this specific application.
    '''
    r = requests.get(url, allow_redirects=True)
    open('a.mp3', 'wb').write(r.content)

def get_wow():
    '''
    Uses Owen Wilson Wow API to get a random "Wow" sound byte and downloads the MP3 file.
    '''
    url = "https://owen-wilson-wow-api.onrender.com/wows/random"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    response = response.json()
    download_file(response[0]["audio"])
    return response

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

# API keys and bot initialization
TOKEN = os.getenv("WILSON")
bot = discord.Client()
path = r"D:\Fun\Owen Wilson\a.mp3"

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='wow', description="Owen Wilson says wow.",)
async def wow(ctx, hide=True):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("Wow! You're not in a voice channel.", hidden=True)
        return
    await ctx.defer(hidden=hide)
    info = get_wow()
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(executable=r"C:\MinGW\bin\ffmpeg.exe", source=path))
    while vc.is_playing():
        await asyncio.sleep(1)
    await ctx.guild.voice_client.disconnect()
    await ctx.send(f'This wow is from the movie {info[0]["movie"]}, released on {convert_date(info[0]["release_date"])}. Owen Wilson, playing the character {info[0]["character"]}, said it at {info[0]["timestamp"]}. The full line was \"{info[0]["full_line"]}\"', hidden=hide)

bot.run(TOKEN)
