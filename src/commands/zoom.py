from discord.ext import commands
from src.config import NASA_API_KEY, sent_images
from src.utils import safe_send
from datetime import datetime
import discord
import requests
import shlex
import io

@commands.command(name="zoom")
async def zoom(ctx, *, args=None):
    params_input = {}

    if args:
        try:
            lexer = shlex.shlex(args, posix=True)
            lexer.whitespace_split = True
            tokens = list(lexer)
            for token in tokens:
                if "=" in token:
                    key, value = token.split("=", 1)
                    params_input[key.lower()] = value.strip('"')
        except Exception as e:
            await safe_send(ctx, "Błąd w parsowaniu argumentów: " + str(e))
            return

    if "location" not in params_input:
        await safe_send(
            ctx, 'Musisz podać parametr location, np.: location="Warsaw, ul. Marszałkowska 1"'
        )
        return

    location = params_input["location"]
    geocode_url = "https://nominatim.openstreetmap.org/search"
    geocode_params = {"q": location, "format": "json", "limit": 1}
    geo_response = requests.get(
        geocode_url, params=geocode_params, headers={"User-Agent": "DiscordBot"}
    )
    if geo_response.status_code != 200:
        await safe_send(ctx, "Błąd geokodowania lokalizacji.")
        return

    geo_data = geo_response.json()
    if not geo_data:
        await safe_send(ctx, "Nie znaleziono lokalizacji dla: " + location)
        return

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]
    date = params_input.get("date", datetime.now().strftime("%Y-%m-%d"))

    earth_params = {
        "lat": lat,
        "lon": lon,
        "date": date,
        "dim": 0.1,
        "api_key": NASA_API_KEY,
    }
    earth_url = "https://api.nasa.gov/planetary/earth/imagery"
    resp = requests.get(earth_url, params=earth_params, timeout=60)
    if resp.status_code == 200:
        msg = await safe_send(
            ctx, file=discord.File(fp=io.BytesIO(resp.content), filename="earth.png")
        )
        if msg:
            sent_images[msg.id] = {
                "type": "file",
                "file_bytes": resp.content,
                "filename": "earth.png",
            }
    else:
        await safe_send(ctx, "Nie udało się pobrać obrazu dla daty: " + date)
8