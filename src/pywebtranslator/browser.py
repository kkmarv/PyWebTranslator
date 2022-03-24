import os

# abstract
from abc import ABC
from selenium.webdriver.remote.webdriver import WebDriver
# edge
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EService
from selenium.webdriver import Edge as EdgeDriver, EdgeOptions
# firefox
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions


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


class AbstractBrowser(ABC):
    def __init__(self, driver: WebDriver):
        """Abstract superclass for browsers. Use a specific Browser class to instantiate a browser session.

        :param driver: Which driver to use"""
        self.__driver: WebDriver = driver
        self.__driver.set_window_size(1920, 1080)  # at this size, every button used is inside the viewport

    def __del__(self):
        self.__driver.quit()

    def get(self, url: str) -> None:
        """Calls given URL in this browser."""
        self.driver.get(url)

    @property
    def driver(self) -> WebDriver:
        return self.__driver


class Edge(AbstractBrowser):
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


class Firefox(AbstractBrowser):
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
