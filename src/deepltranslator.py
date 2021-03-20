import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class DeepLTranslator:
    def __init__(self, browser_name, headless=True, timeout_threshold=30):
        self._sourceLang = None
        self._targetLang = None
        self.__headless = headless
        self.__browserName = browser_name
        self.__timeoutThreshold = timeout_threshold
        self.__workDir = os.path.normpath(os.path.join(os.path.dirname(__file__)))
        self._supportedBrowsers = {
            'Firefox': ('FirefoxOptions',
                        os.path.join(self.__workDir, r'./geckodriver.exe'),
                        os.path.join(self.__workDir, r'./geckodriver.log'))}
        self._supported_languages = {'English': 'en',
                                     'German': 'de',
                                     'Russian': 'ru',
                                     'Spanish': 'es',
                                     'French': 'fr',
                                     'Dutch': 'nl',
                                     'Polish': 'pl',
                                     'Portuguese': 'pt',
                                     'Japanese': 'ja',
                                     'Italian': 'it',
                                     'Chinese': 'zh'}
        if browser_name in self._supportedBrowsers:
            self.__init_browser_session(browser_name)
        else:
            raise ValueError('Browser not supported!')

    def __del__(self):
        if self.__browser:
            self.__browser.close()

    def __search_css(self, css):
        """Searches for given CSS location in HTML text and returns element if found."""
        return self.__waitForRequest.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))

    def __init_browser_session(self, browser_name):
        """Sets up a Selenium webdriver for use and initializes DeepL translation via the specified browser."""
        # Selecting the browser, browser options, driver path and log path determined by given browser
        browser_options = getattr(webdriver, self._supportedBrowsers[browser_name][0])()
        browser_options.headless = self.__headless
        self.__browser = getattr(webdriver, browser_name)(
            options=browser_options,
            service_log_path=self._supportedBrowsers[browser_name][2],
            executable_path=self._supportedBrowsers[browser_name][1],
        )
        self.__browser.set_window_position(0, 0)
        self.__browser.set_window_size(1920, 1080)
        self.__browser.get('https://www.deepl.com/en/translator')
        self.__waitForUI = WebDriverWait(self.__browser, 5)
        self.__waitForRequest = WebDriverWait(self.__browser, self.__timeoutThreshold)
        self.__sourceTextArea = self.__search_css("textarea[dl-test='translator-source-input']")
        self.__targetTextArea = self.__search_css("textarea[dl-test='translator-target-input']")
        self.source_language = 'en'
        self.target_language = 'de'

    def translate(self, source_text):
        """
        Parses the sourceText to DeepL and returns whatever is given back. Returns empty string if request times out.
        """
        if len(source_text) > 1:
            self.__sourceTextArea.send_keys(source_text)
            try:  # wait til DeepL finishes translation
                WebDriverWait(self.__browser, 12).until(
                    TextNotToBePresentInElementValueNorTextShorterThanLimit(self.__targetTextArea, '[...]', 2))
            except TimeoutException:
                return ""
            else:
                translation = self.__targetTextArea.get_attribute('value')
                self.__sourceTextArea.clear()
                return translation
        else:  # just return sourceText if its a single letter
            return source_text

    def reinitialize_browser_session(self):
        self.__browser.close()
        self.__init_browser_session(self.__browserName)

    def close(self):
        self.__browser.close()

    @property
    def supported_languages(self):
        return self._supported_languages

    @property
    def supported_browsers(self):
        return self._supportedBrowsers

    @property
    def source_language(self):
        source_lang_button_text = self.__search_css("button[dl-test='translator-source-lang-btn']").text
        for language in self._supported_languages.keys():
            if language in source_lang_button_text:
                return language

    @property
    def target_language(self):
        target_lang_button_text = self.__search_css("button[dl-test='translator-target-lang-btn']").text
        for language in self._supported_languages.keys():
            if language in target_lang_button_text:
                return language

    @source_language.setter
    def source_language(self, lang):
        if lang in self._supported_languages.values():  # if source_language is a valid selection
            if lang != self.source_language:  # skip changing if its already selected
                self.__search_css("button[dl-test='translator-source-lang-btn']").click()
                self.__search_css(f"button[dl-test='translator-lang-option-{lang.lower()}']").click()
        else:
            raise ValueError("Source language not supported!")

    @target_language.setter
    def target_language(self, lang):
        if lang in self._supported_languages.values():  # if target_language is a valid selection
            if lang != self.target_language:  # skip changing if its already selected
                if lang != self.source_language:
                    self.__search_css("button[dl-test='translator-target-lang-btn']").click()
                    if lang.lower() == 'en':
                        self.__search_css(f"button[dl-test='translator-lang-option-{lang.lower()}-{'US'}']").click()
                    else:
                        self.__search_css(
                            f"button[dl-test='translator-lang-option-{lang.lower()}-{lang.upper()}']").click()
        else:
            raise ValueError("Target language not supported!")


class TextNotToBePresentInElementValueNorTextShorterThanLimit:
    """
    An expectation for checking if the given text is not present in the element nor shorter than given limit
    """

    def __init__(self, element, text_, limit_):
        self.element = element
        self.text_ = text_
        self.limit_ = limit_

    def __call__(self, driver):
        if (self.text_ not in self.element.get_attribute('value')) and (
                len(self.element.get_attribute('value')) >= self.limit_):
            return self.element
        else:
            return False
