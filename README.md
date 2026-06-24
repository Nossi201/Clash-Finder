# Clash Finder

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg) ![Flask](https://img.shields.io/badge/flask-v3.1+-green.svg) ![Selenium](https://img.shields.io/badge/selenium-v4.0+-orange.svg) ![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## Project Description

Clash Finder is a League of Legends web application built with Flask that lets players analyze match history, player statistics, and Clash team compositions. The project emphasizes software quality and modern QA practices — serving as a full-stack portfolio project demonstrating REST API integration, asynchronous request handling, and a layered test suite (unit, integration, end-to-end).

The application features:

* Detailed player and match statistics (KDA, CS, items, runes, win/loss)
* Automatic resource updates for champion icons, items, runes, and other game assets
* Multi-region support for all major League of Legends servers (NA, EUW, EUNE, KR, and more)
* Secure SSL/TLS communication
* Responsive design using Bootstrap 5

## Key Features

* **Player Statistics**: Detailed match history with pagination, including KDA, CS, control wards, kill participation, win/loss tracking
* **Clash Team Info**: View Clash team compositions and statistics
* **Auto-updating Resources**: Detects new patches and updates game assets every 24 hours; manual trigger available via API
* **Async Batch Requests**: Uses `aiohttp` + `asyncio` to fetch match data concurrently — the same pattern used in document ingestion pipelines
* **Responsive UI**: Clean, mobile-friendly interface built with Bootstrap 5
* **Caching & Rate Limiting**: Custom TTL cache, Flask-Limiter, and exponential backoff on Riot API errors
* **Comprehensive Testing**: Unit, integration, and end-to-end tests with 85%+ code coverage

## Table of Contents

* [Technologies](#technologies)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Screenshots](#screenshots)
* [API Endpoints](#api-endpoints)
* [Testing Strategy](#testing-strategy)
* [Project Structure](#project-structure)
* [Key QA Challenges](#key-qa-challenges)
* [AI-Driven Development](#ai-driven-development)
* [Known Limitations & Roadmap](#known-limitations--roadmap)
* [Quality Metrics](#quality-metrics)
* [License](#license)

## Technologies

* **Backend**: Python 3.8+, Flask 3.1+, aiohttp, asyncio, Requests
* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
* **Data & Assets**: Riot Games API (REST), Data Dragon API, Community Dragon API
* **Security**: SSL/TLS via certifi, Flask-Limiter, input validation
* **Caching**: Custom TTL cache + optional Redis
* **Automation**: `schedule` for background resource updates
* **Testing & QA**: pytest 9+, pytest-cov, pytest-mock, Selenium WebDriver

## Prerequisites

* Python 3.8 or higher
* pip (Python package manager)
* Riot Games API key (register at [https://developer.riotgames.com/](https://developer.riotgames.com/))
* Chrome/Chromium browser (for Selenium E2E tests)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Nossi201/Clash-Finder.git
   cd Clash-Finder
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install production dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install development & testing dependencies**:

   ```bash
   pip install -r requirements-dev.txt
   ```

## Configuration

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Fill in your values in `.env`:

   ```env
   FLASK_ENV=development
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   SECRET_KEY=your-secret-key   # generate with: python scripts/generate_secret_key.py
   RIOT_API_KEY=RGAPI-your-key-here
   LOG_LEVEL=INFO
   ```

## Usage

1. Run the application:

   ```bash
   python run.py
   ```

2. Open your browser at `http://localhost:5000`.

3. Enter a summoner name (e.g., `Faker#KR1`) and select a region.

4. Choose between:
   * **Player Stats**: View detailed match history
   * **Clash Team**: View Clash team information

## Screenshots

### Home Page

![Home Page](app/static/img/screenshoots/index.png)

### Player History

![Player History](app/static/img/screenshoots/Player%20History%201.png)

### Match Detail View

![Match Detail](app/static/img/screenshoots/Player%20History%202.png)

## API Endpoints

* `GET /` — Home page
* `POST /search` — Search player or team
* `GET /clash_team/<summoner_name>/<server>` — Clash team data
* `GET /player_stats/<summoner_name>/<server>` — Player match history
* `POST /load_more_matches` — Load additional matches (async)
* `POST /api/resources/update` — Manual resource update
* `GET /api/resources/version` — Current resource version
* `POST /api/resources/force-update` — Force resource update

## Testing Strategy

Tests are organized in three layers, each with a distinct purpose:

### 1. Unit Tests (`tests/unit/`)

* Business logic and data transformation (formatters, validators)
* Flask route handlers tested in isolation
* App initialization and configuration
* 25+ parametrized test cases

```bash
pytest tests/unit/ -v
```

### 2. Integration Tests (`tests/integration/`)

* Riot Games API client — verifies real HTTP responses, rate-limit handling, and error mapping
* Cache service — validates TTL expiry, LRU eviction, and thread safety

```bash
pytest tests/integration/ -v
```

### 3. End-to-End Tests (`tests/e2e/`) — Selenium

* `test_search_flow.py`: Search form, region selection, navigation
* Dynamic "load more matches" button behavior
* Expanding detailed match stats

```bash
pytest tests/e2e/ -v
```

**Run the full suite with coverage**:

```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Project Structure

```
clash-finder/
├── app/                        # Flask application package
│   ├── __init__.py             # App factory (create_app)
│   ├── template_filters.py     # Custom Jinja2 filters
│   ├── models/                 # Dataclass-based game models
│   ├── routes/                 # Flask blueprints (main, player, clash, errors)
│   ├── services/               # Business logic & external API clients
│   │   ├── riot_api.py         # High-level Riot API service
│   │   ├── api/                # Low-level HTTP client
│   │   ├── player_async.py     # Async batch match fetching
│   │   ├── cache.py            # Custom TTL cache
│   │   └── auto_updater.py     # Background resource updater
│   ├── utils/                  # Decorators, formatters, validators, helpers
│   ├── static/                 # CSS, JS, images
│   └── templates/              # Jinja2 HTML templates + components
│
├── config/                     # Configuration module
│   ├── base.py                 # Dev / Prod / Testing config classes
│   ├── game_constants.py       # LoL queue types, tiers, positions
│   └── logging_config.py       # Structured logging setup
│
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── unit/                   # Isolated unit tests
│   ├── integration/            # API & cache integration tests
│   └── e2e/                    # Selenium end-to-end tests
│
├── scripts/                    # Utility scripts (keygen, log check, resource update)
├── run.py                      # Application entry point
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Dev & testing dependencies
├── .env.example                # Environment variable template
└── pytest.ini                  # Pytest configuration
```

## Key QA Challenges Addressed

* **External REST API Testing**: Multi-region response validation, caching, rate-limit handling (429 → retry with backoff), and mocking in unit tests — directly transferable to testing LLM API integrations
* **Async Code Testing**: `pytest-asyncio` for testing `aiohttp`-based concurrent fetch pipelines
* **Dynamic UI Testing**: AJAX-loaded match cards, Selenium waits for DOM updates
* **Test Data Management**: Parametrized fixtures, isolated test configs, cleanup routines
* **Error Path Coverage**: 404, 429, 500 responses from Riot API fully exercised in integration tests

## AI-Driven Development

This project was built using AI-assisted development tools:

* **Claude Code** — used for architecture decisions, refactoring, and implementing the async batch request pipeline
* **ChatGPT / Claude** — prompt engineering for code generation and debugging complex async flows
* **GitHub Copilot** — inline completions during feature development

The workflow treats AI tools as junior pair-programmers: generating initial implementations, then reviewing and adapting output to project conventions.

## Known Limitations & Roadmap

### Current Limitations

* Integration tests hit the real Riot API (no mock server yet)
* No CI/CD pipeline
* No performance testing suite

### Roadmap

* [ ] GitHub Actions CI/CD pipeline
* [ ] API mocking with `pytest-mock` / `responses` for offline integration tests
* [ ] Performance testing with Locust
* [ ] Docker containerization
* [ ] AI-powered player insights (LLM integration experiment)
* [ ] Vector search for champion recommendations (RAG prototype)
* [ ] API documentation with Swagger / OpenAPI

## Quality Metrics

* **Unit Test Coverage**: 95% of core functions
* **Code Coverage**: 85%+ (target: 90%+)
* **E2E Flows**: 3 main user journeys automated
* **Performance**: <2s home page load

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Not endorsed by Riot Games. League of Legends™ and Riot Games™ are trademarks of Riot Games, Inc.*
