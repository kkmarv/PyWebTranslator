from browsers.browser import Edge
from translator import DeepL

a = DeepL(Edge)
a.source_language = "de"
a.target_language = "ru"
print(a.translate("Hallo"))
