import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import io

from src.app import safe_send, apod, dodaj, favorites, sent_images

class DummyCtx:
    def __init__(self):
        self.guild = None
        self.channel = MagicMock()
        self.author = MagicMock()
        self.author.id = 123
        self.message = MagicMock()
        self.message.reference = None

    async def send(self, *args, **kwargs):
        # Zwracamy obiekt wiadomości z minimalnymi atrybutami
        msg = MagicMock()
        msg.id = 999
        return msg

@pytest.mark.asyncio
async def test_safe_send_returns_message():
    ctx = DummyCtx()
    # Testujemy, że funkcja safe_send zwraca obiekt wiadomości
    msg = await safe_send(ctx, "Test")
    assert msg is not None

@pytest.mark.asyncio
async def test_apod_success():
    # Testujemy komendę !daily, symulując poprawną odpowiedź z NASA API.
    ctx = DummyCtx()

    # Przygotowujemy fałszywą odpowiedź API
    fake_data = {
        "title": "Test APOD",
        "url": "http://example.com/apod.png",
        "explanation": "Test explanation"
    }
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = fake_data

    with patch("src.app.requests.get", return_value=fake_response) as mock_get:
        await apod(ctx, date="2025-02-18")
        # Sprawdzamy, czy zapisało wiadomość w sent_images (używamy stałego id 999 z DummyCtx.send)
        assert 999 in sent_images
        embed = sent_images[999].get("embed")
        assert embed.title == "Test APOD"

@pytest.mark.asyncio
async def test_dodaj_already_added():
    # Testujemy komendę !dodaj, gdy użytkownik próbuje dodać ten sam obrazek dwa razy.
    ctx = DummyCtx()
    # Symulujemy wiadomość, która była wysłana przez komendy wyświetlające obrazek
    fake_msg = MagicMock()
    fake_msg.id = 888
    # Zapisujemy dane obrazka w sent_images
    sent_images[888] = {"type": "embed", "embed": MagicMock(title="Test Image")}
    # Ustawiamy kontekst jako reply do wiadomości z id 888
    reply = MagicMock()
    reply.id = 888
    ctx.message.reference = MagicMock(resolved=reply)
    favorites[ctx.author.id] = []
    await dodaj(ctx)
    # Druga próba dodania – obrazek już jest w ulubionych
    await dodaj(ctx)
    # Lista ulubionych nie powinna mieć więcej niż jeden element
    assert len(favorites[ctx.author.id]) == 1