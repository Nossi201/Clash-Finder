<!-- path: README.md -->

# Clash Finder 🎮

![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3%2B-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)
![Selenium](https://img.shields.io/badge/selenium-4%2B-orange.svg)
![Tests](https://img.shields.io/badge/tests-green.svg)

## Project Description 📋

Clash Finder is a League of Legends web application built with Flask. It lets players analyze statistics and view detailed match history. The project emphasizes code quality, caching, and automated tests (unit, integration, and end-to-end).

**Containerized** with a minimal production-style stack:

```
Internet → NGINX → Flask (Gunicorn) ↔ Redis
                     ↘ Riot API
```

**Ephemeral** containers (started only when needed): test runners and Selenium (Chrome).

## Key Features ✨

* **Player Statistics & History** (KDA, CS, KP, win/loss, items, runes)
* **Responsive UI** (Bootstrap 5)
* **Async fetching** for batched requests
* **Caching** with Redis (shared across workers)
* **Secure HTTPS verification** via `certifi`
* **Automated tests**: unit/integration and E2E (Selenium)

## Table of Contents

* [Technologies](#technologies)
* [Prerequisites](#prerequisites)
* [Quick Start (Docker)](#quick-start-docker)
* [Open the app](#open-the-app)
* [Configuration](#configuration)
* [Local Development (optional)](#local-development-optional)
* [Testing](#testing)
* [Project Structure](#project-structure)
* [API Endpoints](#api-endpoints)
* [Known Limitations & Roadmap](#known-limitations--roadmap)
* [License](#license)
* [Disclaimer](#disclaimer)

<a id="technologies"></a>

## Technologies 🛠️

* **Backend**: Python 3.12, Flask, aiohttp/asyncio, Requests, Gunicorn
* **Reverse Proxy**: NGINX
* **Cache**: Redis
* **Frontend**: HTML5, CSS3, JS (ES6+), Bootstrap 5
* **Security**: SSL/TLS verification via `certifi`
* **Testing**: pytest, Selenium WebDriver (Chrome)

<a id="prerequisites"></a>

## Prerequisites 📋

* **Docker Desktop** (or Docker Engine) + Docker Compose v2
* Riot Games API key ([https://developer.riotgames.com/](https://developer.riotgames.com/))
* (For E2E) Chrome via `selenium/standalone-chrome` image

<a id="quick-start-docker"></a>

## Quick Start (Docker) 🚀

1. **Clone the repo**

   ```bash
   git clone https://github.com/Nossi201/Clash-Finder.git
   cd Clash-Finder
   ```

2. **Create `.env` from example**

   ```bash
   cp .env.example .env
   # fill in RIOT_API_KEY, FLASK_SECRET_KEY, etc.
   ```

3. **Start the stack**

   ```bash
   docker compose up -d --build
   ```

   App will be available at: **[http://localhost:8080](http://localhost:8080)**

**Services**

* `nginx` – reverse proxy on host port `8080`
* `web` – Flask app (Gunicorn) on container port `8000` (not published to host)
* `redis` – shared cache (internal only)

<a id="open-the-app"></a>

## Open the app 🌐

* **Windows 10/11** (Docker Desktop): open **[http://localhost:8080](http://localhost:8080)** in your browser.
* **macOS / Linux**: open **[http://localhost:8080](http://localhost:8080)**.

> If you see a connection error, ensure the stack is running (`docker compose ps`) and that port **8080** isn’t used by another process.

<a id="configuration"></a>

## Configuration ⚙️

* Application reads settings from **environment variables**:

  * `RIOT_API_KEY` – your Riot API key
  * `FLASK_SECRET_KEY` – Flask secret (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
  * `ALLOW_INSECURE_SSL` – `0` by default; set `1` only in local DEV if you must disable verification
  * `REDIS_URL` – default `redis://redis:6379/0`
  * `DEFAULT_CACHE_TTL` – default `60` (seconds)

**.env policy**

* Do **not** commit `.env`; commit `.env.example` instead.
* Update containers after editing `.env`:

  ```bash
  docker compose up -d --force-recreate
  # or only web:
  docker compose up -d --no-deps --force-recreate web
  ```

<a id="local-development-optional"></a>

## Local Development (optional)

If you prefer to run locally without Docker:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # set your keys
python app.py
# open http://127.0.0.1:5000
```

> Docker remains the recommended way for parity with production-like settings.

<a id="testing"></a>

## Testing 🧪

### Layout

All test-related files live under **`test/`**:

* `docker-compose.tests.yml` – test stack (no web/nginx/redis here)
* `Dockerfile.tests` – image for running tests
* `requirements-dev.txt` – dev/test dependencies
* `pytest.ini`, `conftest.py` – pytest config and Selenium patching
* `test/*.py` – unit/integration tests
* `test/selenium/*.py` – E2E tests

### How it works

* E2E tests run Chrome via `selenium/standalone-chrome`.
* `conftest.py`:

  * rewrites hardcoded `http://127.0.0.1:5000/...` to `BASE_URL` (default `http://host.docker.internal:8080`);
  * uses remote WebDriver if `SELENIUM_REMOTE_URL` is set.

### Run with Docker Desktop (UI)

1. Start main stack (this repo’s `docker-compose.yml`) → app on `:8080`.
2. Add test stack: **Create → Start with Compose** → choose `test/docker-compose.tests.yml`.
3. Click **Start** on:

   * `tests` (unit/integration),
   * `selenium` then `tests-e2e` (end-to-end).

### Run with CLI

From **root** start main stack:

```bash
docker compose up -d
```

From **test/** run tests:

```bash
# unit/integration
docker compose -f docker-compose.tests.yml run --rm tests

# e2e (Selenium starts via depends_on or start it manually)
docker compose -f docker-compose.tests.yml run --rm tests-e2e
```

<a id="project-structure"></a>

## Project Structure 📁

```
Clash-Finder/
├── app.py
├── config.py
├── question.py
├── ssl_env_config.py
├── cache/                     # cache package (Redis helpers)
│   └── __init__.py
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── .dockerignore
├── .env.example               # sample env (no secrets)
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

<a id="api-endpoints"></a>

## API Endpoints 🌐

> **Status:** Some endpoints below are inactive/removed and kept for historical reference.

* `GET /` — Home page
* `POST /Cheker` — Search player or team
* ~~`GET /clash_team/<summoner_name>/<server>`~~ — **inactive/removed**
* ~~`GET /player_stats/<summoner_name>/<server>`~~ — **inactive/removed**
* ~~`POST /load_more_matches`~~ — **inactive/removed** (Load additional matches)
* ~~`POST /api/resources/update`~~ — **inactive/removed** (Manual resource update)
* ~~`GET /api/resources/version`~~ — **inactive/removed** (Current resource version)
* ~~`POST /api/resources/force-update`~~ — **inactive/removed** (Force resource update)
* `GET /debug/check-static` — health/debug endpoint

<a id="known-limitations--roadmap"></a>

## Known Limitations & Roadmap 🚧

**Current**

* Integration/E2E tests may depend on live Riot API (rate limits, network).
* No CI configured yet.


<a id="license"></a>

## License 📄

MIT — see [LICENSE](LICENSE).

<a id="disclaimer"></a>

## Disclaimer

Not endorsed by Riot Games. League of Legends™ and Riot Games™ are trademarks of Riot Games, Inc.
