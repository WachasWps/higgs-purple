#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
until grep -q "STORY BUILD DONE" feedback/story_build_ps.log; do sleep 10; done
/Users/wachas/Documents/higgs-purple/dub/tools/story_build.sh 23850d94 390113f1 71e0977a bd3b8af7 f7ce58d4 595689d8 715b1b5c 7558fbf1 89697c77 906fbf3c
