from apis.translatorapi import DeepL
from seleniumbrowsers.browsers import Edge

a: DeepL = Edge(DeepL, headless=False).api
print(a.get_supported_languages())
print(a.source_language)
