#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Usage:
  teachable_machine.py <ip>

Options:
  -h --help      Show this screen.
  <ip>           Nao ip
"""

from __future__ import absolute_import

import logging.handlers
import os

from docopt import docopt

from nao_utils.nao_speech import NaoSpeech
from nao_utils.nao_utils import NaoUtils
from nao_utils.nao_video_stream import NaoVideoStream
from utils import http_json_request
import time

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/teachable_machine.log",
                                                 when="midnight", backupCount=60)
STREAM_HDLR = logging.StreamHandler()
FORMATTER = logging.Formatter("%(asctime)s %(filename)s [%(levelname)s] %(message)s")
HDLR.setFormatter(FORMATTER)
STREAM_HDLR.setFormatter(FORMATTER)
PYTHON_LOGGER.addHandler(HDLR)
PYTHON_LOGGER.addHandler(STREAM_HDLR)
PYTHON_LOGGER.setLevel(logging.DEBUG)

# Absolute path to the folder location of this python file
FOLDER_ABSOLUTE_PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))

args = docopt(__doc__)

IP = args["<ip>"]

wait_list = ["MiddleTactilTouched", "RightBumperPressed", "LeftBumperPressed"]

nao_utils = NaoUtils(IP)
video_stream = NaoVideoStream(IP).start()
speech = NaoSpeech(IP)

nao_utils.nao_posture.goToPosture("Stand", 1.0)
speech.speech_and_move(u'On va tester le réseau de neuronne que vous avez fait! Apuy sur le dessu de ma tête quand tu est prêt. Pour arreter le test. Apuy sur l\'un de mais pied')
while True:

    event = nao_utils.wait_for(wait_list)
    if event == "RightBumperPressed" or event == "LeftBumperPressed":
        break
    frame = video_stream.frame
    if frame is None:
        continue
    label = http_json_request({"img": frame.tolist()}, "http://localhost:8888/")
    if label is not None:
        label_name = label["label"].encode()
        speech.speech("J'ai reconus le label {}".format(label_name))
    time.sleep(1)

video_stream.stop()
