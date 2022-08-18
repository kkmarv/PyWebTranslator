# PyWebTranslator

The PyWebTranslator is a small web scraping library that allows to use any online translation service on the command
line (WiP) or in your own project.

### Background

This project started as a personal bet between me and a friend from university that was about whether we'd be able to
fully translate a huge mod called [Russian Universalis](https://steamcommunity.com/workshop/filedetails/?id=1862741477)
for the game [Europa Universalis 4](https://www.paradoxinteractive.com/games/europa-universalis-iv/about).

When we started together both of us only had the most basic programming knowledge. Even though we achieved a [somewhat
enjoyable translation](https://steamcommunity.com/sharedfiles/filedetails/?id=2101033804) into English, the code wasn't
perfect. It mostly missed a proper architecture ie. it was hard to support more languages, more translation services,
browsers and so on.  
Eventually we parted our ways, but since then I learned a lot and continued to maintain this project with new
concepts and techniques I've learned along the way.

## Disclaimer

The people behind [DeepL](https://www.deepl.com/translator) offer the best online translation available by far and so
its commercial use comes at a small price. And using a web scraper isn't exactly in accordance with their terms of use
or any other service.

**So please consider this repository as educational purpose only.**

## Minimal working example

### Source code

For this example, clone the repository and create a Python source file under `PyWebTranslator/` which contains the
following lines:

```python
from src.pywebtranslator.drivers import Edge  # or Firefox
from src.pywebtranslator.services import DeepL

browser = Edge()
translator = DeepL(browser)
```

### CLI

ToDo
