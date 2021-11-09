from selenium.webdriver.remote.webelement import WebElement


class IsTextPresent:
    """
    An expectation for checking if text is present in the web elements value.
    """

    def __init__(self, element):
        self.element: WebElement = element

    def __call__(self, driver):
        if len(self.element.text) > 0:
            return self.element
        else:
            return False


class TextNotPresent:
    def __init__(self, element: WebElement, text: str) -> None:
        """
        An expectation for checking if given text is not present in the web elements value.

        :param element: The web element
        :param text: The text that the element should not contain
        """
        self.element: WebElement = element
        self.text: str = text

    def __call__(self, driver):
        element_value: str = self.element.get_attribute('value')
        return self.element if (self.text not in element_value) else False


class TextNotPresentAndTextShorterThan:
    """
    An expectation for checking if a given text is not present in the web element nor shorter than given limit.
    """

    def __init__(self, element: WebElement, text: str, limit: int) -> None:
        self.element: WebElement = element
        self.text: str = text
        self.limit = limit

    def __call__(self, driver):
        element_value: str = self.element.get_attribute('value')
        return self.element if (self.text not in element_value) and (len(element_value) >= self.limit) else False
