from src.config import sent_images, favorites
import logging

async def on_reaction_add(reaction, user):
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
                    await msg.channel.send(f"{user.mention}, dodano obrazek do ulubionych!")
                except Exception as e:
                    logging.error("Błąd przy wysyłaniu potwierdzenia: " + str(e))
