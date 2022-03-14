from pywebtranslator.browsers.abstractbrowser import AbstractBrowser
from pywebtranslator.services.translationservice import TranslationService


class TranslationServicePool:
    """A context manager for multiple TranslationService objects. It simultaneous creates as many of them as needed."""

    __pool: list[TranslationService] = []
    __services: list[TranslationService] = []

    def __init__(self,
                 service_type: TranslationService.__class__,
                 browser_type: AbstractBrowser.__class__,
                 timeout_threshold=30,
                 is_headless=True):
        self.service_type: TranslationService.__class__ = service_type
        self.browser_type: AbstractBrowser.__class__ = browser_type
        self.timeout_threshold: int = timeout_threshold
        self.is_headless: bool = is_headless

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def __create(self) -> None:
        ts_service = self.service_type(self.browser_type(is_headless=self.is_headless), self.timeout_threshold)
        self.__services.append(ts_service)
        self.__pool.append(ts_service)

    # hopefully this mechanism creates at most as many services as needed and not more
    def claim(self) -> TranslationService:
        """Returns a service from the pool or creates a new one if all services are in use."""
        if len(self.__pool) <= 0:
            self.__create()
        return self.__pool.pop()

    def stash(self, service: TranslationService) -> None:
        """Stashes a service back into the pool.
        :param service The service to stash. Make sure it is not accessed after this call!"""
        self.__pool.append(service)

    def translate(self, txt: str, src_lang: str, tgt_lang: str) -> str:
        """Queries a single translation."""
        service = self.claim()
        translation = service.translate(txt, source_language=src_lang, target_language=tgt_lang)
        self.stash(service)
        return translation

    def quit(self) -> None:
        """Quits every service and its associated browser session."""
        for service in self.__services:
            service.quit()
