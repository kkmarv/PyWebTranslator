from abc import ABC

from msedge.selenium_tools import Edge as EdgeDriver, EdgeOptions
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from translatorapi import TranslatorAPI

SERVICE_LOG_PATH = r"./browsers/logs/"


class Browser(ABC):
    """ Base class for all Browsers. """

    def __init__(self, browser, api_sub_class: TranslatorAPI.__class__):
        self.browser = browser
        self.browser.set_window_position(0, 0)
        self.browser.set_window_size(1920, 1080)

        self.api = api_sub_class(self.browser)

    def __del__(self):
        self.browser.close()


class Firefox(Browser):
    """
    Creates a Firefox browser session.
    """

    def __init__(self, api_sub_class: TranslatorAPI.__class__, headless=True):
        """
        :param api_sub_class:
        :param headless: Whether the browser should be headless or not
        """
        browser_options: FirefoxOptions = FirefoxOptions()
        browser_options.headless = headless
        firefox_browser: FirefoxDriver = FirefoxDriver(
            executable_path=GeckoDriverManager().install(),
            service_log_path=SERVICE_LOG_PATH + r"geckodriver.log",
            options=browser_options)
        super().__init__(firefox_browser, api_sub_class)


class Edge(Browser):
    """
    Creates a Edge browser session.
    """

    def __init__(self, api_sub_class: TranslatorAPI.__class__, headless=True):
        browser_options: EdgeOptions = EdgeOptions()
        browser_options.use_chromium = True
        if headless:
            browser_options.add_argument("headless")
            browser_options.add_argument('disable-gpu')
        edge_browser: EdgeDriver = EdgeDriver(
            executable_path=EdgeChromiumDriverManager().install(),
            service_log_path=SERVICE_LOG_PATH + r"msedgedriver.log",
            options=browser_options)
        super().__init__(edge_browser, api_sub_class)
