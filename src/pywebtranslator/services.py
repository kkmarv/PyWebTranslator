from abc import ABC, abstractmethod
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from selenium.webdriver.support.wait import WebDriverWait

from .drivers import Driver
from .errors import BadSourceLanguageError, BadTargetLanguageError
from .expectations import TextNotPresentAndLongerThan


class TranslationService(ABC):
    """Translation service base class. Use a specific TranslationService class to start translating."""

    URL: str = ...
    CSS: dict[str, str | list[str]] = ...

    def __init__(self,
                 driver: Driver,
                 service_url: str,
                 src_textarea: str,
                 tgt_textarea: str,
                 allow_perf_cookies=False):
        """Calls given URL in given browser and sets up the website for the translation process.

        :param driver:              The Browser class to use.
        :param service_url:         URL of the specified translation service.
        :param src_textarea:        CSS path to the source language textarea within the website.
        :param tgt_textarea:        CSS path to the target language textarea within the website.
        :param allow_perf_cookies:  Whether to accept the websites performances cookies.
                                    for a possible translation speed up. May not work for all services."""

        # instantiate a browser
        self._driver = driver
        self._driver.set_url(service_url)

        if allow_perf_cookies:
            self._accept_perf_cookies()

        # get the text areas that are relevant for translating
        self._src_textarea: WebElement = self._driver.search_elem(src_textarea)
        self._tgt_textarea: WebElement = self._driver.search_elem(tgt_textarea)

        # initialize current selected languages
        self.sup_langs: dict = self._get_sup_langs()
        self.src_lang: str = self._get_current_src_lang()
        self.tgt_lang: str = self._get_current_tgt_lang()

        # initialize timeout threshold, 30 sec is a good enough fit for DeepL
        self._wait_for_translation: WebDriverWait = WebDriverWait(self._driver.driver, 30)

        super().__init__()

    def is_src_lang_supported(self, language: str) -> bool:
        """Checks with the list of source languages on the website and returns if given language is supported.

        :param language:    The language to check if it is supported.
        :return:            Whether the given language is supported as a source language by this service or not."""
        return language is not None and language in self.sup_langs['src_langs'].keys()

    def is_tgt_lang_supported(self, language: str) -> bool:
        """Checks with the list of target languages on the website and returns if given language is supported.

        :param language:    The language to check if it is supported.
        :return:            Whether the given language is supported as a target language by this service or not."""
        return language is not None and language in self.sup_langs['tgt_langs'].keys()

    def translate(self, text: str, source_language: str, target_language: str, fallback: Optional[str] = None) -> str:
        """Parses given text to website, calls _get_translation() and returns its result.

        :return: The translated text or an empty string if _get_translation() times out."""
        if len(text) <= 1:  # return text if its just one letter
            return text

        self._driver.discard_tabs()
        self._set_langs(source_language, target_language)

        # send the text to the website
        self._src_textarea.send_keys(text)

        try:  # await translation
            return self._get_translation(text)
        except TimeoutException as te:
            if fallback:
                return fallback
            else:
                raise te

    def quit(self) -> None:
        """Quits the translation service and its associated browser session."""
        self._driver.driver.quit()

    def _accept_perf_cookies(self) -> None:
        """Accepts performance cookies for possible faster translation. May not work for all services."""
        for btn in self.CSS['cookie_btn_list']:
            self._driver.click_elem(btn)

    # Abstract methods

    @abstractmethod
    def _get_translation(self, from_text: str) -> str:
        """Defines the procedure to retrieve a translation from the website."""
        ...

    @abstractmethod
    def _get_sup_langs(self) -> dict[str, dict[str, str]]:
        """Defines the procedure to get all supported languages from the website."""
        ...

    @abstractmethod
    def _get_current_src_lang(self) -> str:
        """Defines the procedure to get the current input source language from the website."""
        ...

    @abstractmethod
    def _get_current_tgt_lang(self) -> str:
        """Defines the procedure to get the current output target language from the website."""
        ...

    @abstractmethod
    def _set_src_lang(self, language) -> None:
        """Defines the procedure to set a new source language on the website."""
        ...

    @abstractmethod
    def _set_tgt_lang(self, language) -> None:
        """Defines the procedure to set a new target language on the website."""
        ...

    @abstractmethod
    def _set_langs(self, src_lang, tgt_lang) -> None:
        """Defines the procedure to set both languages at once on the website."""
        ...

    @abstractmethod
    def _switch_langs(self) -> None:
        """Defines the procedure to switch target with source language on the website."""
        ...


