from discord.ext import commands
from src.utils import safe_send

@commands.command(name="version")
async def version(ctx):
    await safe_send(ctx, "Version 0.1.0")
