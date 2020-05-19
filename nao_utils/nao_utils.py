#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging.handlers
import os

from naoqi import ALProxy

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/nao_utils.log",
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


class NaoUtils:

    def __init__(self, ip="169.254.88.3", port=9559):
        """

        :param ip:
        :param port:
        """
        self.ip = ip
        self.port = port
        self.nao_speech = ALProxy("ALTextToSpeech", ip, port)
        self.nao_motion = ALProxy("ALMotion", ip, port)
        self.nao_posture = ALProxy("ALRobotPosture", ip, port)
        self.camProxy = ALProxy("ALVideoDevice", ip, port)
        self.nao_led = ALProxy("ALLeds", ip, port)
        self.nao_memory = ALProxy("ALMemory", ip, port)

    def wait_for(self, event_list=None):
        """
        Wait that on event are activate
        :param event_list: (list of string) event list to subscribe http://doc.aldebaran.com/1-14/naoqi/sensors/alsensors-api.html
        :return: (string) trigger event
        """
        if event_list is None:
            event_list = ["MiddleTactilTouched"]
        self.nao_led.off("AllLeds")
        self.nao_led.on("AllLedsRed")

        press = False
        press_button = None
        while not press:
            for button_name in event_list:
                if self.nao_memory.getData(button_name) == 1:
                    press_button = button_name
                    press = True
                    break

        while True:
            if self.nao_memory.getData(press_button) == 0:
                self.nao_led.off("AllLeds")
                self.nao_led.on("AllLedsGreen")
                return press_button
