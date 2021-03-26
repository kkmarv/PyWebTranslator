from apis.translatorapi import DeepL
from seleniumbrowsers.browsers import Edge

a = Edge(DeepL, headless=False).api
print(a.translate("Hallo"))
