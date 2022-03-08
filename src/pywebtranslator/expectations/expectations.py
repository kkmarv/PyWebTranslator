from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


# TODO rewrite this old selenium syntax to normal functions

class IsTextPresent:
    """An expectation for checking if any text is present in the web elements value."""

    def __init__(self, element: WebElement):
        self.element: WebElement = element

    def __call__(self, driver):
        return self.element if len(self.element.text) > 0 else False


class TextNotPresent:
    """An expectation for checking if a given text is not present in the web elements value."""

    def __init__(self, element: WebElement, text: str) -> None:
        self.element: WebElement = element
        self.text: str = text

    def __call__(self, driver: webdriver):
        element_value: str = self.element.get_attribute('value')
        return self.element if (self.text not in element_value) else False


class TextNotPresentAndLongerThan:
    """
    An expectation for checking if a given text is not present in the web elements' value attribute
    and that text, that is present, is longer than the given limit.
    """

    def __init__(self, element: WebElement, text: str, limit: int) -> None:
        self.element: WebElement = element
        self.text: str = text
        self.limit = limit

    def __call__(self, driver: webdriver):
        element_value: str = self.element.get_attribute('value')
        return self.element if (self.text not in element_value) and (len(element_value) >= self.limit) else False
