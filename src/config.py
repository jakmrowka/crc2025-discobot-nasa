import os
import logging
import discord
from discord.ext import commands

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# Klucze API
NASA_API_KEY = os.getenv("NASA_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Brak BOT_TOKEN w zmiennych środowiskowych.")

# Inicjalizacja bota
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Zasoby współdzielone
sent_images = {}
favorites = {}