from discord.ext import commands
from src.config import sent_images, favorites
from src.utils import safe_send
import discord
import io

@commands.command(name="dodaj")
async def dodaj(ctx):
    if ctx.message.reference is None:
        await safe_send(ctx, "Odpowiedz na wiadomość z obrazkiem, który chcesz dodać.")
        return

    ref = ctx.message.reference.resolved
    if ref is None or ref.id not in sent_images:
        await safe_send(ctx, "Nie znaleziono obrazka w odpowiedzi.")
        return

    image_data = sent_images[ref.id]
    user_favs = favorites.get(ctx.author.id, [])
    if image_data in user_favs:
        await safe_send(ctx, "Ten obrazek jest już w ulubionych.")
        return

    user_favs.append(image_data)
    favorites[ctx.author.id] = user_favs
    await safe_send(ctx, f"{ctx.author.mention}, dodano do ulubionych!")

@commands.command(name="usun")
async def usun(ctx):
    if ctx.message.reference is None:
        await safe_send(ctx, "Odpowiedz na wiadomość z obrazkiem, który chcesz usunąć.")
        return

    ref = ctx.message.reference.resolved
    if ref is None:
        await safe_send(ctx, "Nie znaleziono wiadomości.")
        return

    heart_present = False
    for reaction in ref.reactions:
        if str(reaction.emoji) == "❤️":
            users = await reaction.users().flatten()
            if ctx.author in users:
                heart_present = True
                break

    if heart_present:
        await safe_send(ctx, "Usuń reakcję serduszka, aby usunąć z ulubionych.")
        return

    user_favs = favorites.get(ctx.author.id, [])
    found = False
    for fav in user_favs:
        if "display_ids" in fav and ref.id in fav["display_ids"]:
            user_favs.remove(fav)
            favorites[ctx.author.id] = user_favs
            found = True
            await safe_send(ctx, f"{ctx.author.mention}, obrazek usunięty z ulubionych!")
            break

    if not found:
        await safe_send(ctx, "Nie znaleziono tego obrazka w ulubionych.")

@commands.command(name="ulubione")
async def ulubione(ctx):
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
        if msg:
            if "display_ids" not in fav:
                fav["display_ids"] = []
            fav["display_ids"].append(msg.id)
            sent_images[msg.id] = fav
