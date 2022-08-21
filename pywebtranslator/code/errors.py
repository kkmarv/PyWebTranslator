class BadSourceLanguageError(ValueError):
    """
    Exception class for letting you know that
    the input language you used isn't supported by this translation service.
    """

    def __init__(self, service_name: str, src_lang: str):
        super().__init__(f"{service_name} currently does not support '{src_lang}' as a source language.")


class BadTargetLanguageError(ValueError):
    """
    Exception class for letting you know that
    the output language you used isn't supported by this translation service.
    """

    def __init__(self, service_name: str, tgt_lang: str):
        super().__init__(f"{service_name} currently does not support '{tgt_lang}' as a target language.")