class DeepL(TranslationService):
    """Holds information and methods to interact with www.deepl.com."""

    URL = r"https://www.deepl.com/translate"
    CSS = {
        'src_textarea': r"textarea[dl-test='translator-source-input']",
        'tgt_textarea': r"textarea[dl-test='translator-target-input']",
        'paywall_div': r"div[class='lmt__notification__blocked_content']",
        'src_lang_list': r"div[dl-test='translator-source-lang-list'] > .lmt__language_wrapper > .lmt__language_select_column > *",
        'tgt_lang_list': r"div[dl-test='translator-target-lang-list'] > .lmt__language_wrapper > .lmt__language_select_column > *",
        'src_lang_list_btn': r"button[dl-test='translator-source-lang-btn']",
        'tgt_lang_list_btn': r"button[dl-test='translator-target-lang-btn']",
        'lang_switch_btn': r"button[data-testid='deepl-ui-tooltip-target']",
        'cookie_btn_list': [
            r"input[id='cookie-checkbox-performance']",  # select performance cookies
            r"button[class='dl_cookieBanner--buttonSelected']"  # accept selected cookies
        ]
    }

    def __init__(self, driver: Driver):
        super().__init__(
            driver=driver,
            service_url=self.URL,
            src_textarea=self.CSS['src_textarea'],
            tgt_textarea=self.CSS['tgt_textarea']
        )

    def _is_paywall_visible(self) -> bool:
        try:
            self._driver.search_elem(self.CSS['paywall_div'])
            return True
        except TimeoutException:
            return False

    def _get_translation(self, from_text: str) -> str:
        # wait for the text to refresh - this is useful if target and source lang have been swapped right before this
        if from_text in self._tgt_textarea.get_attribute('value'):
            self._wait_for_translation.until_not(text_to_be_present_in_element(self._tgt_textarea, from_text))

        # wait for the translation to appear
        self._wait_for_translation.until(TextNotPresentAndLongerThan(self._tgt_textarea, '[...]', 2))

        translation = self._tgt_textarea.get_attribute('value')
        self._src_textarea.clear()
        return translation

    def _get_sup_langs(self) -> dict[str, dict[str, str]]:
        # get supported languages from list
        supported_languages = {'src_langs': {}, 'tgt_langs': {}}

        # show src language list and get the list of source languages
        self._driver.click_elem(self.CSS['src_lang_list_btn'])
        for btn in self._driver.search_elems(self.CSS['src_lang_list']):
            lang_id = '-'.join(btn.get_attribute('dl-test').split('-')[3:])
            supported_languages['src_langs'][lang_id] = btn.text
        self._driver.click_elem(self.CSS['src_lang_list_btn'])

        # show tgt language list and get the list of target languages
        self._driver.click_elem(self.CSS['tgt_lang_list_btn'])
        for btn in self._driver.search_elems(self.CSS['tgt_lang_list']):
            lang_id = '-'.join(btn.get_attribute('dl-test').split('-')[3:])
            supported_languages['tgt_langs'][lang_id] = btn.text
        self._driver.click_elem(self.CSS['tgt_lang_list_btn'])

        return supported_languages

    def _get_current_src_lang(self) -> str:
        cur_src_language: str = self._driver.search_elem(self.CSS['src_lang_list_btn']).text
        # DeepL has weird behaviour here: we need to remove overlapping text, which is separated by line breaks
        cur_src_language = cur_src_language if '\n' not in cur_src_language else cur_src_language.split('\n')[1]
        # return the source language's key
        return list(self.sup_langs['src_langs'].keys())[
            list(self.sup_langs['src_langs'].values()).index(cur_src_language)]

    def _get_current_tgt_lang(self) -> str:
        tgt_lang_list_btn_text: str = self._driver.search_elem(self.CSS['tgt_lang_list_btn']).text
        for language in self.sup_langs['tgt_langs'].values():
            # we want to search only for those values that are in our supported_languages
            if language in tgt_lang_list_btn_text:
                return list(self.sup_langs['tgt_langs'].keys())[
                    list(self.sup_langs['tgt_langs'].values()).index(language)]

    def _set_src_lang(self, src_lang: str) -> None:
        src_lang = src_lang.lower()

        if not self.is_src_lang_supported(src_lang):
            raise BadSourceLanguageError('DeepL', src_lang)

        if src_lang != self.src_lang:  # skip changing if its already selected
            self._driver.click_elem(self.CSS['src_lang_list_btn'])
            self._driver.click_elem(f"button[dl-test='translator-lang-option-{src_lang}']")
            self.src_lang = src_lang

    def _set_tgt_lang(self, tgt_lang: str) -> None:
        tgt_lang = tgt_lang.lower()

        if tgt_lang != self.tgt_lang and tgt_lang != self.src_lang:  # skip changing if its already selected
            self._driver.click_elem(self.CSS['tgt_lang_list_btn'])
            if tgt_lang == 'en':  # unless specified otherwise, translate to standard english
                try:
                    self._driver.click_elem(f"button[dl-test='translator-lang-option-en-GB']")
                except TimeoutException:  # some languages cannot be translated into dialects
                    self._driver.click_elem(f"button[dl-test='translator-lang-option-en']")
            elif tgt_lang == 'pt':  # unless specified otherwise, translate to standard portuguese
                try:
                    self._driver.click_elem(f"button[dl-test='translator-lang-option-pt-PT']")
                except TimeoutException:  # some languages cannot be translated into dialects
                    self._driver.click_elem(f"button[dl-test='translator-lang-option-pt']")
            elif not self.is_tgt_lang_supported(tgt_lang):
                raise BadTargetLanguageError('DeepL', tgt_lang)
            else:
                self._driver.click_elem(f"button[dl-test='translator-lang-option-{tgt_lang}']")
            self.tgt_lang = tgt_lang

    def _set_langs(self, src_lang: str, tgt_lang: str) -> None:
        # use the websites' button to change languages if they are in reversed order
        if src_lang == self.tgt_lang and tgt_lang == self.src_lang:
            self._switch_langs()
        else:
            self._set_src_lang(src_lang)
            self._set_tgt_lang(tgt_lang)

    def _switch_langs(self) -> None:
        # first, switch languages on webpage then switch class variables too
        self._driver.click_elem(self.CSS['lang_switch_btn'])
        self.src_lang, self.tgt_lang = self.tgt_lang, self.src_lang


class GoogleTranslate(TranslationService):
    """Holds information and methods to interact with translate.google.com."""

    def __init__(self):
        raise NotImplementedError
