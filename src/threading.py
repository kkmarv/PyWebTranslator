from .browsers import Browser


class BrowserPool:
    """A class which manages multiple browsers. It simultaneous creates as many browsers as needed."""
    __pool: list[Browser] = []

    def __init__(self, browser_type: Browser.__class__, is_headless=True):
        self.browser_type = browser_type
        self.is_headless = is_headless

    def claim(self) -> Browser:  # hopefully this mechanism creates at most as many browsers as needed and not more
        """Returns a browser from the pool or creates a new one if all browsers are in use."""
        return self.browser_type(is_headless=self.is_headless) if len(self.__pool) <= 0 else self.__pool.pop()

    def stash(self, browser: Browser) -> None:
        """
        Puts a browser back into the pool.
        :param browser The browser to stash. Make sure it is not accessed after this call!
        """
        self.__pool.append(browser)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for browser in self.__pool:
            browser.driver.close()
            browser.driver.quit()
