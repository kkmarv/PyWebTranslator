import os.path

from abc import ABC
from selenium import webdriver
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge as EdgeDriver, EdgeOptions


SERVICE_LOG_PATH = r'./logs/'
WEBDRIVER_ARGUMENTS = {
    'path': r'./webdrivers/',
    'log_level': 0,
    'print_first_line': False
}

# create paths
if not os.path.exists(SERVICE_LOG_PATH):
    os.mkdir(SERVICE_LOG_PATH)
if not os.path.exists(WEBDRIVER_ARGUMENTS['path']):
    os.mkdir(WEBDRIVER_ARGUMENTS['path'])


class Browser(ABC):
    """Abstract Browser class"""

    def __init__(self, driver: webdriver, is_headless: bool, stay_open: bool):
        """
        Creates a browser session with given driver and translation service.

        :param driver: Which driver to use
        :param stay_open: Whether the browser window will close after its finished or not.
        """

        self._driver: webdriver = driver
        self._driver.set_window_position(0, 0)
        self._driver.set_window_size(1920, 1080)

        self._stay_open = stay_open
        self._is_headless = is_headless

    def __del__(self):
        """Makes sure to properly quit the driver before exiting the program."""
        self._driver.close() if (self._is_headless or not self._stay_open) else None

    # Getter & Setter

    @property
    def driver(self) -> webdriver:
        return self._driver


class Firefox(Browser):
    def __init__(self, is_headless=True, stay_open=False):
        """Creates a Firefox browser session.

        :param is_headless: Whether the browser should run in the background (without GUI) or not.
        :param stay_open: Whether the browser window will close after its finished or not. is_headless has to be set to False for this to take effect. This is to prevent processes from idling in the background.
        """

        # prepare webdriver options
        driver_options: FirefoxOptions = FirefoxOptions()
        driver_options.headless = is_headless

        # create a selenium driver and install the webdriver for selenium usage
        firefox_driver: FirefoxDriver = FirefoxDriver(
            executable_path=GeckoDriverManager(**WEBDRIVER_ARGUMENTS).install(),
            service_log_path=SERVICE_LOG_PATH + r'geckodriver.log',
            options=driver_options
        )

        super().__init__(firefox_driver, is_headless, stay_open)


class Edge(Browser):
    def __init__(self, is_headless=True, stay_open=False):
        """Creates a Edge browser session.

        :param is_headless: Whether the browser should run in the background (without GUI) or not.
        :param stay_open: Whether the browser window will close after its finished or not. is_headless has to be set to False for this to take effect. This is to prevent processes from idling in the background.
        """

        # prepare webdriver options
        driver_options: EdgeOptions = EdgeOptions()
        driver_options.use_chromium = True

        if is_headless:
            driver_options.add_argument('is_headless')
            driver_options.add_argument('disable-gpu')

        # create a selenium driver and install the webdriver for selenium usage
        edge_driver: EdgeDriver = EdgeDriver(
            executable_path=EdgeChromiumDriverManager(**WEBDRIVER_ARGUMENTS).install(),
            service_log_path=SERVICE_LOG_PATH + r'msedgedriver.log',
            options=driver_options
        )

        super().__init__(edge_driver, is_headless, stay_open)
