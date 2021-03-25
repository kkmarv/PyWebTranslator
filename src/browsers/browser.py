from abc import ABC

from msedge.selenium_tools import Edge as EdgeDriver, EdgeOptions
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

SERVICE_LOG_PATH = r"./browsers/logs"


class Browser(ABC):
    """ Base class for all Browsers. """

    def __init__(self, browser, url: str, source_textarea: str, target_textarea: str, timeout_threshold=30):
        self.browser = browser
        self.browser.set_window_position(0, 0)
        self.browser.set_window_size(1920, 1080)
        self.browser.get(url)

        self.wait_for_ui = WebDriverWait(self.browser, 5)
        self.wait_for_translation = WebDriverWait(self.browser, timeout_threshold)

        self.source_textarea = self.search_css(source_textarea)
        self.target_textarea = self.search_css(target_textarea)

    def search_css(self, css: str):
        """
        Searches for given CSS location in HTML text and returns element if found.
        :param css: CSS path to look for
        """
        return self.wait_for_ui.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))

    def __del__(self):
        self.browser.close()


class Firefox(Browser):
    """
    Creates a Firefox browser session.
    """

    def __init__(self, url: str, source_textarea: str, target_textarea: str, headless=True, timeout_threshold=30):
        """
        :param url: URL to open at start of browser session
        :param source_textarea: CSS path to the source language textarea
        :param target_textarea: CSS path to the target language textarea
        :param headless: Whether the browser should be headless or not
        :param timeout_threshold: Time in seconds after which a TimeoutException should be thrown if the website cannot be conmpletely loaded.
        """
        browser_options: FirefoxOptions = FirefoxOptions()
        browser_options.headless = headless
        firefox_browser: FirefoxDriver = FirefoxDriver(
            executable_path=GeckoDriverManager().install(),
            service_log_path=SERVICE_LOG_PATH + r"/geckodriver.txt",
            options=browser_options)
        super().__init__(firefox_browser, url, source_textarea, target_textarea, timeout_threshold)


class Edge(Browser):
    """
    Creates a Edge browser session.
    """

    def __init__(self, url: str, source_textarea: str, target_textarea: str, headless=True, timeout_threshold=30):
        browser_options: EdgeOptions = EdgeOptions()
        browser_options.use_chromium = True
        if headless:
            browser_options.add_argument("headless")
            browser_options.add_argument('disable-gpu')
        edge_browser: EdgeDriver = EdgeDriver(
            executable_path=EdgeChromiumDriverManager().install(),
            service_log_path=SERVICE_LOG_PATH + r"/msedgedriver.txt",
            options=browser_options)
        super().__init__(edge_browser, url, source_textarea, target_textarea, timeout_threshold)
