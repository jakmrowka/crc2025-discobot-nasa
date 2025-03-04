import discord
from discord.ext import commands
import requests
import os
import io
from datetime import datetime
import shlex
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)

# Klucz API NASA pobierany z zmiennych środowiskowych (lub użyj własnego)
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Inicjalizacja bota z wymaganymi intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Słowniki przechowujące dane o wysłanych obrazkach i ulubionych użytkowników.
# sent_images mapuje id wiadomości -> słownik z danymi obrazka.
sent_images = {}
# favorites mapuje id użytkownika -> lista słowników z danymi obrazka.
# Każdy element może zawierać opcjonalnie klucz "display_ids" – listę id wiadomości, na których został wyświetlony.
favorites = {}


async def safe_send(ctx, *args, **kwargs):
    """
    Funkcja pomocnicza do wysyłania wiadomości – przed wysłaniem sprawdza uprawnienia.
    Zwraca obiekt wiadomości, jeśli wysłanie się powiedzie.
    """
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            logging.warning(
                f"Brak uprawnień do wysyłania wiadomości na kanale {ctx.channel} (ID: {ctx.channel.id})."
            )
            return None
    try:
        message = await ctx.send(*args, **kwargs)
        return message
    except discord.Forbidden:
        logging.warning(
            f"Brak uprawnień do wysyłania wiadomości na kanale {ctx.channel} (ID: {ctx.channel.id})."
        )
        return None


@bot.command(name="daily")
async def apod(ctx, date: str = None):
    """
    Komenda daily – pobiera Astronomy Picture of the Day.
    Przykłady:
      - !daily
          -> pobiera obraz dnia (dzisiejszy).
      - !daily 2025-02-18
          -> pobiera obraz z daty 2025-02-18.
    """
    logging.info(f"Wywołano komendę daily z parametrem date={date}")
    params = {"api_key": NASA_API_KEY}
    if date:
        params["date"] = date
    url = "https://api.nasa.gov/planetary/apod"
    response = requests.get(url, params=params)
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


@bot.command(name="mars")
async def mars(ctx, date: str = None):
    """
    Komenda mars – pobiera zdjęcie z łazika Curiosity.
    Przykłady:
      - !mars
          -> pobiera zdjęcie z dzisiejszej daty.
      - !mars 2025-02-18
          -> pobiera zdjęcie z daty 2025-02-18.
    """
    logging.info(f"Wywołano komendę mars z parametrem date={date}")
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
    data = response.json()
    photos = data.get("photos", [])
    if photos:
        photo_url = photos[0].get("img_src")
        embed = discord.Embed(title=f"Zdjęcie z Marsa z daty {params['earth_date']}")
        embed.set_image(url=photo_url)
        msg = await safe_send(ctx, embed=embed)
        if msg:
            sent_images[msg.id] = {"type": "embed", "embed": embed}
    else:
        await safe_send(ctx, "Nie znaleziono zdjęć dla podanej daty.")


@bot.command(name="zoom")
async def zoom(ctx, *, args=None):
    """
    Komenda zoom – pobiera zdjęcie satelitarne dla wskazanej lokalizacji.
    Przykłady:
      - !zoom location="Warsaw, ul. Marszałkowska 1"
          -> pobiera zdjęcie satelitarne dla lokalizacji "Warsaw, ul. Marszałkowska 1" (dzisiejsza data).
      - !zoom location="Warsaw, ul. Marszałkowska 1" date=2025-02-18
          -> pobiera zdjęcie satelitarne dla tej lokalizacji z daty 2025-02-18.
    """
    logging.info(f"Wywołano komendę zoom z argumentami: {args}")
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
            ctx,
            'Musisz podać parametr location, np.: location="Warsaw, ul. Marszałkowska 1"',
        )
        return

    location = params_input["location"]

    # Geokodowanie adresu przy użyciu Nominatim (OpenStreetMap)
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

    # Pobieramy obraz – opcjonalnie można podać datę, domyślnie dzisiejsza data
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


@bot.command(name="pomoc")
async def pomoc(ctx):
    """
    Komenda pomoc – wyświetla dostępne komendy oraz przykłady użycia.
    """
    logging.info("Wywołano komendę pomoc")
    help_text = (
        "**Dostępne komendy:**\n\n"
        "**!daily [data]**\n"
        "  - Pobiera Astronomy Picture of the Day.\n"
        "      `!daily` lub `!daily 2025-02-18`\n\n"
        "**!mars [data]**\n"
        "  - Pobiera zdjęcie z łazika Curiosity.\n"
        "      `!mars` lub `!mars 2025-02-18`\n\n"
        '**!zoom location="adres" [date=YYYY-MM-DD]**\n'
        "  - Pobiera zdjęcie satelitarne dla wskazanej lokalizacji.\n"
        '      `!zoom location="Warsaw, ul. Marszałkowska 1"` lub `!zoom location="Warsaw, ul. Marszałkowska 1" date=2025-02-18`\n\n'
        "**!dodaj**\n"
        "  - Dodaje obrazek do ulubionych. Użyj komendy w odpowiedzi (reply) na wiadomość z obrazkiem lub dodaj reakcję ❤️.\n\n"
        "**!usun**\n"
        "  - Usuwa obrazek z ulubionych. Aby to zadziałało, odpowiedz (reply) na wiadomość wysłaną przez komendę **!ulubione** i upewnij się, że usunąłeś reakcję serduszka z tej wiadomości.\n\n"
        "**!ulubione**\n"
        "  - Wyświetla zapisane ulubione obrazki.\n"
    )
    await safe_send(ctx, help_text)


