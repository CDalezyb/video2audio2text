#!/bin/bash

SCRIPTS_HOME=$(dirname $(readlink -f "$0"))
bili2text_HOME=${SCRIPTS_HOME}/../bili2text
python3 ${bili2text_HOME}/main.py \
    --av BV1ZNr4YUE8Z BV1wVnozYEUb \
    --download-dir /home/dale/CDale/Bili_STT/downloaded_data \
    --whisper-model large \
    --asr-prompt "以下是普通话的句子。请准确转写。" 