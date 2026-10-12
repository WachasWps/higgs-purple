#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
S=/Users/wachas/Documents/higgs-purple/dub/tools
$S/story_build.sh 00b304b4 291827ba c51221b6 ce849d3f e7e42eaf 5fd50ab8 655a1328 74495eba 7ea55172 23850d94 390113f1 71e0977a bd3b8af7 f7ce58d4 595689d8 715b1b5c 7558fbf1 89697c77 906fbf3c
echo "STORY BUILD DONE" >> feedback/story_build_knc.log
$S/ads_v3.sh
