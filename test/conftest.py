# test/conftest.py
# Session-scoped patches for Selenium and BASE_URL rewrite (no ScopeMismatch).
import os
import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

@pytest.fixture(scope="session", autouse=True)
def _session_patches():
    mp = pytest.MonkeyPatch()

    # Use remote driver if provided (our selenium container), else local
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    def _mk_driver(*args, **kwargs):
        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        if remote_url:
            return webdriver.Remote(command_executor=remote_url, options=opts)
        return webdriver.Chrome(options=opts)
    mp.setattr(webdriver, "Chrome", _mk_driver)

    # Rewrite hardcoded localhost:5000 to BASE_URL (for all driver.get calls)
    base = os.getenv("BASE_URL", "http://host.docker.internal:8080").rstrip("/")
    orig_get = RemoteWebDriver.get
    def patched_get(self, url):
        prefix = "http://127.0.0.1:5000"
        if isinstance(url, str) and url.startswith(prefix):
            url = base + url[len(prefix):]
        return orig_get(self, url)
    mp.setattr(RemoteWebDriver, "get", patched_get)

    yield
    mp.undo()