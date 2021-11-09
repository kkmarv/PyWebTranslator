from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from .browsers import Browser
from .expectations import IsTextPresent, TextNotPresent, TextNotPresentAndTextShorterThan


class TranslationService(ABC):
    """Translation services base class."""

    def __init__(self,
                 browser: Browser.__class__,
                 translation_service_url: str,
                 source_textarea: str,
                 target_textarea: str,
                 timeout_threshold: int):
        """
        Calls the specified URL in the specified browser and sets up the website to allow further translation.

        :param browser: Selenium webdriver object
        :param translation_service_url: URL of the specified translation service which to open in browser
        :param source_textarea: CSS path to source language textarea within the website
        :param target_textarea: CSS path to target language textarea within the website
        :param timeout_threshold: Timeout in seconds after which a translation request throws a TimeoutException
        """

        self._driver: webdriver = browser.driver
        self._driver.get(translation_service_url)

        self._wait_for_ui = WebDriverWait(self._driver, 1)
        self._wait_for_translation = WebDriverWait(self._driver, timeout_threshold)

        self._source_textarea: WebElement = self.search_css(source_textarea)
        self._target_textarea: WebElement = self.search_css(target_textarea)

        self._supported_languages: dict = self._get_supported_languages()

        self._source_language = self._get_source_language()
        self._target_language = self._get_target_language()

        super().__init__()

    def search_css(self, css: str) -> WebElement:
        """
        Searches for given CSS location in HTML text and returns element if found.
        :param css: CSS path to look for
        """
        return self._wait_for_ui.until(presence_of_element_located((By.CSS_SELECTOR, css)))

    def is_language_supported(self, language) -> bool:
        """
        Checks with the list of language on the website and returns if given language is supported.
        :param language: The language to check if it is supported.
        :return: Whether the given language is supported by this service or not.
        """
        return language is not None and language in self._supported_languages.keys()

    def translate(self, text: str, source_language=None, target_language=None) -> str:
        """
        Parses given text to website, calls _get_translation() and returns its result.
        Returns empty string if _get_translation() times out.
        """
        if len(text) <= 1:  # return text if its just one letter
            return text

        self._set_languages(source_language, target_language)

        # send the text to the website
        self._source_textarea.send_keys(text)

        #  await translation
        try:
            return self._get_translation(text)
        except TimeoutException:
            return ""

    @abstractmethod
    def _get_translation(self, from_text: str) -> str:
        """Defines the procedure to retrieve translations from the website."""
        pass

    @abstractmethod
    def _get_supported_languages(self) -> dict:
        """Defines the procedure to get all supported languages from the website."""
        pass

    @abstractmethod
    def _get_source_language(self):
        """Defines the procedure to get the current input source language from the website."""
        pass

    @abstractmethod
    def _get_target_language(self):
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
    def _set_languages(self, source_language, target_language) -> None:
        """Defines the procedure to set both languages at once on the website."""
        pass

    @abstractmethod
    def _switch_languages(self) -> None:
        """Defines the procedure to switch target- with source language on the website."""
        pass

    # Getter & Setter

    @property
    def supported_languages(self) -> dict:
        return self._supported_languages

    @property
    def source_language(self):
        return self._source_language

    @property
    def target_language(self):
        return self._target_language


