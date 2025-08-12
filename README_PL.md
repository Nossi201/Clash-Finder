<!-- path: README_PL.md -->

# Clash Finder 🎮

![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3%2B-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)
![Selenium](https://img.shields.io/badge/selenium-4%2B-orange.svg)
![Tests](https://img.shields.io/badge/tests-green.svg)

## Opis projektu 📋

Clash Finder to aplikacja webowa League of Legends oparta na Flasku. Umożliwia analizę statystyk graczy oraz przegląd szczegółowej historii meczów. Projekt kładzie nacisk na jakość kodu, cache’owanie i automatyczne testy (jednostkowe, integracyjne i end‑to‑end).

**Konteneryzacja** w minimalnym, produkcyjnym układzie:

```
Internet → NGINX → Flask (Gunicorn) ↔ Redis
                     ↘ Riot API
```

**Ephemeral** (uruchamiane tylko na czas potrzeby): kontenery testów oraz Selenium (Chrome).

## Kluczowe funkcje ✨

* **Statystyki i historia gier** (KDA, CS, KP, win/loss, przedmioty, runy)
* **Responsywny interfejs** (Bootstrap 5)
* **Asynchroniczny fetch** dla batchy zapytań
* **Cache** w Redis (współdzielony między workerami)
* **Weryfikacja HTTPS** przez `certifi`
* **Automatyczne testy**: unit/integration + E2E (Selenium)

## Spis treści

* [Technologie](#technologie)
* [Wymagania wstępne](#wymagania)
* [Uruchomienie (Docker)](#docker-start)
* [Uruchom aplikację](#open-the-app)
* [Konfiguracja](#konfiguracja)
* [Development lokalny (opcjonalnie)](#dev-local)
* [Testy](#testy)
* [Struktura projektu](#struktura)
* [Endpointy API](#api)
* [Ograniczenia i plan rozwoju](#roadmap)
* [Licencja](#license)
* [Zastrzeżenia](#disclaimer)

<a id="technologie"></a>

## Technologie 🛠️

* **Backend**: Python 3.12, Flask, aiohttp/asyncio, Requests, Gunicorn
* **Reverse Proxy**: NGINX
* **Cache**: Redis
* **Frontend**: HTML5, CSS3, JS (ES6+), Bootstrap 5
* **Security**: weryfikacja SSL/TLS poprzez `certifi`
* **Testing**: pytest, Selenium WebDriver (Chrome)

<a id="wymagania"></a>

## Wymagania wstępne 📋

* **Docker Desktop** (lub Docker Engine) + Docker Compose v2
* Klucz Riot Games API ([https://developer.riotgames.com/](https://developer.riotgames.com/))
* (Do E2E) obraz `selenium/standalone-chrome`

<a id="docker-start"></a>

## Uruchomienie (Docker) 🚀

1. **Sklonuj repozytorium**

   ```bash
   git clone https://github.com/Nossi201/Clash-Finder.git
   cd Clash-Finder
   ```

2. **Utwórz `.env` na podstawie przykładu**

   ```bash
   cp .env.example .env
   # uzupełnij RIOT_API_KEY, FLASK_SECRET_KEY itd.
   ```

3. **Start stosu**

   ```bash
   docker compose up -d --build
   ```

   Aplikacja dostępna pod: **[http://localhost:8080](http://localhost:8080)**

**Usługi**

* `nginx` – reverse proxy na porcie hosta `8080`
* `web` – aplikacja Flask (Gunicorn) na porcie kontenera `8000` (niepublikowany na hosta)
* `redis` – współdzielony cache (tylko wewnętrznie)

<a id="open-the-app"></a>

## Uruchom aplikację 🌐

* **Windows 10/11** (Docker Desktop): otwórz **[http://localhost:8080](http://localhost:8080)** w przeglądarce.
* **macOS / Linux**: otwórz **[http://localhost:8080](http://localhost:8080)**.

> Jeśli pojawi się błąd połączenia, sprawdź czy stack działa (`docker compose ps`) i czy port **8080** nie jest zajęty przez inny proces.

<a id="konfiguracja"></a>

## Konfiguracja ⚙️

* Aplikacja czyta ustawienia ze **zmiennych środowiskowych**:

  * `RIOT_API_KEY` – Twój klucz Riot API
  * `FLASK_SECRET_KEY` – sekret Flask (np. `python -c "import secrets; print(secrets.token_hex(32))"`)
  * `ALLOW_INSECURE_SSL` – domyślnie `0`; ustaw `1` wyłącznie w DEV, jeśli musisz tymczasowo wyłączyć weryfikację
  * `REDIS_URL` – domyślnie `redis://redis:6379/0`
  * `DEFAULT_CACHE_TTL` – domyślnie `60` (sekund)

**Polityka `.env`**

* **Nie commituj** `.env`; dodaj do repo **`.env.example`**.
* Po edycji `.env` odśwież kontenery:

  ```bash
  docker compose up -d --force-recreate
  # albo tylko web:
  docker compose up -d --no-deps --force-recreate web
  ```

<a id="dev-local"></a>

## Development lokalny (opcjonalnie)

Jeśli wolisz uruchamiać lokalnie bez Dockera:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # ustaw swoje klucze
python app.py
# otwórz http://127.0.0.1:5000
```

> Rekomendujemy Dockera dla zgodności ze środowiskiem produkcyjnym.

<a id="testy"></a>

## Testy 🧪

### Układ

Wszystkie pliki testowe znajdują się w **`test/`**:

* `docker-compose.tests.yml` – stack testowy (bez web/nginx/redis)
* `Dockerfile.tests` – obraz do uruchamiania testów
* `requirements-dev.txt` – zależności deweloperskie/testowe
* `pytest.ini`, `conftest.py` – konfiguracja pytest + patching Selenium
* `test/*.py` – testy jednostkowe/integracyjne
* `test/selenium/*.py` – testy E2E

### Jak to działa

* E2E korzystają z Chrome poprzez `selenium/standalone-chrome`.
* `conftest.py`:

  * przepisuje twarde `http://127.0.0.1:5000/...` na `BASE_URL` (domyślnie `http://host.docker.internal:8080`),
  * używa zdalnego WebDrivera, jeśli ustawiono `SELENIUM_REMOTE_URL`.

### Uruchamianie (Docker Desktop – klik)

1. Uruchom główny stack (ten z `docker-compose.yml`) → aplikacja na `:8080`.
2. Dodaj stack testowy: **Create → Start with Compose** → wskaż `test/docker-compose.tests.yml`.
3. Kliknij **Start** na:

   * `tests` (unit/integration),
   * `selenium`, a następnie `tests-e2e` (end‑to‑end).

### Uruchamianie (CLI)

Z **roota** włącz główny stack:

```bash
docker compose up -d
```

Z **test/** odpal testy:

```bash
# unit/integration
docker compose -f docker-compose.tests.yml run --rm tests

# e2e (Selenium może startować automatycznie albo uruchom go osobno)
docker compose -f docker-compose.tests.yml run --rm tests-e2e
```

<a id="struktura"></a>

## Struktura projektu 📁

```
Clash-Finder/
├── app.py
├── config.py
├── question.py
├── ssl_env_config.py
├── cache/
│   └── __init__.py
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── .dockerignore
├── .env.example
├── test/
│   ├── docker-compose.tests.yml
│   ├── Dockerfile.tests
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── conftest.py
│   ├── selenium/
│   │   └── test_*.py
│   └── test_*.py
└── README.md
```

<a id="api"></a>

## Endpointy API 🌐

> **Status:** część poniższych endpointów jest **nieaktywna/usunięta** i pozostaje jedynie jako informacja historyczna.

* `GET /` — strona główna
* `POST /Cheker` — wyszukiwanie gracza lub drużyny
* ~~`GET /clash_team/<summoner_name>/<server>`~~ — **nieaktywne/usunięte**
* ~~`GET /player_stats/<summoner_name>/<server>`~~ — **nieaktywne/usunięte**
* ~~`POST /load_more_matches`~~ — **nieaktywne/usunięte** (ładowanie kolejnych meczów)
* ~~`POST /api/resources/update`~~ — **nieaktywne/usunięte** (ręczna aktualizacja zasobów)
* ~~`GET /api/resources/version`~~ — **nieaktywne/usunięte** (aktualna wersja zasobów)
* ~~`POST /api/resources/force-update`~~ — **nieaktywne/usunięte** (wymuszenie aktualizacji)
* `GET /debug/check-static` — endpoint zdrowia/debug

<a id="roadmap"></a>

## Ograniczenia i plan rozwoju 🚧

**Aktualnie**

* Testy integracyjne/E2E mogą zależeć od żywego Riot API (limity, sieć).
* Brak skonfigurowanego CI.

<a id="license"></a>

## Licencja 📄

MIT — zobacz [LICENSE](LICENSE).

<a id="disclaimer"></a>

## Zastrzeżenia

Projekt nie jest sponsorowany ani wspierany przez Riot Games. League of Legends™ i Riot Games™ są znakami towarowymi Riot Games, Inc.
