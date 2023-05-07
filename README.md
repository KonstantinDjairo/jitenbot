# jitenbot
Jitenbot is a program for scraping Japanese dictionary websites and
compiling the scraped data into compact dictionary file formats.

### Supported Dictionaries
* Online
  * [国語辞典オンライン](https://kokugo.jitenon.jp/)
  * [四字熟語辞典オンライン](https://yoji.jitenon.jp/)
  * [故事・ことわざ・慣用句オンライン](https://kotowaza.jitenon.jp/)
* Offline
  * [新明解国語辞典 第八版](https://www.monokakido.jp/ja/dictionaries/smk8/index.html)
  * [大辞林 第四版](https://www.monokakido.jp/ja/dictionaries/daijirin2/index.html)

### Supported Output Formats

* [Yomichan](https://github.com/foosoft/yomichan)

# Examples

<details>
  <summary>国語辞典オンライン (web | yomichan)</summary>
  
  ![jitenon_kokugo](https://user-images.githubusercontent.com/8003332/236656018-631aae07-55fa-4f27-ba53-18952cf01b90.png)
</details>

<details>
  <summary>四字熟語辞典オンライン (web | yomichan)</summary>
  
  ![yoji](https://user-images.githubusercontent.com/8003332/235578611-b89bf707-01a7-4887-a4d3-250346501361.png)
</details>

<details>
  <summary>故事・ことわざ・慣用句オンライン (web | yomichan)</summary>
  
  ![kotowaza](https://user-images.githubusercontent.com/8003332/235578632-f33ea8fa-8d5f-49f9-bc78-6bff7b6bf9c9.png)
</details>

### 
<details>
  <summary>新明解国語辞典 第八版 (print | yomichan)</summary>
  
  ![smk8](https://user-images.githubusercontent.com/8003332/235578664-906a31bb-ee75-4c25-becc-37968dc2eab6.png)
</details>

### 
<details>
  <summary>大辞林 第四版 (print | yomichan)</summary>
  
  ![daijirin2](https://user-images.githubusercontent.com/8003332/235578700-9dbf4fb0-0154-48b5-817c-8fe75e442afc.png)
</details>

# Usage
```
usage: jitenbot [-h] [-p PAGE_DIR] [-i IMAGE_DIR]
                {jitenon-kokugo,jitenon-yoji,jitenon-kotowaza,smk8,daijirin2}

Convert Japanese dictionary files to new formats.

positional arguments:
  {jitenon-kokugo,jitenon-yoji,jitenon-kotowaza,smk8,daijirin2}
                        name of dictionary to convert

options:
  -h, --help            show this help message and exit
  -p PAGE_DIR, --page-dir PAGE_DIR
                        path to directory containing XML page files
  -i IMAGE_DIR, --image-dir IMAGE_DIR
                        path to directory containing image folders (gaiji,
                        graphics, etc.)
```
### Online Targets
Jitenbot will scrape the target website and save the pages to the [user cache directory](https://pypi.org/project/platformdirs/).
As a courtesy to the website owners, jitenbot is configured to pause for 10 seconds between each page request. Consequently, 
a complete crawl of a target website may take several days.

HTTP request headers (user agent string, etc.) may be customized by editing the `config.json` file created in the
[user config directory](https://pypi.org/project/platformdirs/).

### Offline Targets
Page data and image data must be procured by the user
and passed to jitenbot via the appropriate command line flags.

# Attribution
`Adobe-Japan1_sequences.txt` is provided by [The Adobe-Japan1-7 Character Collection](https://github.com/adobe-type-tools/Adobe-Japan1).
