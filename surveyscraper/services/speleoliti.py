"""Speleoliti Online (https://speleoliti.speleo.net) Selenium driver.

Automates upload of the survey JSON, identifies the highest-elevation station
as a default fixed point, retrieves cave dimensions (polygon/horizontal length,
elevation, depth), and updates the fixed station back on the page.

XPath selectors are collected as module-level constants — when Speleoliti
changes its DOM, the fragile-string surface area is here, not scattered.
"""
from __future__ import annotations

# Explicit submodule imports (rather than `from selenium import webdriver` and
# `webdriver.Chrome` / `webdriver.ChromeOptions`) so PyInstaller's static
# analysis bundles the chrome.options / chrome.webdriver modules. Modern
# selenium resolves those names via a lazy `__getattr__` at runtime, which the
# bundled exe cannot see.
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from surveyscraper.core.errors import SpeleolitiError
from surveyscraper.logging_setup import get_logger

URL = "https://speleoliti.speleo.net/online/app_en.html"

XPATH_DEF_OPT2 = '//*[@id="DefOpt2"]'
XPATH_FILE_RADIO = '//*[@id="impexRadio_file"]'
XPATH_FILE_INPUT = '//*[@id="UploadFileFld"]'
XPATH_IMPORT_CONFIRM = '//*[@id="impex"]/table/tbody/tr/td/div/input'
XPATH_TABLE99_ROW = '//*[@id="table99"]/tbody/tr[{row}]/td[2]'
XPATH_ICO_COORDS = '//*[@id="ico_coords"]'
XPATH_ICO_MAIN = '//*[@id="ico_main"]'
XPATH_ICO_SURVEY = '//*[@id="ico_survey"]'
XPATH_TABLE2B = '//*[@id="table2b"]/tbody'
XPATH_TABLE2B_STATION = '//*[@id="table2b"]/tbody/tr[{row}]/td[1]'
XPATH_TABLE2B_ALT = '//*[@id="table2b"]/tbody/tr[{row}]/td[4]/div'
XPATH_SURVEY_FIX = '//*[@id="survey_fix"]'

# table99 rows for the four reported dimensions
ROW_POLY_LENGTH = 4
ROW_HOR_LENGTH = 5
ROW_ELEVATION = 6
ROW_DEPTH = 7

_log = get_logger("speleoliti")