@bot.command(name="version")
async def version(ctx):
    """
    Komenda wersja – wyświetla nazwe wersji.
    """
    logging.info("Wywołano komendę wersja")
    version_text = "Version 0.1.0"
    await safe_send(ctx, version_text)


@bot.command(name="dodaj")
async def dodaj(ctx):
    """
    Komenda dodaj – dodaje obrazek do ulubionych.
    Aby zadziałała, należy odpowiedzieć (reply) na wiadomość, która zawiera obrazek.
    """
    if ctx.message.reference is None:
        await safe_send(
            ctx,
            "Proszę odpowiedzieć na wiadomość z obrazkiem, który chcesz dodać do ulubionych.",
        )
        return
    ref = ctx.message.reference.resolved
    if ref is None or ref.id not in sent_images:
        await safe_send(
            ctx, "Nie znaleziono obrazka w wiadomości, na którą odpowiadasz."
        )
        return
    image_data = sent_images[ref.id]
    user_favs = favorites.get(ctx.author.id, [])
    if image_data in user_favs:
        await safe_send(ctx, "Ten obrazek jest już w ulubionych.")
        return
    # Dodajemy obrazek do ulubionych użytkownika
    user_favs.append(image_data)
    favorites[ctx.author.id] = user_favs
    await safe_send(ctx, f"{ctx.author.mention}, obrazek dodany do ulubionych!")


@bot.command(name="usun")
async def usun(ctx):
    """
    Komenda usun – usuwa obrazek z ulubionych.
    Aby zadziałała, należy odpowiedzieć (reply) na wiadomość wysłaną przez komendę **!ulubione**
    oraz upewnić się, że nie masz już na niej reakcji serduszka.
    """
    if ctx.message.reference is None:
        await safe_send(
            ctx,
            "Proszę odpowiedzieć na wiadomość z obrazkiem, który chcesz usunąć z ulubionych.",
        )
        return
    ref = ctx.message.reference.resolved
    if ref is None:
        await safe_send(ctx, "Nie znaleziono wiadomości, na którą odpowiadasz.")
        return

    # Sprawdzamy, czy na wiadomości nie ma reakcji serduszka od autora
    heart_present = False
    for reaction in ref.reactions:
        if str(reaction.emoji) == "❤️":
            users = await reaction.users().flatten()
            if ctx.author in users:
                heart_present = True
                break
    if heart_present:
        await safe_send(
            ctx,
            "Najpierw usuń reakcję serduszka z obrazka, aby go usunąć z ulubionych.",
        )
        return

    # Szukamy w ulubionych tego użytkownika ulubionego obrazka, który został wyświetlony (klucz display_ids zawiera id wiadomości)
    user_favs = favorites.get(ctx.author.id, [])
    found = False
    for fav in user_favs:
        if "display_ids" in fav and ref.id in fav["display_ids"]:
            user_favs.remove(fav)
            favorites[ctx.author.id] = user_favs
            found = True
            await safe_send(
                ctx, f"{ctx.author.mention}, obrazek został usunięty z ulubionych!"
            )
            break
    if not found:
        await safe_send(ctx, "Nie znaleziono tego obrazka w Twoich ulubionych.")


@bot.command(name="ulubione")
async def ulubione(ctx):
    """
    Komenda ulubione – wyświetla zapisane ulubione obrazki.
    Przy wysyłaniu każdego obrazka zapisujemy jego id (display_ids),
    aby można było później odwołać się do niego przy usuwaniu.
    """
    user_favs = favorites.get(ctx.author.id, [])
    if not user_favs:
        await safe_send(ctx, "Nie masz jeszcze ulubionych obrazków.")
        return
    for fav in user_favs:
        if fav.get("type") == "embed":
            msg = await safe_send(ctx, embed=fav["embed"])
        elif fav.get("type") == "file":
            msg = await safe_send(
                ctx,
                file=discord.File(
                    fp=io.BytesIO(fav["file_bytes"]),
                    filename=fav.get("filename", "image.png"),
                ),
            )
        # Zapisujemy id wiadomości, na których wyświetlono ten obrazek
        if msg:
            if "display_ids" not in fav:
                fav["display_ids"] = []
            fav["display_ids"].append(msg.id)
            # Dodajemy również wiadomość do sent_images, aby później móc odwołać się do danych obrazka
            sent_images[msg.id] = fav


@bot.event
async def on_reaction_add(reaction, user):
    """
    Gdy użytkownik doda reakcję, sprawdzamy czy jest to serduszko.
    Jeśli tak, a wiadomość zawiera obrazek (zapisany w sent_images),
    dodajemy go do ulubionych użytkownika.
    """
    if user.bot:
        return
    if str(reaction.emoji) == "❤️":
        msg = reaction.message
        if msg.id in sent_images:
            image_data = sent_images[msg.id]
            user_favs = favorites.get(user.id, [])
            if image_data not in user_favs:
                user_favs.append(image_data)
                favorites[user.id] = user_favs
                try:
                    await msg.channel.send(
                        f"{user.mention}, dodano obrazek do ulubionych!"
                    )
                except Exception as e:
                    logging.error("Błąd przy wysyłaniu potwierdzenia: " + str(e))


TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Brak BOT_TOKEN w zmiennych środowiskowych.")

if __name__ == "__main__":
    logging.info("Bot starting...")
    logging.info(TOKEN)
    bot.run(TOKEN)
