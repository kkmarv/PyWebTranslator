import os

from abc import ABC
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EService
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver import (
    Edge as EdgeDriver, EdgeOptions,
    Firefox as FirefoxDriver, FirefoxOptions
)

WEBDRIVER_EXEC_DIR = os.path.normpath(r'./.webdrivers')
SERVICE_LOG_DIR = os.path.normpath(f'{WEBDRIVER_EXEC_DIR}/logs/')

# WebDriver manager environ vars
os.environ['WDM_LOG_LEVEL'] = '0'  # disable console logs
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'  # disable blank line printed to console

# create WebDriver directories
if not os.path.exists(WEBDRIVER_EXEC_DIR):
    os.mkdir(WEBDRIVER_EXEC_DIR)
    os.mkdir(SERVICE_LOG_DIR)
elif not os.path.exists(SERVICE_LOG_DIR):
    os.mkdir(SERVICE_LOG_DIR)


class Browser(ABC):
    """Abstract superclass for browsers. Use a specific Browser class to instantiate a browser session."""

    def __init__(self, driver: webdriver):
        """
        :param driver: Which driver to use
        """
        self.__driver: webdriver = driver
        self.__driver.set_window_size(1920, 1080)  # at this size, every button used is inside the viewport

    def get(self, url: str):
        """Calls an URL in the browser."""
        self.driver.get(url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # properly quit the driver and close the browser window
        self.__driver.close()
        self.__driver.quit()

    @property
    def driver(self):
        return self.__driver


class Firefox(Browser):
    def __init__(self, is_headless=True):
        """Creates a Firefox browser session.

        :param is_headless: Whether the browser should run in the background (without GUI).
        """

        # prepare WebDriver options
        driver_options: FirefoxOptions = FirefoxOptions()
        driver_options.headless = is_headless

        # create a selenium WebDriver
        firefox_driver: FirefoxDriver = webdriver.Firefox(
            service=FFService(
                log_path=f'{SERVICE_LOG_DIR}/geckodriver.log',
                executable_path=GeckoDriverManager(path=WEBDRIVER_EXEC_DIR).install()),  # install the WebDriver
            options=driver_options
        )

        super().__init__(firefox_driver)


class Edge(Browser):
    def __init__(self, is_headless=True):
        """Creates an Edge browser session.

        :param is_headless: Whether the browser should run in the background (without GUI).
        """

        # prepare WebDriver options
        driver_options: EdgeOptions = EdgeOptions()
        driver_options.use_chromium = True

        if is_headless:
            driver_options.add_argument('is_headless')
            driver_options.add_argument('disable-gpu')

        # create a selenium WebDriver
        edge_driver: EdgeDriver = EdgeDriver(
            service=EService(
                log_path=f'{SERVICE_LOG_DIR}/msedgedriver.log',
                executable_path=EdgeChromiumDriverManager(path=WEBDRIVER_EXEC_DIR).install()  # install the WebDriver
            ),
            options=driver_options
        )

        super().__init__(edge_driver)
