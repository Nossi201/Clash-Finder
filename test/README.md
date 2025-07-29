# 🧪 Test Suite – Clash Finder

A comprehensive suite of automated tests for the Clash Finder application, showcasing modern QA practices.

## 📂 Test Structure

```
test/
├── README.md                            # This file
├── test_app.py                          # Unit tests
├── test_question.py                     # API integration tests
└── selenium/                            # End-to-End tests
    ├── test_testSearchBar.py            # Search bar tests
    ├── test_testButtonShowMoreMatches.py# Dynamic loading tests
    └── test_testCheckMoreStats.py       # Stats expansion tests
```

## 🎯 Test Types

### 1. **Unit Tests** (`test_app.py`)

**Purpose:** Validate helper functions and core business logic.

**Coverage:**

* `parse_summoner_name()` – parsing summoner names (20+ cases)
* `slugify_server()` / `unslugify_server()` – URL conversion for servers
* Edge-case handling and input validation

**Example test:**

```python
@pytest.mark.parametrize("summoner_name,expected_name,expected_tag", [
    ("PlayerName#TAG1", "PlayerName", "TAG1"),
    ("Hide on bush#KR", "Hide on bush", "KR"),
    ("Player With Spaces", "Player With Spaces", ""),
])
def test_parse_summoner_name(summoner_name, expected_name, expected_tag):
    # Test implementation
```

**Run:**

```bash
pytest test/test_app.py -v
pytest test/test_app.py::TestParseSummonerName -v  # Specific test class
```

### 2. **Integration Tests** (`test_question.py`)

**Purpose:** Verify integration with the external Riot Games API.

**Coverage:**

* Riot Games API communication
* Error and rate-limit handling
* Asynchronous functions
* JSON response validation

**Key tests:**

* `test_get_account_info_by_puuid()` – fetch account data
* `test_get_summoner_info_puuid()` – fetch summoner info
* `test_display_matches_async_behavior()` – async match retrieval
* `test_show_players_team_async_performance()` – async performance

**Requirements:**

* Active Riot API key in `config.py`
* Internet connection
* Valid test PUUID

**Run:**

```bash
# Requires Riot API key
pytest test/test_question.py -v
pytest test/test_question.py -k "async" -v  # Only async tests
```

### 3. **End-to-End Tests (Selenium)** (`selenium/`)

**Purpose:** Test full user flows in the browser.

#### `test_testSearchBar.py`

**Scenario:** Player search workflow

```python
def test_testSearchBar(self):
    # 1. Navigate to home page
    # 2. Select server from dropdown
    # 3. Enter summoner name
    # 4. Click search button
    # 5. Verify redirection
```

#### `test_testButtonShowMoreMatches.py`

**Scenario:** Dynamic loading of additional matches

```python
def test_show_more_matches(self):
    # 1. Open player match history
    # 2. Click “Show more”
    # 3. Confirm match count increases
    # 4. Verify new data loads
```

#### `test_testCheckMoreStats.py`

**Scenario:** Expanding detailed stats

```python
def test_testCheckMoreStats(self):
    # 1. Open player match history
    # 2. Click “Show Stats” on a match
    # 3. Verify details appear
    # 4. Test collapse/expand behavior
```

**Requirements:**

* Chrome/Chromium browser
* ChromeDriver in PATH
* App running on `localhost:5000`

**Run:**

```bash
# First, start the app:
python app.py

# In another terminal:
pytest test/selenium/ -v
pytest test/selenium/test_testSearchBar.py -v  # Single test
```

## 🚀 Quick Start

### 1. **Set up environment**

```bash
# Install dependencies
pip install pytest selenium pytest-asyncio

# Verify installation
pytest --version
```

### 2. **Run all tests**

```bash
# Unit tests (no API/app required)
pytest test/test_app.py -v

# Integration tests (requires API key)
pytest test/test_question.py -v

# E2E tests (requires running app)
python app.py &  # Run in background
pytest test/selenium/ -v
```

### 3. **Generate coverage report**

```bash
pip install pytest-cov
pytest test/ --cov=. --cov-report=html
# Report available at htmlcov/index.html
```

## 🔧 Test Configuration

### `pytest.ini` (in project root)

```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: time-consuming tests
    api: tests requiring API
    selenium: Selenium E2E tests
```

### Environment Variables

```bash
# For API tests
export RIOT_API_KEY="your_api_key_here"

# For Selenium tests
export SELENIUM_TIMEOUT=10
export SELENIUM_BROWSER=chrome
```

## 📊 Testing Strategy

### **Test Pyramid**

1. **Unit tests (70%)** – fast, isolated
2. **Integration tests (20%)** – component cooperation
3. **E2E tests (10%)** – critical user paths

### **Test Case Categories**

* **Positive (Happy Path):**

  * Valid player search
  * Correct match display
  * Stats expansion

* **Negative (Error Handling):**

  * Invalid summoner names
  * API errors (404, 403, 429)
  * No internet connection

* **Edge Cases:**

  * Very long names
  * Special characters
  * Empty results

## 🐛 Debugging

### 1. Selenium tests failing

```bash
# Check app is running:
curl http://localhost:5000

# Check ChromeDriver:
chromedriver --version

# Add explicit waits in tests:
from selenium.webdriver.support.ui import WebDriverWait
```

### 2. API tests failing

```bash
# Verify API key:
grep RIOT_API_KEY config.py

# Check rate limits:
# Dev key: 100 requests / 2 minutes
```

### 3. Async tests issues

```python
# Use pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## 📈 Metrics & Reporting

* **Coverage:** target ≥ 85%
* **Runtime:** < 5 minutes for full suite
* **Flakiness:** < 1%

**Reports available:**

```bash
# HTML coverage:
pytest --cov=. --cov-report=html

# JUnit XML:
pytest --junitxml=test-results.xml

# Detailed output:
pytest -v --tb=long
```

## 🔄 CI/CD Integration (example)

### GitHub Actions workflow

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest test/test_app.py
      - name: Run integration tests
        run: pytest test/test_question.py
        env:
          RIOT_API_KEY: ${{ secrets.RIOT_API_KEY }}
```

## 🤝 Collaboration

### Adding new tests

1. Create a branch: `feature/new-test-functionality`
2. Add tests following naming conventions
3. Ensure coverage does not decrease
4. Update documentation
5. Open a PR describing new test cases

### Reporting test bugs

1. Verify reproducibility
2. Add a test reproducing the issue
3. Mark test with `pytest.mark.xfail` and rationale
4. Create an issue tagged `bug`

---

> **Note:** Tests may occasionally fail due to API rate limits or external service changes—this is normal when testing against third-party APIs.
