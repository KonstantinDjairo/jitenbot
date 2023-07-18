#!/bin/sh

python -m unittest discover -s tests

python jitenbot.py jitenon-kokugo
python jitenbot.py jitenon-yoji
python jitenbot.py jitenon-kotowaza

python jitenbot.py smk8 \
       --media-dir  monokakido/SMK8/media \
       --page-dir   monokakido/SMK8/pages \
       --mdict-icon monokakido/SMK8/SMK8-76@3x.png

python jitenbot.py daijirin2 \
       --media-dir  monokakido/DAIJIRIN2/media \
       --page-dir   monokakido/DAIJIRIN2/pages \
       --mdict-icon monokakido/DAIJIRIN2/DAIJIRIN2-76@3x.png

python jitenbot.py sankoku8 \
       --media-dir  monokakido/SANKOKU8/media \
       --page-dir   monokakido/SANKOKU8/pages \
       --mdict-icon monokakido/SANKOKU8/SANKOKU8-76@3x.png