class SpeleolitiOnline:
    """Wrap a Selenium-driven Speleoliti session.

    The `online` attribute is False when ChromeDriver could not start (e.g.
    no internet); callers should check it before invoking other methods. All
    other operations raise `SpeleolitiError` on failure.
    """

    def __init__(self, *, headless: bool, survey_path: str) -> None:
        self.online = True
        self.driver: Chrome | None = None
        self.headless = headless
        self.survey_path = survey_path
        self.url = URL

        try:
            driver_path = ChromeDriverManager().install()
            options = ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument("--log-level=0")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-logging")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            if headless:
                options.add_argument("--headless=new")
            service = Service(driver_path)
            self.driver = Chrome(service=service, options=options)
            if not headless:
                self.driver.minimize_window()
                self.handle_of_the_window = self.driver.current_window_handle
        except Exception as e:
            _log.exception("Failed to initialize ChromeDriver")
            self.online = False
            self._init_error = e
            if self.driver is not None:
                try:
                    self.driver.quit()
                except Exception:
                    pass

    @property
    def init_error(self) -> Exception | None:
        return getattr(self, "_init_error", None)

    def open_empty_object(self) -> None:
        assert self.driver is not None
        self.driver.get(self.url)

    def _dismiss_alert_if_present(self, timeout: float = 5.0) -> bool:
        """Accept any pending JS alert. Returns True if one was dismissed.

        A pending alert blocks every other interaction with `ElementNotInteractable`,
        so each public method calls this defensively before doing anything else.
        """
        assert self.driver is not None
        try:
            WebDriverWait(self.driver, timeout).until(expected_conditions.alert_is_present())
            text = self.driver.switch_to.alert.text
            self.driver.switch_to.alert.accept()
            _log.info("Dismissed Speleoliti alert: %s", text)
            return True
        except Exception:
            return False

    def open_object(self) -> None:
        assert self.driver is not None
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 3).until(
                expected_conditions.element_to_be_clickable((By.XPATH, XPATH_DEF_OPT2))
            ).click()
            self.driver.find_element(By.XPATH, XPATH_FILE_RADIO).click()
            file_input = self.driver.find_element(By.XPATH, XPATH_FILE_INPUT)
            file_input.send_keys(self.survey_path)
            self.driver.find_element(By.XPATH, XPATH_IMPORT_CONFIRM).click()
        except Exception as e:
            _log.exception("Failed to open object on Speleoliti")
            raise SpeleolitiError(f"Failed to open object: {e}") from e
        # Wait up to 30 s for the import-completion alert; absent alert is fine.
        # Subsequent methods also dismiss defensively in case this misses.
        self._dismiss_alert_if_present(timeout=30.0)

    def retrieve_cave_data(self) -> tuple[str, str, str, str]:
        assert self.driver is not None
        self._dismiss_alert_if_present(timeout=2.0)
        try:
            poly = self.driver.find_element(By.XPATH, XPATH_TABLE99_ROW.format(row=ROW_POLY_LENGTH)).text.split()[0]
            horiz = self.driver.find_element(By.XPATH, XPATH_TABLE99_ROW.format(row=ROW_HOR_LENGTH)).text.split()[0]
            elev = self.driver.find_element(By.XPATH, XPATH_TABLE99_ROW.format(row=ROW_ELEVATION)).text.split()[0]
            depth = self.driver.find_element(By.XPATH, XPATH_TABLE99_ROW.format(row=ROW_DEPTH)).text.split()[0]
            return poly, horiz, elev, depth
        except Exception as e:
            _log.exception("Failed to retrieve cave data")
            raise SpeleolitiError(f"Failed to retrieve cave data: {e}") from e

    def find_highest_point(self) -> str:
        assert self.driver is not None
        self._dismiss_alert_if_present(timeout=3.0)
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, XPATH_ICO_COORDS))
            ).click()
            data_tbl = self.driver.find_element(By.XPATH, XPATH_TABLE2B)
            station_alts: dict[str, float] = {}
            for index, row in enumerate(data_tbl.find_elements(By.XPATH, ".//tr")):
                if index == 0:
                    continue
                station = row.find_element(By.XPATH, XPATH_TABLE2B_STATION.format(row=index + 1)).text
                alt = row.find_element(By.XPATH, XPATH_TABLE2B_ALT.format(row=index + 1)).text
                station_alts[station] = float(alt)
            self.driver.find_element(By.XPATH, XPATH_ICO_MAIN).click()
            return max(station_alts, key=station_alts.get)
        except Exception as e:
            _log.exception("Failed to find highest point")
            raise SpeleolitiError(f"Failed to find highest point: {e}") from e

    def update_fixed_station(self, fixed_station: str) -> None:
        assert self.driver is not None
        self._dismiss_alert_if_present(timeout=3.0)
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, XPATH_ICO_SURVEY))
            ).click()
            element = WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, XPATH_SURVEY_FIX))
            )
            self.driver.execute_script('arguments[0].value = ""', element)
            element.click()
            element.send_keys(fixed_station)
            self.driver.find_element(By.XPATH, XPATH_ICO_MAIN).click()
        except Exception as e:
            _log.exception("Failed to update fixed station")
            raise SpeleolitiError(f"Failed to update fixed station: {e}") from e

    def restore_window(self) -> None:
        assert self.driver is not None
        self.driver.switch_to.window(self.handle_of_the_window)
        self.driver.set_window_rect(0, 0)

    def close_driver(self) -> None:
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
