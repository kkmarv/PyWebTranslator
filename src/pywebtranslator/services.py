from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

# DeepL
from .browser import AbstractBrowser
from .expectations import TextNotPresentAndLongerThan
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    text_to_be_present_in_element,
    visibility_of_all_elements_located
)


class AbstractService(ABC):
    """Translation services base class. Use a specific TranslationService class to start translating."""

    def __init__(self,
                 browser: AbstractBrowser,
                 translation_service_url: str,
                 src_textarea_path: str,
                 tgt_textarea_path: str):
        """Calls given URL in given browser and sets up the website for the translation process.

        :param browser: The Browser class to use
        :param translation_service_url: URL of the specified translation service
        :param src_textarea_path: CSS path to the source language textarea within the website
        :param tgt_textarea_path: CSS path to the target language textarea within the website
        """

        # instantiate a browser
        self._browser: AbstractBrowser = browser
        self._browser.get(translation_service_url)

        # initialize timeout thresholds
        self._wait_5_sec: WebDriverWait = WebDriverWait(self._browser.driver, 5)
        self._wait_30_sec: WebDriverWait = WebDriverWait(self._browser.driver, 30)

        # get the text areas that are relevant for translating
        self._src_textarea: WebElement = self._search_element(src_textarea_path)
        self._tgt_textarea: WebElement = self._search_element(tgt_textarea_path)

        # initialize current selected languages
        self._supported_langs: dict = self._get_supported_languages()
        self._current_src_lang: str = self._get_source_language()
        self._current_tgt_lang: str = self._get_target_language()

        super().__init__()

    def _search_element(self, css_path: str) -> WebElement:
        """Searches for a given CSS selector in HTML DOM and returns the corresponding element if found.

        :param css_path: The CSS path to look for"""
        return self._wait_5_sec.until(presence_of_element_located((By.CSS_SELECTOR, css_path)))

    def is_language_supported(self, language: str) -> bool:
        """Checks with the list of language on the website and returns if given language is supported.

        :param language: The language to check if it is supported.
        :return: Whether the given language is supported by this service or not."""
        return language is not None and language in self._supported_langs.keys()

    def translate(self, text: str, source_language=None, target_language=None) -> str:
        """Parses given text to website, calls _get_translation() and returns its result.
        Returns empty string if _get_translation() times out."""
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

    # Abstract methods

    @abstractmethod
    def _get_translation(self, from_text: str) -> str:
        """Defines the procedure to retrieve a translation from the website."""
        raise NotImplementedError

    @abstractmethod
    def _get_supported_languages(self) -> dict:
        """Defines the procedure to get all supported languages from the website."""
        raise NotImplementedError

    @abstractmethod
    def _get_source_language(self) -> str:
        """Defines the procedure to get the current input source language from the website."""
        raise NotImplementedError

    @abstractmethod
    def _get_target_language(self) -> str:
        """Defines the procedure to get the current output target language from the website."""
        raise NotImplementedError

    @abstractmethod
    def _set_source_language(self, language) -> None:
        """Defines the procedure to set a new source language on the website."""
        raise NotImplementedError

    @abstractmethod
    def _set_target_language(self, language) -> None:
        """Defines the procedure to set a new target language on the website."""
        raise NotImplementedError

    @abstractmethod
    def _set_languages(self, src_lang, tgt_lang) -> None:
        """Defines the procedure to set both languages at once on the website."""
        raise NotImplementedError

    @abstractmethod
    def _switch_languages(self) -> None:
        """Defines the procedure to switch target- with source language on the website."""
        raise NotImplementedError

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


