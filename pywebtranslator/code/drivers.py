import os
from abc import ABC, abstractmethod
from typing import Optional

from selenium.webdriver import Edge as EdgeDriver, EdgeOptions, Keys
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

WEBDRIVER_DIR = os.path.abspath(os.path.normpath(r'../.webdriver/'))
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
    @abstractmethod  # used to indicate to isabstract() that the Driver class is abstract
    def __init__(self, driver: WebDriver):
        """Abstract superclass for selenium web drivers. Use a specific driver class to instantiate a driver session.

        :param driver: Which driver to use"""

        self._driver = driver
        self._wait_for_elem: WebDriverWait = WebDriverWait(self._driver, 5)

        self._url: Optional[str] = None
        self._main_window_handle: Optional[str] = None  # main tab which gets created upon calling set_url()

    def __del__(self):
        self._driver.quit()

    def set_url(self, url: str) -> None:
        """Creates a new tab and calls given URL in this driver.

        :param url: The URL to call"""
        self._driver.get(url)
        self._url = url
        self._main_window_handle = self._driver.current_window_handle

    def click_elem(self, css_path: str) -> None:
        """Tries to find and click an element by hitting enter on it.
        This way, it works even if the element is visibly obstructed.

        :param css_path: CSS selector for the element."""
        self.search_elem(css_path).send_keys(Keys.RETURN)

    def search_elem(self, css_path: str) -> WebElement:
        """Searches with a CSS selector for a single element in the HTML DOM
        and returns the corresponding element if found.

        :param css_path: A CSS selector for a single element.
        :return: The corresponding selenium WebElement, if found."""
        return self._wait_for_elem.until(
            visibility_of_element_located((By.CSS_SELECTOR, css_path)),
            f'Path {css_path} not found.'
        )

    def search_elems(self, css_path: str) -> list[WebElement]:
        """Searches with a CSS selector for multiple elements in the HTML DOM
        and returns the corresponding elements if found.

        :param css_path: A css selector for selecting more than one element.
        :return: The corresponding list of selenium WebElements, if found."""
        return self._wait_for_elem.until(
            visibility_of_all_elements_located((By.CSS_SELECTOR, css_path)),
            f'Path {css_path} not found.'
        )

    def discard_tabs(self):
        """Closes all tabs in the current session except the main tab set through set_url().
        Especially useful if in a longer lasting session multiple tabs were opened that need to be cleaned up."""
        for window in self._driver.window_handles:
            self._driver.switch_to.window(window)
            if self._driver.current_window_handle != self._main_window_handle:
                self._driver.close()

        self._driver.switch_to.window(self._main_window_handle)  # switch back to main tab

    @property
    def driver(self) -> WebDriver:
        return self._driver


class Edge(Driver):
    """https://www.microsoft.com/en-us/edge"""

    def __init__(self, is_headless=True):
        """Creates an Edge session.

        :param is_headless: Whether the driver should run headless (without GUI)."""

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
    """https://www.mozilla.org/en-GB/firefox/new/"""

    def __init__(self, is_headless=True):
        """Creates a Firefox session.

        :param is_headless: Whether the driver should run headless (without GUI)."""

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
