from pywebtranslator.browsers.abstractbrowser import AbstractBrowser

from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import presence_of_element_located


class TranslationService(ABC):
    """Translation services base class. Use a specific TranslationService class to start translating."""

    def __init__(self,
                 browser: AbstractBrowser,
                 translation_service_url: str,
                 src_textarea: str,
                 tgt_textarea: str,
                 timeout_threshold: int):
        """
        Calls given URL in given browser and sets up the website for the translation process.

        :param browser: The Browser class to use
        :param translation_service_url: URL of the specified translation service
        :param src_textarea: CSS path to the source language textarea within the website
        :param tgt_textarea: CSS path to the target language textarea within the website
        :param timeout_threshold: Timeout in seconds after which a translation request throws a TimeoutException
        """

        # instantiate a browser
        self._browser: AbstractBrowser = browser
        self._browser.get(translation_service_url)

        # initialize timeout thresholds
        self._wait_for_ui: WebDriverWait = WebDriverWait(self._browser.driver, 1)
        self._wait_for_translation: WebDriverWait = WebDriverWait(self._browser.driver, timeout_threshold)

        # get the text areas that are relevant for translating
        self._src_textarea: WebElement = self.search_css(src_textarea)
        self._tgt_textarea: WebElement = self.search_css(tgt_textarea)

        # initialize current selected languages
        self._supported_langs: dict = self._get_supported_languages()
        self._current_src_lang: str = self._get_source_language()
        self._current_tgt_lang: str = self._get_target_language()

        super().__init__()

    def search_css(self, css_selector: str) -> WebElement:
        """
        Searches for given CSS selector in HTML DOM and returns the corresponding element if found.
        :param css_selector: The CSS path to look for
        """
        return self._wait_for_ui.until(presence_of_element_located((By.CSS_SELECTOR, css_selector)))

    def is_language_supported(self, language: str) -> bool:
        """
        Checks with the list of language on the website and returns if given language is supported.
        :param language: The language to check if it is supported.
        :return: Whether the given language is supported by this service or not.
        """
        return language is not None and language in self._supported_langs.keys()

    def translate(self, text: str, source_language=None, target_language=None) -> str:
        """
        Parses given text to website, calls _get_translation() and returns its result.
        Returns empty string if _get_translation() times out.
        """
        if len(text) <= 1:  # return text if its just one letter
            return text

        self._set_languages(source_language, target_language)

        # send the text to the website
        self._src_textarea.send_keys(text)

        try:  # await translation
            return self._get_translation(text)
        except TimeoutException:
            return ""

    def quit(self) -> None:
        """Quits the translation service and its associated browser session."""
        self._browser.driver.quit()

    @abstractmethod
    def _get_translation(self, from_text: str) -> str:
        """Defines the procedure to retrieve a translation from the website."""
        pass

    @abstractmethod
    def _get_supported_languages(self) -> dict:
        """Defines the procedure to get all supported languages from the website."""
        pass

    @abstractmethod
    def _get_source_language(self) -> str:
        """Defines the procedure to get the current input source language from the website."""
        pass

    @abstractmethod
    def _get_target_language(self) -> str:
        """Defines the procedure to get the current output target language from the website."""
        pass

    @abstractmethod
    def _set_source_language(self, language) -> None:
        """Defines the procedure to set the new source language on the website."""
        pass

    @abstractmethod
    def _set_target_language(self, language) -> None:
        """Defines the procedure to set the new target language on the website."""
        pass

    @abstractmethod
    def _set_languages(self, src_lang, tgt_lang) -> None:
        """Defines the procedure to set both languages at once on the website."""
        pass

    @abstractmethod
    def _switch_languages(self) -> None:
        """Defines the procedure to switch target- with source language on the website."""
        pass

    # Getter & Setter

    @property
    def supported_languages(self) -> dict:
        return self._supported_langs

    @property
    def source_language(self) -> str:
        return self._current_src_lang

    @property
    def target_language(self) -> str:
        return self._current_tgt_lang
