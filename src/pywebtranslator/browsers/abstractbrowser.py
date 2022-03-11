import os

from abc import ABC
from selenium.webdriver.remote.webdriver import WebDriver


WEBDRIVER_DIR = os.path.abspath(os.path.normpath(r'.webdriver/'))
SERVICE_LOG_DIR = os.path.join(WEBDRIVER_DIR, 'logs/')

# WebDriverManager environment variables
os.environ['WDM_LOG_LEVEL'] = '0'  # disable console logs
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'  # disable blank line printed to console

# create WebDriver directories
if not os.path.exists(WEBDRIVER_DIR):
    os.mkdir(WEBDRIVER_DIR)
    os.mkdir(SERVICE_LOG_DIR)
elif not os.path.exists(SERVICE_LOG_DIR):
    os.mkdir(SERVICE_LOG_DIR)


class AbstractBrowser(ABC):
    def __init__(self, driver: WebDriver):
        """Abstract superclass for browsers. Use a specific Browser class to instantiate a browser session.

        :param driver: Which driver to use"""
        self.__driver: WebDriver = driver
        self.__driver.set_window_size(1920, 1080)  # at this size, every button used is inside the viewport

    def get(self, url: str) -> None:
        """Calls given URL in this browser."""
        self.driver.get(url)

    @property
    def driver(self) -> WebDriver:
        return self.__driver
