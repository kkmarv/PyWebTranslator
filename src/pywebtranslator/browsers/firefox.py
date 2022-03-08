import os.path
import pywebtranslator.browsers.abstractbrowser as browser

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver import Firefox as FirefoxDriver, FirefoxOptions


class Firefox(browser.AbstractBrowser):
    def __init__(self, is_headless=True):
        """Creates a Firefox browser session.

        :param is_headless: Whether the browser should run in the background (without GUI).
        """

        # prepare WebDriver options
        driver_options: FirefoxOptions = FirefoxOptions()
        driver_options.headless = is_headless

        # create a selenium WebDriver
        firefox_driver: FirefoxDriver = FirefoxDriver(
            service=FFService(
                log_path=os.path.normpath(f'{browser.SERVICE_LOG_DIR}/geckodriver.log'),
                executable_path=GeckoDriverManager(path=browser.WEBDRIVER_EXEC_DIR).install()),
            options=driver_options
        )

        super().__init__(firefox_driver)
