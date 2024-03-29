from code.drivers import Driver
from code.services import TranslationService


class TranslationServicePool:
    """
    A context manager for multiple TranslationService objects.
    It creates simultaneous as many TranslationService objects as needed.
    """

    _pool: list[TranslationService] = []
    _services: list[TranslationService] = []

    def __init__(self, service_type: TranslationService.__class__, driver_type: Driver.__class__, is_headless=True):
        self.service_type = service_type
        self.driver_type = driver_type
        self.is_headless = is_headless

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    # hopefully this mechanism creates at most as many services as needed and not more
    def claim(self) -> TranslationService:
        """Returns a service from the pool or creates a new one if all services are in use."""
        if len(self._pool) <= 0:
            ts_service = self.service_type(self.driver_type(is_headless=self.is_headless))
            self._services.append(ts_service)
            self._pool.append(ts_service)
        return self._pool.pop()

    def stash(self, service: TranslationService) -> None:
        """Stashes a service back into the pool.
        :param service The service to stash. Make sure it is not accessed after this call!"""
        self._pool.append(service)

    def translate(self, txt: str, src_lang: str, tgt_lang: str) -> str:
        """Queries a single translation."""
        service = self.claim()
        translation = service.translate(txt, source_language=src_lang, target_language=tgt_lang)
        self.stash(service)
        return translation

    def quit(self) -> None:
        for service in self._services:
            service.quit()  # TODO not always closing when error or ctrl+c
