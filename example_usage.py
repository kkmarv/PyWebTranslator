from pywebtranslator.services.deepl import DeepL
from pywebtranslator.browsers.firefox import Firefox
from pywebtranslator.browsers.edge import Edge
from pywebtranslator.threading import TranslationServicePool


if __name__ == "__main__":
    with TranslationServicePool(service_type=DeepL, browser_type=Edge) as tsp:
        print(tsp.translate("Wasser, Zucker, Orangensaftkonzentrat", "de", "en"))

    translator = DeepL(Firefox(is_headless=False))

    # get all languages the website offers to translate
    print(translator.supported_languages)

    # get current source and target language
    print(translator.source_language, translator.target_language)

    # translate some text
    print(translator.translate("Makes sure to quit the driver when exiting the program.", "en", "de"))
    print(translator.translate("fils de pute", source_language="da", target_language="de"))
    print(translator.translate("Passi ist eine kleine Spinne.", source_language="de", target_language="da"))
    print(translator.translate("Passi er en lille edderkop.", source_language="da", target_language="en"))

    # translate english stuff
    print(translator.translate("Eine Weißwurst, bitte.", "de", "en"))
    print(translator.translate("Hello", "en", "de"))
    print(translator.translate("Eine Weißwurst, bitte.", "de", "ru"))

    # translate text in same language but fast
    print(translator.translate("Hello", source_language="en", target_language="de"))
    print(translator.translate("I", source_language="en", target_language="de"))
    print(translator.translate("am", source_language="en", target_language="de"))
    print(translator.translate("your", source_language="en", target_language="de"))
    print(translator.translate("mum", source_language="en", target_language="de"))
    print(translator.translate("and", source_language="en", target_language="de"))
    print(translator.translate("I", source_language="en", target_language="de"))
    print(translator.translate("will", source_language="en", target_language="de"))
    print(translator.translate("spank", source_language="en", target_language="de"))
    print(translator.translate("you", source_language="en", target_language="de"))

    # yes
    print(translator.translate("Hej I am din mor og I vil smæk du", source_language="da", target_language="ru"))
