from apis.translatorapi import DeepL
from seleniumbrowsers.browsers import Edge

b: Edge = (Edge(DeepL, headless=False))
a: DeepL = b.api

print(a.supported_languages)

print(a.source_language)
print(a.target_language)

a.source_language = "de"

print(a.source_language)
print(a.target_language)
print(a.translate("Hallo"))
"""print(a.supported_languages)
a.source_language = "de"
print(a.source_language)"""
