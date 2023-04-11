# jitenbot
Jitenbot is a program for scraping Japanese dictionary websites and converting the scraped data into structured dictionary files.

### Target Websites

* [四字熟語辞典オンライン](https://yoji.jitenon.jp/)
* [故事・ことわざ・慣用句オンライン](https://kotowaza.jitenon.jp/)

### Export Formats

* [Yomichan](https://github.com/foosoft/yomichan)

# Usage
Add your desired HTTP request headers to [config.json](https://github.com/stephenmk/jitenbot/blob/main/config.json)
and ensure that all [requirements](https://github.com/stephenmk/jitenbot/blob/main/requirements.txt)
are installed.

```
jitenbot [-h] {all,jitenon-yoji,jitenon-kotowaza}

positional arguments:
  {all,jitenon-yoji,jitenon-kotowaza}
                        website to crawl

options:
  -h, --help            show this help message and exit
```

Scraped webpages are written to a `webcache` directory. Each page may be as large as a megabyte,
and a single dictionary may include thousands of pages. Ensure that adequate disk space is available.

Jitenbot will pause for at least 10 seconds between each web request. Depending upon the size of
the target dictionary, it make take hours or days to finish scraping.

Exported dictionary files will be saved in an `output` directory.
