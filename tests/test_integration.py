import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import io

from src.app import (
    apod,
    mars,
    zoom,
    dodaj,
    usun,
    ulubione,
    favorites,
    sent_images,
    on_reaction_add
)

class DummyCtx:
    def __init__(self, author_id=123):
        self.guild = None
        self.channel = MagicMock()
        self.author = MagicMock()
        self.author.id = author_id
        self.message = MagicMock()
        self.message.reference = None

    async def send(self, *args, **kwargs):
        msg = MagicMock()
        msg.id = 1000  # przykładowe id
        return msg

@pytest.mark.asyncio
async def test_integration_add_and_remove_favorite():
    # Test integracyjny: symulujemy dodanie obrazka do ulubionych przez reakcję,
    # następnie wyświetlenie ulubionych i usunięcie za pomocą !usun.
    ctx = DummyCtx()

    # Symulujemy wysłanie obrazka (np. komenda !daily)
    fake_embed = MagicMock()
    fake_embed.title = "Integracyjny test"
    fake_msg = MagicMock()
    fake_msg.id = 2000
    sent_images[2000] = {"type": "embed", "embed": fake_embed}

    # Dodajemy ulubiony obrazek przez komendę !dodaj (odpowiadamy na fake_msg)
    reply = MagicMock()
    reply.id = 2000
    ctx.message.reference = MagicMock(resolved=reply)
    favorites[ctx.author.id] = []
    await dodaj(ctx)
    assert len(favorites[ctx.author.id]) == 1

    # Testujemy reakcję – symulujemy, że użytkownik dodaje reakcję serduszka
    reaction = MagicMock()
    reaction.emoji = "❤️"
    reaction.message = fake_msg
    # Symulujemy brak botowego użytkownika, a zwykłego użytkownika z id 123
    await on_reaction_add(reaction, ctx.author)
    # Powinno zostać dodane, ale ponieważ już mamy obrazek, lista nie powinna mieć duplikatów
    assert len(favorites[ctx.author.id]) == 1

    # Testujemy komendę !ulubione – symulujemy wyświetlenie ulubionych
    # Zmieniamy metodę send, aby zapamiętać wysłane id wiadomości
    ctx.send = AsyncMock(side_effect=ctx.send)
    await ulubione(ctx)
    # Zakładamy, że po wyświetleniu ulubionych każdy ulubiony obrazek posiada atrybut 'display_ids'
    fav = favorites[ctx.author.id][0]
    assert 'display_ids' in fav
    assert len(fav['display_ids']) > 0

    # Aby usunąć ulubiony obrazek za pomocą !usun,
    # symulujemy, że użytkownik usunął reakcję serduszka z wyświetlonej wiadomości.
    # Przygotowujemy kontekst odpowiadający na wiadomość z ulubionym obrazkiem.
    ctx.message.reference = MagicMock(resolved=MagicMock(id=fav['display_ids'][0], reactions=[]))
    await usun(ctx)
    # Po usunięciu lista ulubionych powinna być pusta.
    assert len(favorites[ctx.author.id]) == 0
