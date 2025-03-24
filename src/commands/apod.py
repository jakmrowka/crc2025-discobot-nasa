from discord.ext import commands
from src.config import NASA_API_KEY, sent_images
from src.utils import safe_send
import discord
import requests

@commands.command(name="daily")
async def apod(ctx, date: str = None):
    params = {"api_key": NASA_API_KEY}
    if date:
        params["date"] = date
    response = requests.get("https://api.nasa.gov/planetary/apod", params=params)
    if response.status_code != 200:
        await safe_send(ctx, "Błąd pobierania danych APOD.")
        return
    data = response.json()
    embed = discord.Embed(title=data.get("title", "APOD"))
    embed.set_image(url=data.get("url"))
    embed.description = data.get("explanation", "")
    msg = await safe_send(ctx, embed=embed)
    if msg:
        sent_images[msg.id] = {"type": "embed", "embed": embed}