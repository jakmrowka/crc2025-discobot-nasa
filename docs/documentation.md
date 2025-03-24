Poniżej znajdziesz przykładową dokumentację, którą możesz umieścić w folderze `docs` (np. jako plik `Dokumentacja.md`). Dokumentacja ta opisuje strukturę projektu, instalację, konfigurację, uruchamianie, testowanie i rozwój projektu.

---

# Dokumentacja projektu crc-nasabot

## Spis treści

- [Opis projektu](#opis-projektu)
- [Struktura projektu](#struktura-projektu)
- [Instalacja i konfiguracja](#instalacja-i-konfiguracja)
- [Uruchamianie bota](#uruchamianie-bota)
- [Testowanie](#testowanie)
- [Rozwój i kontrybucje](#rozwój-i-kontrybucje)
- [Licencja](#licencja)

---

## Opis projektu

**crc-nasabot** to bot Discorda wykorzystujący API NASA do pobierania zdjęć kosmicznych, zdjęć z Marsa, obrazów satelitarnych oraz zarządzania ulubionymi obrazkami. Projekt demonstruje modularne podejście do budowania aplikacji w Pythonie, wykorzystując bibliotekę `discord.py` oraz organizację kodu w wielu modułach.

---

## Struktura projektu

Projekt został podzielony na kilka modułów, aby ułatwić jego rozwój, testowanie i utrzymanie. Oto przykładowa struktura katalogów:

```
crc-nasabot/
├── src/
│   ├── __init__.py
│   ├── app.py             # Główny plik uruchomieniowy bota
│   ├── config.py          # Konfiguracja, klucze API, globalny stan (favorites, sent_images)
│   ├── utils.py           # Funkcje pomocnicze (np. safe_send)
│   ├── commands/          # Komendy bota
│   │   ├── __init__.py
│   │   ├── apod.py        # Komenda !daily
│   │   ├── mars.py        # Komenda !mars
│   │   ├── zoom.py        # Komenda !zoom
│   │   ├── favorites.py   # Komendy !dodaj, !usun, !ulubione
│   │   ├── help_cmd.py    # Komenda !pomoc
│   │   └── version.py     # Komenda !version
│   └── events/            # Obsługa eventów (np. on_reaction_add)
│       ├── __init__.py
│       └── reactions.py
├── tests/                 # Testy jednostkowe i integracyjne
│   ├── test_unit.py
│   └── test_integration.py
├── docs/                  # Dokumentacja projektu (ten folder)
│   └── Dokumentacja.md    # Plik z dokumentacją
├── .venv/                # Środowisko wirtualne
├── README.md              # Plik Readme z ogólnym opisem projektu
├── requirements.txt       # Lista zależności projektu
└── pytest.ini             # Konfiguracja dla pytest
```

---

## Instalacja i konfiguracja

1. **Klonowanie repozytorium**  
   Sklonuj repozytorium na lokalny komputer:
   ```bash
   git clone https://github.com/twoj-uzytkownik/crc-nasabot.git
   cd crc-nasabot
   ```

2. **Utworzenie środowiska wirtualnego**  
   Utwórz nowe środowisko wirtualne i je aktywuj:
   ```bash
   python -m venv .venv
   # Na systemie Windows:
   .venv\Scripts\activate
   # Na systemach Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalacja zależności**  
   Zainstaluj wymagane pakiety:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfiguracja zmiennych środowiskowych**  
   Utwórz plik `.env` (lub ustaw zmienne w systemie) z kluczami:
   ```
   BOT_TOKEN=<twoj_bot_token>
   NASA_API_KEY=<twoj_klucz_api_NASA>
   ```

---

## Uruchamianie bota

Aby uruchomić bota, upewnij się, że środowisko wirtualne jest aktywne i wykonaj:
```bash
python src/app.py
```
Bot powinien się zalogować i rozpocząć nasłuchiwanie komend na Discordzie.

---

## Testowanie

Testy zostały podzielone na testy jednostkowe i integracyjne. Aby je uruchomić, użyj polecenia:
```bash
pytest
```

### Ważne uwagi:
- Upewnij się, że przed uruchomieniem testów globalne stany (np. `favorites`, `sent_images`) są czyszczone. W testach używamy fixture, które to wykonują.
- Testy wykorzystują patchowanie z użyciem `unittest.mock`, co pozwala symulować odpowiedzi API oraz zachowanie kontekstu bota.

---

## Rozwój i kontrybucje

Jeśli chcesz przyczynić się do projektu:
1. Sklonuj repozytorium.
2. Utwórz nową gałąź (`feature/moja-funkcjonalnosc`).
3. Wprowadź zmiany i upewnij się, że wszystkie testy przechodzą.
4. Stwórz Pull Request, opisując zmiany.

---

## Licencja

Projekt jest dostępny na licencji [tutaj wpisz typ licencji, np. MIT]. Szczegółowe informacje znajdziesz w pliku `LICENSE` w katalogu głównym projektu.

---

To przykładowa dokumentacja, którą możesz rozwijać w miarę potrzeb. Możesz dodać kolejne sekcje (np. FAQ, przykłady użycia, diagramy architektury) według potrzeb projektu. Jeśli masz dodatkowe pytania lub chcesz rozbudować dokumentację o konkretne aspekty, daj znać!