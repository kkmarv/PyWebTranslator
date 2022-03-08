from pywebtranslator.browsers.abstractbrowser import AbstractBrowser
from pywebtranslator.services.translationservice import TranslationService
from pywebtranslator.expectations.expectations import IsTextPresent, TextNotPresent, TextNotPresentAndLongerThan

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement


class DeepL(TranslationService):
    """Holds information and methods to interact with www.deepl.com."""

    URL = r"https://www.deepl.com/"
    SRC_TEXTAREA = r"textarea[dl-test='translator-source-input']"
    TGT_TEXTAREA = r"textarea[dl-test='translator-target-input']"

    PAYWALL_DIV: str = r"div[class='lmt__notification__blocked_content']"
    SRC_LANG_LIST: str = r".lmt__language_wrapper > .lmt__language_select_column > *"
    SRC_LANG_LIST_DIV: str = r"div[dl-test='translator-source-lang-list']"
    SRC_LANG_LIST_BTN: str = r"button[dl-test='translator-source-lang-btn']"
    TGT_LANG_LIST_BTN: str = r"button[dl-test='translator-target-lang-btn']"
    SWITCH_LANG_DIV: str = r"div[class='lmt__language_container_switch']"

    def __init__(self, browser: AbstractBrowser, timeout_threshold=30):
        super().__init__(
            browser=browser,
            translation_service_url=self.URL,
            src_textarea=self.SRC_TEXTAREA,
            tgt_textarea=self.TGT_TEXTAREA,
            timeout_threshold=timeout_threshold
        )

    def _is_paywall_visible(self) -> bool:
        try:
            self.search_css(self.PAYWALL_DIV)
            return True
        except TimeoutException:
            return False

    def _get_translation(self, from_text: str) -> str:
        # wait for the text to refresh
        if from_text in self._tgt_textarea.get_attribute('value'):
            self._wait_for_translation.until(TextNotPresent(self._tgt_textarea, from_text))

        # wait for the translation to appear
        self._wait_for_translation.until(TextNotPresentAndLongerThan(self._tgt_textarea, '[...]', 2))

        translation = self._tgt_textarea.get_attribute('value')
        self._src_textarea.clear()
        return translation

    def _get_supported_languages(self) -> dict:
        # show language list
        self.search_css(self.SRC_LANG_LIST_BTN).click()

        # get the source language list
        src_lang_list_div: WebElement = self.search_css(self.SRC_LANG_LIST_DIV)
        src_lang_list: list[WebElement] = src_lang_list_div.find_elements(By.CSS_SELECTOR, self.SRC_LANG_LIST)

        # get supported languages from list
        supported_languages: dict = {}
        for button in src_lang_list:
            self._wait_for_ui.until(IsTextPresent(button))
            language = button.text.split(" (")[0]  # used for auto detection which has braces
            language_id = button.get_attribute("dl-test").split("-")[3]
            supported_languages[language_id] = language

        # hide language list
        self.search_css(self.SRC_LANG_LIST_BTN).click()
        return supported_languages

    def _get_source_language(self) -> str:
        src_language = self.search_css(self.SRC_LANG_LIST_BTN).text
        # DeepL has weird behaviour here: we need to remove overlapped text which is separated by a line break
        src_language = src_language if '\n' not in src_language else src_language.split('\n')[1]

        # return the source language's key
        return list(self._supported_langs.keys())[list(self._supported_langs.values()).index(src_language)]

    def _get_target_language(self) -> str:
        tgt_lang_list_btn_text: str = self.search_css(self.TGT_LANG_LIST_BTN).text
        for language in self._supported_langs.values():
            # we want to search only for those values that are in our supported_languages
            if language in tgt_lang_list_btn_text:
                return list(self._supported_langs.keys())[list(self._supported_langs.values()).index(language)]

    def _set_source_language(self, src_lang) -> None:
        if not self.is_language_supported(src_lang):
            raise ValueError("Source language not supported!")

        if src_lang != self._current_src_lang:  # skip changing if its already selected
            self.search_css(self.SRC_LANG_LIST_BTN).click()
            self.search_css(f"button[dl-test='translator-lang-option-{src_lang.lower()}']").click()
            self._current_src_lang = src_lang

    def _set_target_language(self, tgt_lang) -> None:
        if not self.is_language_supported(tgt_lang):
            raise ValueError("Target language not supported!")

        if tgt_lang != self._current_tgt_lang:  # skip changing if its already selected
            if tgt_lang != self._current_src_lang:
                self.search_css(self.TGT_LANG_LIST_BTN).click()
                if tgt_lang == 'en':
                    try:  # deepL can't translate every language to english dialects, so try to select US at first
                        self.search_css(
                            f"button[dl-test='translator-lang-option-{tgt_lang.lower()}-{'US'}']"
                        ).click()
                    except TimeoutException:  # if unsuccessful, select standard english
                        self.search_css(
                            f"button[dl-test='translator-lang-option-{tgt_lang.lower()}-{tgt_lang.upper()}']"
                        ).click()
                else:
                    self.search_css(
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
        self.search_css(self.SWITCH_LANG_DIV).click()
        # switch class variables too
        self._current_src_lang, self._current_tgt_lang = self._current_tgt_lang, self._current_src_lang
