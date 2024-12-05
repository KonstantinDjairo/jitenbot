# jitenbot
Jitenbot is a program for scraping Japanese dictionary websites and
compiling the scraped data into compact dictionary file formats.

### Supported Dictionaries
* Web Dictionaries
  * [国語辞典オンライン](https://kokugo.jitenon.jp/) (`jitenon-kokugo`)
  * [四字熟語辞典オンライン](https://yoji.jitenon.jp/) (`jitenon-yoji`)
  * [故事・ことわざ・慣用句オンライン](https://kotowaza.jitenon.jp/) (`jitenon-kotowaza`)
* Monokakido
  * [新明解国語辞典 第八版](https://www.monokakido.jp/ja/dictionaries/smk8/index.html) (`smk8`)
  * [大辞林 第四版](https://www.monokakido.jp/ja/dictionaries/daijirin2/index.html) (`daijirin2`)
  * [三省堂国語辞典 第八版](https://www.monokakido.jp/ja/dictionaries/sankoku8/index.html) (`sankoku8`)

### Supported Output Formats

* [Yomichan](https://github.com/foosoft/yomichan)
* MDict (.MDX & .MDD)

# Examples

<details>
  <summary>Jitenon Kokugo (web | yomichan)</summary>
  
  ![jitenon_kokugo](https://user-images.githubusercontent.com/8003332/236656018-631aae07-55fa-4f27-ba53-18952cf01b90.png)
</details>

<details>
  <summary>Jitenon Yoji (web | yomichan)</summary>
  
  ![yoji](https://user-images.githubusercontent.com/8003332/235578611-b89bf707-01a7-4887-a4d3-250346501361.png)
</details>

<details>
  <summary>Jitenon Kotowaza (web | yomichan)</summary>
  
  ![kotowaza](https://user-images.githubusercontent.com/8003332/235578632-f33ea8fa-8d5f-49f9-bc78-6bff7b6bf9c9.png)
</details>

<details>
  <summary>Shinmeikai 8e (print | yomichan)</summary>
  
  ![smk8](https://user-images.githubusercontent.com/8003332/235578664-906a31bb-ee75-4c25-becc-37968dc2eab6.png)
</details>

<details>
  <summary>Daijirin 4e (print | yomichan)</summary>
  
  ![daijirin2](https://user-images.githubusercontent.com/8003332/235578700-9dbf4fb0-0154-48b5-817c-8fe75e442afc.png)
</details>

<details>
  <summary>Sanseidō 8e (print | yomichan)</summary>
  
  ![sankoku8](https://github.com/stephenmk/jitenbot/assets/8003332/0358b3fc-71fb-4557-977c-1976a12229ec)
</details>

<details>
  <summary>Various (GoldenDict)</summary>
  
  ![goldendict](https://github.com/stephenmk/jitenbot/assets/8003332/76104cbf-845d-4e18-8b78-3ee3ebbf4da6)
</details>

# Usage
```
usage: jitenbot [-h] [-p PAGE_DIR] [-m MEDIA_DIR] [-i MDICT_ICON]
                [--no-mdict-export] [--no-yomichan-export]
                [--validate-yomichan-terms]
                {jitenon-kokugo,jitenon-yoji,jitenon-kotowaza,smk8,daijirin2,sankoku8}

Convert Japanese dictionary files to new formats.

positional arguments:
  {jitenon-kokugo,jitenon-yoji,jitenon-kotowaza,smk8,daijirin2,sankoku8}
                        name of dictionary to convert

options:
  -h, --help            show this help message and exit
  -p PAGE_DIR, --page-dir PAGE_DIR
                        path to directory containing XML page files
  -m MEDIA_DIR, --media-dir MEDIA_DIR
                        path to directory containing media folders (gaiji,
                        graphics, audio, etc.)
  -i MDICT_ICON, --mdict-icon MDICT_ICON
                        path to icon file to be used with MDict
  --no-mdict-export     skip export of dictionary data to MDict format
  --no-yomichan-export  skip export of dictionary data to Yomichan format
  --validate-yomichan-terms
                        validate JSON structure of exported Yomichan
                        dictionary terms

See README.md for details regarding media directory structures

```
### Web Targets
Jitenbot will scrape the target website and save the pages to the [user cache directory](https://pypi.org/project/platformdirs/).
As a courtesy to the website owners, jitenbot is configured to pause for 10 seconds between each page request. Consequently, 
a complete crawl of a target website may take several days.

HTTP request headers (user agent string, etc.) may be customized by editing the `config.json` file created in the
[user config directory](https://pypi.org/project/platformdirs/).

### Monokakido Targets
These digital dictionaries are available for purchase through the [Monokakido Dictionaries app](https://www.monokakido.jp/ja/dictionaries/app/) on MacOS/iOS. Under ideal circumstances, Jitenbot would be able to automatically fetch all the data it needs from this app's data directory[^1] on your system. In its current state of development, Jitenbot unfortunately requires you to find and assemble the necessary data yourself. The files must be organized into a particular folder structure (defined below) and then passed to Jitenbot via the corresponding command line arguments.

Some of the folders in the app's data directory[^1] contain encoded files that must be unencoded using [golddranks' monokakido tool](https://github.com/golddranks/monokakido/). These folders are indicated by a reference mark (※) in the notes below.

[^1]: `/Library/Application Support/AppStoreContent/jp.monokakido.Dictionaries/Products/`

<details>
  <summary>smk8 files</summary>

Since Yomichan does not support audio files from imported dictionaries, the `audio/` directory may be omitted to save filesize space in the output ZIP file if desired.

```
.
├── media
│   ├── audio (※)
│   │   ├── 00001.aac
│   │   ├── 00002.aac
│   │   ├── 00003.aac
│   │   ├── ...
│   │   └── 82682.aac
│   ├── Audio.png
│   └── gaiji
│       ├── 1d110.svg
│       ├── 1d15d.svg
│       ├── 1d15e.svg
│       ├── ...
│       └── xbunnoa.svg
└── pages (※)
    ├── 0000000000.xml
    ├── 0000000001.xml
    ├── 0000000002.xml
    ├── ...
    └── 0000064581.xml
```
</details>

<details>
  <summary>daijirin2 files</summary>

The `graphics/` directory may be omitted to save space if desired.

```
.
├── media
│   ├── gaiji
│   │   ├── 1D10B.svg
│   │   ├── 1D110.svg
│   │   ├── 1D12A.svg
│   │   ├── ...
│   │   └── vectorOB.svg
│   └── graphics (※)
│       ├── 3djr_0002.png
│       ├── 3djr_0004.png
│       ├── 3djr_0005.png
│       ├── ...
│       └── 4djr_yahazu.png
└── pages (※)
    ├── 0000000001.xml
    ├── 0000000002.xml
    ├── 0000000003.xml
    ├── ...
    └── 0000182633.xml
```
</details>

<details>
  <summary>sankoku8 files</summary>

```
.
├── media
│   ├── graphics
│   │   ├── 000chouchou.png
│   │   ├── ...
│   │   └── 888udatsu.png
│   ├── svg-accent
│   │   ├── アクセント.svg
│   │   └── 平板.svg
│   ├── svg-frac
│   │   ├── frac-1-2.svg
│   │   ├── ...
│   │   └── frac-a-b.svg
│   ├── svg-gaiji
│   │   ├── aiaigasa.svg
│   │   ├── ...
│   │   └── 異体字_西.svg
│   ├── svg-intonation
│   │   ├── 上昇下降.svg
│   │   ├── ...
│   │   └── 長.svg
│   ├── svg-logo
│   │   ├── denshi.svg
│   │   ├── ...
│   │   └── 重要語.svg
│   └── svg-special
│       └── 区切り線.svg
└── pages (※)
    ├── 0000000001.xml
    ├── ...
    └── 0000065457.xml
```
</details>

# Attribution
`Adobe-Japan1_sequences.txt` is provided by [The Adobe-Japan1-7 Character Collection](https://github.com/adobe-type-tools/Adobe-Japan1).

The Yomichan term-bank schema definition `dictionary-term-bank-v3-schema.json` is provided by the [Yomichan](https://github.com/foosoft/yomichan) project.

Many thanks to [epistularum](https://github.com/epistularum) for providing thoughtful feedback regarding the implementation of the MDict export functionality.
