import os.path
import pywebtranslator.browsers.abstractbrowser as browser

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EService
from selenium.webdriver import Edge as EdgeDriver, EdgeOptions


class Edge(browser.AbstractBrowser):
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
                log_path=os.path.normpath(f'{browser.SERVICE_LOG_DIR}/msedgedriver.log'),
                executable_path=EdgeChromiumDriverManager(path=browser.WEBDRIVER_EXEC_DIR).install()
            ),
            options=driver_options
        )

        super().__init__(edge_driver)
