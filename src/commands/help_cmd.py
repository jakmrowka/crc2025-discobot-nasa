from discord.ext import commands
from utils import safe_send

@commands.command(name="pomoc")
async def pomoc(ctx):
    help_text = (
        "**Dostępne komendy:**\n\n"
        "**!daily [data]** – Astronomy Picture of the Day\n"
        "**!mars [data]** – zdjęcie z Marsa\n"
        "**!zoom location=\"adres\" [date=YYYY-MM-DD]** – zdjęcie satelitarne\n"
        "**!dodaj** – dodaj obrazek do ulubionych (odpowiedź na wiadomość)\n"
        "**!usun** – usuń obrazek z ulubionych (odpowiedź + brak serduszka)\n"
        "**!ulubione** – pokaż ulubione obrazki\n"
        "**!version** – wersja bota\n"
    )
    await safe_send(ctx, help_text)