class DeepL(AbstractService):
    """Holds information and methods to interact with www.deepl.com."""

    URL: str = r"https://www.deepl.com/"
    SRC_TEXTAREA_PATH: str = r"textarea[dl-test='translator-source-input']"
    TGT_TEXTAREA_PATH: str = r"textarea[dl-test='translator-target-input']"

    PAYWALL_DIV_PATH: str = r"div[class='lmt__notification__blocked_content']"
    SRC_LANG_LIST_PATH: str = r"div[dl-test='translator-source-lang-list'] > .lmt__language_wrapper > .lmt__language_select_column > *"
    SRC_LANG_LIST_BTN_PATH: str = r"button[dl-test='translator-source-lang-btn']"
    TGT_LANG_LIST_BTN_PATH: str = r"button[dl-test='translator-target-lang-btn']"
    LANG_SWITCH_BTN_PATH: str = r"button[class='lmt__language_container_switch']"

    def __init__(self, browser: AbstractBrowser):
        super().__init__(
            browser=browser,
            translation_service_url=self.URL,
            src_textarea_path=self.SRC_TEXTAREA_PATH,
            tgt_textarea_path=self.TGT_TEXTAREA_PATH
        )

    def _is_paywall_visible(self) -> bool:
        try:
            self._search_element(self.PAYWALL_DIV_PATH)
            return True
        except TimeoutException:
            return False

    def _get_translation(self, from_text: str) -> str:
        # wait for the text to refresh - this is useful if target and source lang have been swapped right before this
        if from_text in self._tgt_textarea.get_attribute('value'):
            self._wait_30_sec.until_not(text_to_be_present_in_element(self._tgt_textarea, from_text))

        # wait for the translation to appear
        self._wait_30_sec.until(TextNotPresentAndLongerThan(self._tgt_textarea, '[...]', 2))

        translation = self._tgt_textarea.get_attribute('value')
        self._src_textarea.clear()
        return translation

    def _get_supported_languages(self) -> dict:
        # show language list
        self._search_element(self.SRC_LANG_LIST_BTN_PATH).click()

        # get the list of source languages
        src_lang_buttons: list[WebElement] = \
            self._wait_30_sec.until(visibility_of_all_elements_located((By.CSS_SELECTOR, self.SRC_LANG_LIST_PATH)))

        # get supported languages from list
        supported_languages: dict = {}
        for button in src_lang_buttons:
            language = button.text.split(" (")[0]  # used only for auto language detection: it has braces
            language_id = button.get_attribute("dl-test").split("-")[3]
            supported_languages[language_id] = language

        # hide language list
        self._search_element(self.SRC_LANG_LIST_BTN_PATH).click()
        return supported_languages

    def _get_source_language(self) -> str:
        src_language = self._search_element(self.SRC_LANG_LIST_BTN_PATH).text
        # DeepL has weird behaviour here: we need to remove overlapping text, which is separated by line breaks
        src_language = src_language if '\n' not in src_language else src_language.split('\n')[1]
        # return the source language's key
        return list(self._supported_langs.keys())[list(self._supported_langs.values()).index(src_language)]

    def _get_target_language(self) -> str:
        tgt_lang_list_btn_text: str = self._search_element(self.TGT_LANG_LIST_BTN_PATH).text
        for language in self._supported_langs.values():
            # we want to search only for those values that are in our supported_languages
            if language in tgt_lang_list_btn_text:
                return list(self._supported_langs.keys())[list(self._supported_langs.values()).index(language)]

    def _set_source_language(self, src_lang) -> None:
        if not self.is_language_supported(src_lang):
            raise ValueError("Source language not supported!")

        if src_lang != self._current_src_lang:  # skip changing if its already selected
            self._search_element(self.SRC_LANG_LIST_BTN_PATH).click()
            self._search_element(f"button[dl-test='translator-lang-option-{src_lang.lower()}']").click()
            self._current_src_lang = src_lang

    def _set_target_language(self, tgt_lang) -> None:
        if not self.is_language_supported(tgt_lang):
            raise ValueError("Target language not supported!")

        if tgt_lang != self._current_tgt_lang:  # skip changing if its already selected
            if tgt_lang != self._current_src_lang:
                self._search_element(self.TGT_LANG_LIST_BTN_PATH).click()
                if tgt_lang == 'en':
                    try:  # deepL can't translate every language to english dialects, so try to select US at first
                        self._search_element(
                            f"button[dl-test='translator-lang-option-{tgt_lang.lower()}-{'US'}']"
                        ).click()
                    except TimeoutException:  # if unsuccessful, select standard english
                        self._search_element(
                            f"button[dl-test='translator-lang-option-{tgt_lang.lower()}-{'EN'}']"
                        ).click()
                else:
                    self._search_element(
                        f"button[dl-test='translator-lang-option-{tgt_lang.lower()}-{tgt_lang.upper()}']"
                    ).click()
                self._current_tgt_lang = tgt_lang

    def _set_languages(self, src_lang, tgt_lang) -> None:
        if not self.is_language_supported(src_lang):
            raise ValueError("Source language not supported!")
        if not self.is_language_supported(tgt_lang):
            raise ValueError("Target language not supported!")

        # use the websites' button to change languages if they are in reversed order
        if src_lang == self._current_src_lang and tgt_lang == self._current_src_lang:
            self._switch_languages()
        else:
            self._set_source_language(src_lang)
            self._set_target_language(tgt_lang)

    def _switch_languages(self) -> None:
        # first, switch languages on webpage then switch class variables too
        self._search_element(self.LANG_SWITCH_BTN_PATH).click()
        self._current_src_lang, self._current_tgt_lang = self._current_tgt_lang, self._current_src_lang


class Google(AbstractService):
    """Holds information and methods to interact with translate.google.com."""
    pass  # TODO
