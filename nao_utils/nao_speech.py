#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import logging.handlers
import os
from random import randint

import nao_utils.move_pattern.move as Mp
import nao_utils.move_pattern.stand_up as Sp
from nao_utils.nao_utils import NaoUtils

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/nao_speech.log",
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

NB_MOVE = 7
NB_CHARS_MOVE_THRESHOLD = 100


class NaoSpeech(NaoUtils):

    def speech(self, text_to_say):
        self.nao_speech.say(codecs.encode(text_to_say, "utf-8"))

    def speech_and_move(self, text_to_say):
        """
        Fonction qui fait bouger nao pendant qu'il parle
        INFO: Si le message est court Nao ne bougera pas (voir fichier setting.py pour changer la longueur)
        ATTENTION: Nao doit être debout !!!!!!!
        :param text_to_say: texte à dire
        :return:
        """

        if len(text_to_say) <= NB_CHARS_MOVE_THRESHOLD:
            self.nao_speech.say(codecs.encode(text_to_say, "utf-8"))
            return

        pid = self.nao_speech.post.say(codecs.encode(text_to_say, "utf-8"))
        move_cc = randint(1, NB_MOVE)
        while self.nao_speech.wait(pid, 1):
            names, times, keys = Mp.dico_move['move' + str(move_cc)]
            self.nao_motion.angleInterpolation(names, keys, times, True)
            move_cc += 1
            if move_cc > NB_MOVE:
                move_cc = 1
        try:
            self.nao_motion.angleInterpolation(Sp.names, Sp.keys, Sp.times, True)
        except Exception as e:
            print "Error ", e
            self.nao_posture.goToPosture("Stand", 0.6)
