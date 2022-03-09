from pywebtranslator.browsers.abstractbrowser import AbstractBrowser
from pywebtranslator.services.translationservice import TranslationService


class TranslationServicePool:
    """A class which manages multiple translation services. It simultaneous creates as many of them as needed."""
    __pool: list[TranslationService] = []

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

    # hopefully this mechanism creates at most as many services as needed and not more
    def claim(self) -> TranslationService:
        """Returns a service from the pool or creates a new one if all services are in use."""

        if len(self.__pool) <= 0:
            return self.service_type(self.browser_type(is_headless=self.is_headless), self.timeout_threshold)
        else:
            return self.__pool.pop()

    def stash(self, service: TranslationService) -> None:
        """
        Stashes a service back into the pool.
        :param service The service to stash. Make sure it is not accessed after this call!
        """
        self.__pool.append(service)

    def quit(self) -> None:
        """Quits every service and its associated browser session."""
        for service in self.__pool:
            service.quit()