class DeepL(TranslationService):
    """
    API to interact with DeepL online translator at https://www.deepl.com/
    Holds all information and methods to interact with the website.
    """

    def __init__(self, browser: webdriver, timeout_threshold=30):
        """
        Calls super class with specific information on how to set up DeepL online translation.

        :param browser: Selenium webdriver object
        :param timeout_threshold: Timeout in seconds after which a translation request throws a TimeoutException
        """

        translation_service_url = r"https://www.deepl.com/"
        source_textarea = r"textarea[dl-test='translator-source-input']"
        target_textarea = r"textarea[dl-test='translator-target-input']"

        self._paywall_div = r"div[class='lmt__notification__blocked_content']"
        self._source_language_list = r".lmt__language_wrapper > .lmt__language_select_column > *"
        self._source_language_list_div = r"div[dl-test='translator-source-lang-list']"
        self._source_language_list_button = r"button[dl-test='translator-source-lang-btn']"
        self._target_language_list_button = r"button[dl-test='translator-target-lang-btn']"
        self._language_switch_div = r"div[class='lmt__language_container_switch']"

        super().__init__(browser, translation_service_url, source_textarea, target_textarea, timeout_threshold)

    def _is_paywall_visible(self) -> bool:
        try:
            self.search_css(self._paywall_div)
        except TimeoutException:
            return False
        else:
            return True

    def _get_translation(self, from_text: str) -> str:
        if from_text in self._target_textarea.get_attribute('value'):  # wait for the text to refresh
            self._wait_for_translation.until(TextNotPresent(self._target_textarea, from_text))
        # wait for the translation to appear
        self._wait_for_translation.until(TextNotPresentAndTextShorterThan(self._target_textarea, '[...]', 2))

        translation = self._target_textarea.get_attribute('value')
        self._source_textarea.clear()

        return translation

    def _get_supported_languages(self) -> dict:
        # show language list
        self.search_css(self._source_language_list_button).click()

        # get supported languages from the source language list
        source_language_list_div = self.search_css(self._source_language_list_div)
        source_language_list = source_language_list_div.find_elements(By.CSS_SELECTOR, self._source_language_list)

        supported_languages = {}
        for button in source_language_list:
            self._wait_for_ui.until(IsTextPresent(button))
            language = button.text
            language_id = button.get_attribute("dl-test").split("-")[3]
            supported_languages[language_id] = language

        # hide language list
        self.search_css(self._source_language_list_button).click()

        return supported_languages

    def _get_source_language(self):
        language = self.search_css(self._source_language_list_button).text
        # display- and source text don't match here so we have to correct it:
        # language = "Any language (detect)" if "ny language" in language else language # TODO remove
        # language = language.split(" ")[2] if "Translate from" in language else language
        return list(self._supported_languages.keys())[list(self._supported_languages.values()).index(language)]

    def _get_target_language(self):
        target_lang_button_text = self.search_css(self._target_language_list_button).text
        for language in self._supported_languages.values():
            # we want to search only for values that are in our supported_languages
            if language in target_lang_button_text:
                return list(self._supported_languages.keys())[list(self._supported_languages.values()).index(language)]

    def _set_source_language(self, source_language) -> None:
        if not self.is_language_supported(source_language):
            raise ValueError("Source language not supported!")

        if source_language != self._source_language:  # skip changing if its already selected
            self.search_css(self._source_language_list_button).click()
            self.search_css(f"button[dl-test='translator-lang-option-{source_language.lower()}']").click()
            self._source_language = source_language

    def _set_target_language(self, target_language) -> None:
        if not self.is_language_supported(target_language):
            raise ValueError("Target language not supported!")

        if target_language != self._target_language:  # skip changing if its already selected
            if target_language != self._source_language:
                self.search_css(self._target_language_list_button).click()
                # the following used to distinct between en-US and en-GB dialects
                # if target_language.lower() == 'en':
                #     self.search_css(
                #         f"button[dl-test='translator-lang-option-{target_language.lower()}-{'US'}']").click()
                # else:
                self.search_css(
                    f"button[dl-test='translator-lang-option-{target_language.lower()}-{target_language.upper()}']").click()
                self._target_language = target_language

    def _set_languages(self, source_language, target_language) -> None:
        if not self.is_language_supported(source_language):
            raise ValueError("Source language not supported!")
        if not self.is_language_supported(target_language):
            raise ValueError("Target language not supported!")

        # use the websites' button to change languages if they are reversed
        if source_language == self._source_language and target_language == self._source_language:
            self._switch_languages()
        else:
            self._set_source_language(source_language)
            self._set_target_language(target_language)

    def _switch_languages(self) -> None:
        self.search_css(self._language_switch_div).click()
        # switch class variables too
        self._source_language, self._target_language = self._target_language, self._source_language


class Google(TranslationService):
    pass  # TODO
