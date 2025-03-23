FROM python:3.11-slim
LABEL authors="gad"

WORKDIR /src
COPY pyproject.toml pyproject.toml

# Zainstaluj wymagane pakiety
RUN pip install --no-cache-dir .

# Utwórz użytkownika bez uprawnień administracyjnych i ustaw odpowiednie uprawnienia dla katalogu /src
RUN useradd -m appuser && chown -R appuser:appuser /src
# Skopiuj skrypt do katalogu roboczego
COPY ./src .

#RUN apt-get update && apt-get install -y dnsutils libnss3
# Ustaw użytkownika
USER appuser
EXPOSE 32025
# Uruchom skrypt Pythona przy starcie kontenera
CMD [ "python", "app.py" ]
#CMD ["tail", "-f", "/dev/null"]
