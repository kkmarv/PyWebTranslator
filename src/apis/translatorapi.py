from abc import ABC, abstractmethod
from enum import Enum

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from seleniumbrowsers.expectations import TextIsPresent
from seleniumbrowsers.expectations import TextNotPresentAndTextShorterThan


class TranslatorAPI(ABC):
    """ Base class for all translator APIs. """

    class Language(Enum):
        pass

    def __init__(self, browser: webdriver, url: str,
                 source_textarea: str, target_textarea: str, timeout_threshold: int):

        self.browser = browser
        self.browser.get(url)

        self.wait_for_ui = WebDriverWait(self.browser, 5)
        self.wait_for_translation = WebDriverWait(self.browser, timeout_threshold)

        self.source_textarea = self.search_css(source_textarea)
        self.target_textarea = self.search_css(target_textarea)

        self.sourceLang = ""
        self.targetLang = ""
        self.supported_languages = self.get_supported_languages()

        super().__init__()

    def search_css(self, css: str) -> WebElement:
        """
        Searches for given CSS location in HTML text and returns element if found.
        :param css: CSS path to look for
        """
        return self.wait_for_ui.until(presence_of_element_located((By.CSS_SELECTOR, css)))

    def translate(self, text: str) -> str:
        """
        Parses given text to website and calls get_translation().
        Returns empty string if request times out.
        """
        if len(text) > 1:
            self.source_textarea.send_keys(text)
            try:
                return self.get_translation()
            except TimeoutException:
                return ""
        else:  # just return the text if its a single letter
            return text

    @abstractmethod
    def get_translation(self) -> str:
        """Defines the procedure to retrieve translations from a specific website."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> dict:
        """Defines the procedure to get all supported languages from a specific website."""
        pass

    # Getter & Setter

    @property
    @abstractmethod
    def source_language(self):
        pass

    @property
    @abstractmethod
    def target_language(self):
        pass

    @source_language.setter
    @abstractmethod
    def source_language(self, lang):
        pass

    @target_language.setter
    @abstractmethod
    def target_language(self, lang):
        pass


class DeepL(TranslatorAPI):
    """
    API to interact with DeepL online translator at https://www.deepl.com/
    """

    def __init__(self, browser: webdriver, timeout_threshold=30):
        """
        Instantiates a Browser object from a given browser sub class and gets the DeepL translator website ready for
        translation.

        :param browser: Reference to a Browser sub class #TODO docstrings update!!
        """
        url = "https://www.deepl.com/"
        source_textarea = r"textarea[dl-test='translator-source-input']"
        target_textarea = r"textarea[dl-test='translator-target-input']"
        super().__init__(browser, url, source_textarea, target_textarea, timeout_threshold)

    def get_translation(self) -> str:
        self.wait_for_translation.until(TextNotPresentAndTextShorterThan(self.target_textarea, '[...]', 2))
        translation = self.target_textarea.get_attribute('value')
        self.source_textarea.clear()
        return translation

    def get_supported_languages(self) -> dict:
        self.search_css("button[dl-test='translator-source-lang-btn']").click()
        source_language_button_list_div = self.search_css("div[dl-test='translator-source-lang-list']")
        source_language_button_list = source_language_button_list_div.find_elements_by_css_selector("*")
        supported_languages = {}
        for button in source_language_button_list:
            self.wait_for_ui.until(TextIsPresent(button))
            language = button.text
            supported_languages[language] = "".join(language[:3]).lower()
        return supported_languages

    @property
    def source_language(self):
        source_lang_button_text = self.search_css("button[dl-test='translator-source-lang-btn']").text
        for language in self.supported_languages.keys():
            if language in source_lang_button_text:
                return language

    @property
    def target_language(self):
        target_lang_button_text = self.search_css("button[dl-test='translator-target-lang-btn']").text
        for language in self.supported_languages.keys():
            if language in target_lang_button_text:
                return language

    @source_language.setter
    def source_language(self, lang):
        if lang in self.supported_languages.keys():  # if source_language is a valid selection
            if lang != self.source_language:  # skip changing if its already selected
                self.search_css("button[dl-test='translator-source-lang-btn']").click()
                self.search_css(f"button[dl-test='translator-lang-option-{lang.lower()}']").click()
        else:
            raise ValueError("Source language not supported!")

    @target_language.setter
    def target_language(self, lang):
        if lang in self.supported_languages.keys():  # if target_language is a valid selection
            if lang != self.target_language:  # skip changing if its already selected
                if lang != self.source_language:
                    self.search_css("button[dl-test='translator-target-lang-btn']").click()
                    if lang.lower() == 'en':
                        self.search_css(
                            f"button[dl-test='translator-lang-option-{lang.lower()}-{'US'}']").click()
                    else:
                        self.search_css(
                            f"button[dl-test='translator-lang-option-{lang.lower()}-{lang.upper()}']").click()
        else:
            raise ValueError("Target language not supported!")


class Google(TranslatorAPI):
    pass
