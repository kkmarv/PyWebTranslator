import os

from abc import ABC
from selenium import webdriver


WEBDRIVER_EXEC_DIR = os.path.normpath(r'./.webdrivers')
SERVICE_LOG_DIR = os.path.normpath(f'{WEBDRIVER_EXEC_DIR}/logs/')

# WebDriverManager environment variables
os.environ['WDM_LOG_LEVEL'] = '0'  # disable console logs
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'  # disable blank line printed to console

# create WebDriver directories
if not os.path.exists(WEBDRIVER_EXEC_DIR):
    os.mkdir(WEBDRIVER_EXEC_DIR)
    os.mkdir(SERVICE_LOG_DIR)
elif not os.path.exists(SERVICE_LOG_DIR):
    os.mkdir(SERVICE_LOG_DIR)


class AbstractBrowser(ABC):
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

    @property
    def driver(self):
        return self.__driver
