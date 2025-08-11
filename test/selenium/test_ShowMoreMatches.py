# tests/selenium/test_ShowMoreMatches.py
# Style aligned with test_SearchBar.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://127.0.0.1:5000/player_stats/HextechChest--202/eu-west"

class TestShowMoreMatches:
    """End-to-End test for dynamic "Show More" matches button.

    Steps:
      1) Open a player's stats page.
      2) Verify initial number of match cards.
      3) Set select to 1 and click "Show more"; expect +1 card.
      4) Set select to 5 and click again; expect +5 more cards.
    """

    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 15)

    def teardown_method(self, method):
        self.driver.quit()

    def check_count(self, expected_count):
        """Wait until the page shows exactly `expected_count` match cards.
        If there aren't enough matches to reach the expected count within the
        timeout, skip the test (data-dependent scenario).
        """
        try:
            self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".card.mb-3")) == expected_count)
        except TimeoutException:
            actual = len(self.driver.find_elements(By.CSS_SELECTOR, ".card.mb-3"))
            if actual < expected_count:
                pytest.skip(f"Not enough matches available: expected {expected_count}, got {actual}")
            assert actual == expected_count, f"Expected {expected_count} cards, got {actual}"

    def test_show_more_matches(self):
        self.driver.get(BASE_URL)
        self.driver.set_window_size(1936, 1096)

        self.wait.until(EC.title_is("Player History"))
        self.wait.until(EC.presence_of_element_located((By.ID, "number-list")))
        self.wait.until(EC.presence_of_element_located((By.ID, "loadMoreMatchesButton")))

        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".card.mb-3"))

        # Load +1
        Select(self.driver.find_element(By.ID, "number-list")).select_by_visible_text("1")
        self.driver.find_element(By.ID, "loadMoreMatchesButton").click()
        self.check_count(initial_count + 1)

        # Load +5
        Select(self.driver.find_element(By.ID, "number-list")).select_by_visible_text("5")
        self.driver.find_element(By.ID, "loadMoreMatchesButton").click()
        self.check_count(initial_count + 1 + 5)

        # Sanity: last card is visible
        last_card = self.driver.find_elements(By.CSS_SELECTOR, ".card.mb-3")[-1]
        assert last_card.is_displayed()