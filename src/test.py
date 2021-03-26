from apis.translatorapi import DeepL
from seleniumbrowsers.browsers import Firefox

b = (Firefox(DeepL, headless=False))
a: DeepL = b.api

print(a.supported_languages)

print(a.source_language)
print(a.target_language)

a.source_language = "de"
a.target_language = "ru"

# TODO find out about "Translate from" bug
print(a.source_language)  # TODO fix "Translate from" bug
print(a.target_language)
print(a.translate("Hallo"))
