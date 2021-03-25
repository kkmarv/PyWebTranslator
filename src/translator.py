from abc import ABC, abstractmethod
from enum import Enum

from selenium.common.exceptions import TimeoutException

from browsers.browser import Browser
from browsers.expectations import TextNotPresentAndTextShorterThan


class TranslatorAPI(ABC):
    """ Base class for all translator APIs. """

    class Language(Enum):
        pass

    def __init__(self, browser: Browser):
        self.sourceLang = ""
        self.targetLang = ""
        self.supported_languages = {}
        self.browser = browser

        super().__init__()

    def translate(self, text: str) -> str:
        """
        Parses given text to website and returns whatever is given back.
        Returns empty string if request times out.
        """
        if len(text) > 1:
            self.browser.source_textarea.send_keys(text)
            try:
                return self.get_translation()
            except TimeoutException:
                return ""
        else:  # just return the text if its a single letter
            return text

    @abstractmethod
    def get_translation(self):
        """ Defines the procedure to handle the translation a specific website. """
        pass

    @abstractmethod
    def get_supported_languages(self):
        """ Defines the procedure to get all supported languages from a specific website. """
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

    def __init__(self, browser_class: Browser.__class__):
        """
        Instantiates a Browser object from a given browser sub class and gets the DeepL translator website ready for
        translation.

        :param browser_class: Reference to a Browser sub class
        """
        url = "https://www.deepl.com/"
        source_textarea = r"textarea[dl-test='translator-source-input']"
        target_textarea = r"textarea[dl-test='translator-target-input']"
        super().__init__(browser_class(url, source_textarea, target_textarea, False))

        self.supported_languages = self.get_supported_languages()

    def get_translation(self) -> str:
        self.browser.wait_for_translation.until(
            TextNotPresentAndTextShorterThan(self.browser.target_textarea, '[...]', 2))
        translation = self.browser.target_textarea.get_attribute('value')
        self.browser.source_textarea.clear()
        return translation

    def get_supported_languages(self):
        return {}

    @property
    def source_language(self):
        source_lang_button_text = self.browser.search_css("button[dl-test='translator-source-lang-btn']").text
        for language in self.supported_languages.keys():
            if language in source_lang_button_text:
                return language

    @property
    def target_language(self):
        target_lang_button_text = self.browser.search_css("button[dl-test='translator-target-lang-btn']").text
        for language in self.supported_languages.keys():
            if language in target_lang_button_text:
                return language

    @source_language.setter
    def source_language(self, lang):
        if lang in self.supported_languages.values():  # if source_language is a valid selection
            if lang != self.source_language:  # skip changing if its already selected
                self.browser.search_css("button[dl-test='translator-source-lang-btn']").click()
                self.browser.search_css(f"button[dl-test='translator-lang-option-{lang.lower()}']").click()
        else:
            raise ValueError("Source language not supported!")

    @target_language.setter
    def target_language(self, lang):
        if lang in self.supported_languages.values():  # if target_language is a valid selection
            if lang != self.target_language:  # skip changing if its already selected
                if lang != self.source_language:
                    self.browser.search_css("button[dl-test='translator-target-lang-btn']").click()
                    if lang.lower() == 'en':
                        self.browser.search_css(
                            f"button[dl-test='translator-lang-option-{lang.lower()}-{'US'}']").click()
                    else:
                        self.browser.search_css(
                            f"button[dl-test='translator-lang-option-{lang.lower()}-{lang.upper()}']").click()
        else:
            raise ValueError("Target language not supported!")


class Google(TranslatorAPI):
    pass
