from .browser import AbstractBrowser
from .services import AbstractService


class TranslationServicePool:
    """A context manager for multiple TranslationService objects. It simultaneous creates as many of them as needed."""

    __pool: list[AbstractService] = []
    __services: list[AbstractService] = []

    def __init__(self,
                 service_type: AbstractService.__class__,
                 browser_type: AbstractBrowser.__class__,
                 is_headless=True):
        self.is_headless: bool = is_headless
        self.service_type: AbstractService.__class__ = service_type
        self.browser_type: AbstractBrowser.__class__ = browser_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    # hopefully this mechanism creates at most as many services as needed and not more
    def claim(self) -> AbstractService:
        """Returns a service from the pool or creates a new one if all services are in use."""
        if len(self.__pool) <= 0:
            ts_service = self.service_type(self.browser_type(is_headless=self.is_headless))
            self.__services.append(ts_service)
            self.__pool.append(ts_service)
        return self.__pool.pop()

    def stash(self, service: AbstractService) -> None:
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
        for service in self.__services:
            service.quit()  # TODO not always closing when error or ctrl+c
