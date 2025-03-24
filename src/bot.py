from config import bot, TOKEN
import logging

# Załaduj komendy
from commands import apod, mars, zoom, favorites, help_cmd, version
bot.add_command(apod.apod)
bot.add_command(mars.mars)
bot.add_command(zoom.zoom)
bot.add_command(favorites.dodaj)
bot.add_command(favorites.usun)
bot.add_command(favorites.ulubione)
bot.add_command(help_cmd.pomoc)
bot.add_command(version.version)

# Załaduj eventy
from events.reactions import on_reaction_add
bot.event(on_reaction_add)

if __name__ == "__main__":
    logging.info("Bot starting...")
    bot.run(TOKEN)
