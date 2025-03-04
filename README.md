
# CRC-NasaBot

CRC-NasaBot to bot Discord napisany w Pythonie, który integruje się z API NASA i oferuje szereg komend umożliwiających pobieranie zdjęć astronomicznych, zdjęć z Marsa oraz zdjęć satelitarnych dla podanych lokalizacji. Dodatkowo bot umożliwia dodawanie obrazków do ulubionych oraz zarządzanie nimi poprzez reakcje.

## Funkcje

- **!daily [data]** – Pobiera Astronomy Picture of the Day (APOD) z API NASA. Jeśli data nie zostanie podana, domyślnie pobierany jest obraz dla dnia bieżącego.
- **!mars [data]** – Pobiera zdjęcie z łazika Curiosity. Data jest opcjonalna (domyślnie dzisiejsza).
- **!zoom location="adres" [date=YYYY-MM-DD]** – Pobiera zdjęcie satelitarne dla podanej lokalizacji (oraz opcjonalnie z określonej daty).
- **!dodaj** – Dodaje obrazek do ulubionych (poprzez odpowiedź na wiadomość z obrazkiem lub reakcję).
- **!usun** – Usuwa obrazek z ulubionych.
- **!ulubione** – Wyświetla zapisane ulubione obrazki.

## Wymagania

- Python 3.9 lub nowszy
- [discord.py](https://discordpy.readthedocs.io/)
- [requests](https://docs.python-requests.org/)
- [imageio](https://imageio.readthedocs.io/)
- Inne narzędzia do testów i stylizacji: pytest, pytest-asyncio, flake8, black

## Instalacja i Uruchomienie

1. **Klonowanie repozytorium**

   ```bash
   git clone https://github.com/jakmrowka/crc2025-discobot-nasa.git
   cd crc2025-discobot-nasa
   ```

2. **Utworzenie i aktywacja wirtualnego środowiska**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

3. **Instalacja zależności**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Konfiguracja zmiennych środowiskowych**

   Utwórz zmienne środowiskowe:
   - `BOT_TOKEN` – token Twojego bota Discord.
   - `NASA_API_KEY` – klucz API z NASA (możesz uzyskać bezpłatny klucz na [NASA API Portal](https://api.nasa.gov/)).

   Na przykład, możesz utworzyć plik `.env` (jeśli używasz narzędzia do ładowania zmiennych, np. python-dotenv) lub ustawić zmienne ręcznie:
   
   ```bash
   export BOT_TOKEN="twoj_token"
   export NASA_API_KEY="twoj_klucz_api"
   ```

5. **Uruchomienie bota**

   ```bash
   python src/app.py
   ```

## Testy

Testy są napisane przy użyciu `pytest` oraz `pytest-asyncio` i obejmują zarówno testy jednostkowe, jak i integracyjne.

Aby uruchomić testy:

1. Upewnij się, że zmienna środowiskowa `BOT_TOKEN` jest ustawiona (możesz ustawić jej wartość na `dummy` podczas testów).  
   Możesz też utworzyć plik `tests/conftest.py` z następującą zawartością:

   ```python
   import os
   os.environ["BOT_TOKEN"] = "dummy"
   ```

2. Uruchom testy:

   ```bash
   pytest tests
   ```

## Docker

Aplikację można zbudować i uruchomić w kontenerze Docker. Przykładowy plik `Dockerfile`:

```dockerfile
FROM python:3.9-slim
LABEL authors="gad"

WORKDIR /app
COPY requirements.txt requirements.txt

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Utwórz użytkownika nieuprzywilejowanego i ustaw uprawnienia
RUN useradd -m appuser && chown -R appuser:appuser /app
COPY . .
RUN rm Dockerfile

USER appuser
EXPOSE 32025

CMD [ "python", "src/app.py" ]
```

### Budowanie i uruchomienie kontenera

1. **Budowanie obrazu**

   ```bash
   docker build -t NAME:latest -f src/Dockerfile src/
   ```

2. **Uruchomienie kontenera**

   Upewnij się, że zmienne środowiskowe są ustawione, np.:

   ```bash
   docker run -e BOT_TOKEN="twoj_token" -e NASA_API_KEY="twoj_klucz_api" -p 32025:32025 NAME:latest
   ```

## Wdrożenie w Kubernetes z Helm

Bot działa jako klient (inicjuje połączenia wychodzące), więc do wdrożenia wystarczy Deployment. Jeśli chcesz wymusić uruchomienie na konkretnym nodzie (np. `minipc1`), możesz użyć `nodeSelector` w manifeście Deployment.

Przykładowy fragment `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crc-bot
  labels:
    app: crc-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crc-bot
  template:
    metadata:
      labels:
        app: crc-bot
    spec:
      containers:
        - name: crc-bot
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: BOT_TOKEN
              value: "{{ .Values.env.BOT_TOKEN }}"
            - name: NASA_API_KEY
              value: "{{ .Values.env.NASA_API_KEY }}"
          ports:
            - containerPort: {{ .Values.service.port }}
```

## CI/CD – Azure Pipelines

Przykładowy pipeline Azure definiuje etapy:
- **Tests:** Tworzenie wirtualnego środowiska, instalacja zależności, uruchomienie testów i sprawdzenie kodu przy użyciu Black.
- **Docker:** Budowanie i wypychanie obrazu Dockera.
- **microk8s:** Wdrożenie Helm na klastrze.
- **GithubSync:** Synchronizacja repozytorium.

Fragment pipeline YAML (zobacz pełny kod w repozytorium):

```yaml
# [Przykładowa konfiguracja pipeline]
trigger:
  branches:
    include:
      - '*'
  
# Parametry, zmienne oraz etapy pipeline są zdefiniowane poniżej
# [Pełna konfiguracja pipeline w pliku azure-pipelines.yml]
```

## Kontrybucje

Jeśli chcesz przyczynić się do rozwoju projektu, proszę otwórz pull request lub zgłoś issue w repozytorium GitHub.


---

Dzięki tym instrukcjom będziesz mógł lokalnie rozwijać, testować i wdrażać CRC-NasaBot zarówno w środowisku Docker, jak i Kubernetes, a także zautomatyzować procesy CI/CD przy użyciu Azure Pipelines.
```