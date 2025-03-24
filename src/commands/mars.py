from discord.ext import commands
from src.config import NASA_API_KEY, sent_images
from src.utils import safe_send
from datetime import datetime
import discord
import requests

@commands.command(name="mars")
async def mars(ctx, date: str = None):
    params = {"api_key": NASA_API_KEY}
    if date:
        params["earth_date"] = date
    else:
        params["earth_date"] = datetime.now().strftime("%Y-%m-%d")

    url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        await safe_send(ctx, "Błąd pobierania zdjęć z Marsa.")
        return

    photos = response.json().get("photos", [])
    if photos:
        photo_url = photos[0].get("img_src")
        embed = discord.Embed(title=f"Zdjęcie z Marsa z daty {params['earth_date']}")
        embed.set_image(url=photo_url)
        msg = await safe_send(ctx, embed=embed)
        if msg:
            sent_images[msg.id] = {"type": "embed", "embed": embed}
    else:
        await safe_send(ctx, "Nie znaleziono zdjęć dla podanej daty.")
