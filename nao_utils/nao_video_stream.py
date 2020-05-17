#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging.handlers
import os
from threading import Thread

import numpy as np
from naoqi import ALProxy

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/nao_video_stream.log",
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


class NaoVideoStream:
    def __init__(self, ip="169.254.88.3", port=9559, cam_index=0, fps=10):
        """

        :param ip:
        :param port:
        :param cam_index: 0 = head, 1 = mouth
        :param fps:
        """
        self.ip = ip
        self.port = port
        self.cam_index = cam_index
        self.fps = fps
        self.camProxy = ALProxy("ALVideoDevice", ip, port)
        self.resolution = 1
        # BGR
        self.colorSpace = 13
        self.videoClient = self.camProxy.subscribeCamera("nao_video_stream",
                                                         cam_index,
                                                         self.resolution,
                                                         self.colorSpace,
                                                         self.fps)
        self.stopped = False
        self.frame = None

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.camProxy.unsubscribe(self.videoClient)
                return
            # Get frame
            naoImage = self.camProxy.getImageRemote(self.videoClient)
            # Get the image size and pixel array.
            imageWidth = naoImage[0]
            imageHeight = naoImage[1]
            number_of_layers = naoImage[2]
            img = naoImage[6]
            resolution = (imageHeight, imageWidth, number_of_layers)
            img = np.frombuffer(img, dtype=np.uint8)
            self.frame = np.array(img, dtype=np.uint8).reshape(resolution)

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
