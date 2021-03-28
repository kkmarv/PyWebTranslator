class TextNotPresentAndTextShorterThan:
    """
    An expectation for checking if a given text is not present in the web element nor shorter than given limit.
    """

    def __init__(self, element, text, limit):
        self.element = element
        self.text = text
        self.limit = limit

    def __call__(self, driver):
        if (self.text not in self.element.get_attribute('value')) and (
                len(self.element.get_attribute('value')) >= self.limit):
            return self.element
        else:
            return False


class TextIsPresent:
    """
    An expectation for checking if text is present in the web elements value.
    """

    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        if len(self.element.text) > 0:
            return self.element
        else:
            return False
