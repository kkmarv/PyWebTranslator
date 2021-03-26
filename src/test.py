from apis.translatorapi import DeepL
from seleniumbrowsers.browsers import Edge
from seleniumbrowsers.browsers import Firefox

a = Edge(DeepL, headless=False).api
print(a.translate("Hallo"))

a = Firefox(DeepL, headless=False).api
print(a.translate("Hallo"))
