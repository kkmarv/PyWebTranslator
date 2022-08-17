import os
from abc import ABC

from selenium.webdriver import Edge as EdgeDriver, EdgeOptions
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EService
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import (
    visibility_of_element_located,
    visibility_of_all_elements_located
)
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

WEBDRIVER_DIR = os.path.abspath(os.path.normpath(r'.webdriver/'))
SERVICE_LOG_DIR = os.path.join(WEBDRIVER_DIR, 'logs/')

# WebDriverManager environment variables
os.environ['WDM_LOG_LEVEL'] = '0'  # disable console logs
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'  # disable blank line printed to console

# create WebDriver directories
if not os.path.exists(WEBDRIVER_DIR):
    os.mkdir(WEBDRIVER_DIR)
    os.mkdir(SERVICE_LOG_DIR)
if not os.path.exists(SERVICE_LOG_DIR):
    os.mkdir(SERVICE_LOG_DIR)


class Driver(ABC):
    def __init__(self, driver: WebDriver):
        """Abstract superclass for browsers. Use a specific Browser class to instantiate a browser session.

        :param driver: Which driver to use"""
        self._driver: WebDriver = driver
        self._wait_for_webelem: WebDriverWait = WebDriverWait(self._driver, 5)
        self._driver.set_window_size(1920, 1080)  # at this size, every button used is inside the viewport

    def __del__(self):
        self._driver.quit()

    def get(self, url: str) -> None:
        """Calls given URL in this browser."""
        self.driver.get(url)

    def click_elem(self, css_path) -> None:
        """Tries to find and click an element."""
        self.search_elem(css_path).click()

    def search_elem(self, css_path: str) -> WebElement:
        """
        Searches with a CSS selector for a single element in the HTML DOM
        and returns the corresponding element if found.
        """
        return self._wait_for_webelem.until(
            visibility_of_element_located((By.CSS_SELECTOR, css_path)),
            f'Path {css_path} not found.'
        )

    def search_elems(self, css_path: str) -> list[WebElement]:
        """
        Searches with a CSS selector for multiple elements in the HTML DOM
        and returns the corresponding elements if found.
        """
        return self._wait_for_webelem.until(
            visibility_of_all_elements_located((By.CSS_SELECTOR, css_path)),
            f'Path {css_path} not found.'
        )

    @property
    def driver(self) -> WebDriver:
        return self._driver


class Edge(Driver):
    def __init__(self, is_headless=True):
        """Creates an Edge browser session.

        :param is_headless: Whether the browser should run in the background (without GUI)."""

        # prepare WebDriver options
        driver_options: EdgeOptions = EdgeOptions()
        driver_options.use_chromium = True

        if is_headless:
            driver_options.add_argument('is_headless')
            driver_options.add_argument('disable-gpu')

        # create a selenium WebDriver
        edge_driver: EdgeDriver = EdgeDriver(
            service=EService(
                log_path=os.path.normpath(os.path.join(SERVICE_LOG_DIR, 'msedgedriver.log')),
                executable_path=EdgeChromiumDriverManager(path=WEBDRIVER_DIR, cache_valid_range=7).install()
            ),
            options=driver_options
        )

        super().__init__(edge_driver)


class Firefox(Driver):
    def __init__(self, is_headless=True):
        """Creates a Firefox browser session.

        :param is_headless: Whether the browser should run in the background (without GUI)."""

        # prepare WebDriver options
        driver_options: FirefoxOptions = FirefoxOptions()
        driver_options.headless = is_headless  # use this, without it threads are not working!

        # create a selenium WebDriver
        firefox_driver: FirefoxDriver = FirefoxDriver(
            service=FFService(
                log_path=os.path.normpath(os.path.join(SERVICE_LOG_DIR, 'geckodriver.log')),
                executable_path=GeckoDriverManager(path=WEBDRIVER_DIR, cache_valid_range=7).install()),
            options=driver_options
        )

        super().__init__(firefox_driver)
