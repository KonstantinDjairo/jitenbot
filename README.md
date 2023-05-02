# jitenbot
Jitenbot is a program for scraping Japanese dictionary websites and
compiling the scraped data into compact dictionary file formats.

### Supported Dictionaries
* Online
  * [四字熟語辞典オンライン](https://yoji.jitenon.jp/)
  * [故事・ことわざ・慣用句オンライン](https://kotowaza.jitenon.jp/)
* Offline
  * [新明解国語辞典 第八版](https://www.monokakido.jp/ja/dictionaries/smk8/index.html)
  * [大辞林 第四版](https://www.monokakido.jp/ja/dictionaries/daijirin2/index.html)

### Supported Output Formats

* [Yomichan](https://github.com/foosoft/yomichan)

# Usage
```
usage: jitenbot [-h] [-p PAGE_DIR] [-i IMAGE_DIR]
                {jitenon-yoji,jitenon-kotowaza,smk8,daijirin2}

Convert Japanese dictionary files to new formats.

positional arguments:
  {jitenon-yoji,jitenon-kotowaza,smk8,daijirin2}
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
a complete crawl of a target website may take several hours.

HTTP request headers (user agent string, etc.) may be customized by editing the `config.json` file created in the
[user config directory](https://pypi.org/project/platformdirs/).

### Offline Targets
Page data and image data must be procured by the user
and passed to jitenbot via the appropriate command line flags.

# Attribution
`Adobe-Japan1_sequences.txt` is provided by [The Adobe-Japan1-7 Character Collection](https://github.com/adobe-type-tools/Adobe-Japan1).

# Examples

### 四字熟語辞典オンライン
<details>
  <summary>白玉微瑕 (web)</summary>
  
  ![yoji_hakugyokunobika_web](https://user-images.githubusercontent.com/8003332/235552346-50862906-df26-41a6-aa8f-c8b7e3df0e60.png)
</details>

<details>
  <summary>白玉微瑕 (yomichan)</summary>
  
  ![yoji_hakugyokunobika](https://user-images.githubusercontent.com/8003332/235552362-c187c241-930e-4dff-b046-d72272272b6b.png)
</details>

---

### 故事・ことわざ・慣用句オンライン
<details>
  <summary>怒髪、冠を衝く (web)</summary>
  
  ![kotowaza_dohatsu_web](https://user-images.githubusercontent.com/8003332/235552184-893bc0f7-83ef-4d4c-bc43-59cf81971419.png)
</details>

<details>
  <summary>怒髪、冠を衝く (yomichan)</summary>
  
  ![kotowaza_dohatsu_yomi](https://user-images.githubusercontent.com/8003332/235552202-1301a875-ca39-4ce1-896f-64c26915a5ac.png)
</details>

---

### 新明解国語辞典 第八版
<details>
  <summary>離れる (print)</summary>
  
  ![smk8_hanareru_print](https://user-images.githubusercontent.com/8003332/235550560-e32f1ac8-2333-4ed9-adfc-a8e47ba187a0.png)
</details>

<details>
  <summary>離れる (yomichan)</summary>
  
  ![smk8_hanareru_yomichan](https://user-images.githubusercontent.com/8003332/235550676-024a0d82-b695-45e8-96e8-b8a4f5bf4ffb.png)
</details>

---

### 大辞林 第四版
<details>
  <summary>令月 (print)</summary>
  
  ![daijirin_reigetsu_print](https://user-images.githubusercontent.com/8003332/235550833-5ca99ab8-1255-419f-ae86-228b57b3da02.png)
</details>

<details>
  <summary>令月 (yomichan)</summary>
  
  ![daijirin_reigetsu_yomichan](https://user-images.githubusercontent.com/8003332/235550802-4d008264-205a-4fc2-9bf5-6af31cf7b910.png)
</details>
