#!/usr/bin/env python

import logging

class Log():

  def __init__(self, filename = "trace.log"):
    self.log = logging.getLogger("log")
    self.log.setLevel(logging.DEBUG)
    self.formatter = logging.Formatter("%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
    self.file_handler = logging.FileHandler(filename, "a")
    self.file_handler.setLevel(logging.DEBUG)
    self.file_handler.setFormatter(self.formatter)
    self.log.addHandler(self.file_handler)
