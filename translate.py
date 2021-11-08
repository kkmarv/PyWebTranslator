from web.browsers import Firefox
from web.services import DeepL

from time import sleep


"""
Example use:
"""

if __name__ == "__main__":
    translator = DeepL(Firefox(is_headless=False, stay_open=True))

    # get all languages the website offers for translation
    print(translator.supported_languages)

    # get current source and target language
    print(translator.source_language)
    print(translator.target_language)

    # translate some text
    print(translator.translate("Makes sure to quit the driver when exiting the program.", "en", "de"))
    sleep(5)

    print(translator.translate("fils de pute", source_language="da", target_language="de"))
    sleep(5)

    print(translator.translate("Passi ist eine kleine Spinne.", source_language="de", target_language="da"))
    sleep(5)

    print(translator.translate("Passi er en lille edderkop.", target_language="da", source_language="en"))
    sleep(1)
