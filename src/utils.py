import logging

async def safe_send(ctx, *args, **kwargs):
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            logging.warning(f"Brak uprawnień do wysyłania wiadomości na kanale {ctx.channel} (ID: {ctx.channel.id}).")
            return None
    try:
        return await ctx.send(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Błąd przy wysyłaniu wiadomości: {e}")
        return None