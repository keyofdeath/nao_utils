#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Usage:
  teachable_machine.py <ip> <model>

Options:
  -h --help      Show this screen.
  <ip>           Nao ip
  <model>        Teachable machine model path
"""

from __future__ import absolute_import

import logging.handlers
import os

import cv2
import numpy as np
import tensorflow as tf
from docopt import docopt

from nao_utils.nao_speech import NaoSpeech
from nao_utils.nao_utils import NaoUtils
from nao_utils.nao_video_stream import NaoVideoStream

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
SIZE = (224, 224)

# Load the model
model = tf.keras.models.load_model(os.path.join(args["<model>"], "keras_model.h5"))
with open(os.path.join(args["<model>"], "labels.txt")) as f:
    # Remove \n and remove the index next to the label name: <index> <label name>
    labels = [' '.join(l.replace('\n', '').split(' ')[1:]) for l in f]
wait_list = ["MiddleTactilTouched", "RightBumperPressed", "LeftBumperPressed"]

nao_utils = NaoUtils(IP)
video_stream = NaoVideoStream(IP).start()
speech = NaoSpeech(IP)

speech.speech_and_move("On va tester le réseau de neuronne que vous avez fait!"
                       "Apuy sur le dessu de ma tête quand tu est prêt."
                       "Pour arreter le test apuy sur l'un de mais pied")
while True:

    event = nao_utils.wait_for(wait_list)
    if event == "RightBumperPressed" or event == "LeftBumperPressed":
        break
    frame = video_stream.frame
    frame = cv2.resize(frame, SIZE, interpolation=cv2.INTER_AREA)
    normalized_image_array = (frame.astype(np.float32) / 127.0) - 1
    model_input = np.expand_dims(normalized_image_array, axis=0)
    prediction = model.predict(model_input)
    label_name = labels[prediction.argmax(axis=1)[0]]
    speech.speech("J'ai reconus le label {}".format(label_name))

video_stream.stop()
