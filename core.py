#!/usr/bin/python

import controller
#import player
import log

from subprocess import Popen, PIPE

# TODO:
#         - create real player and put the code corresponding to it... in it !
#         - find why these SSL errors occur all the time -> maybe this is something related with the SSL context and the multithreading

class Core:
  """
  Core handle request mainly orginating from Command
  but can also be used directly by main classes (be careful on what you do)
  It aims to check some basic stuff like authentication before passing order
  to Controller or Player
  """
  error_value = {
                 "OK":0,
                 "CONNECTED":1,
                 "AUTH_FAILED":2,
                 "NOT_CONNECTED":3,
                 "CANT_PLAY":4,
                }
  LOGGER = log.Log()

  def __init__(self):
    self.__logged = False
    self.user = ""
    self.password = ""
    self.host = ""
    self.control_port = 8080
    self.stream_port = 8080
    self.controller = None
    self.player = None

  def login_required(func):
    """ simple decorator, wrapping enabled, preventing usage of commands needing logged state """
    def wrapper(*args, **kwargs):
      self = list(args)[0]
      if self.__logged:
        response = func(*args, **kwargs)
      else:
        return (self.__class__.error_value["NOT_CONNECTED"], {"status": "not connected"})
        # post if needed
      return response
    return wrapper

  def login(self, user, host, port, password):
    self.user = user
    self.host = host
    self.port = port
    try:
      self.player = Popen(['mplayer','-input', 'nodefault-bindings', '-noconfig' ,'all', '-slave', '-quiet', 'http://%s:%s@%s:%d/stream' % (self.user, password, self.host, self.stream_port)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
      for i in  self.player.stdout.readline() :
        if i == "Starting playback...":
          break
      self.controller = controller.Controller(self.host, self.control_port, self.user, password)
      self.__logged = True
      self.__class__.LOGGER.log.info("connected as %s, to %s, port %s " % (self.user, self.host, self.port))
      return (self.__class__.error_value["CONNECTED"], {"status":"%s@%s:%s" % (self.user, self.host, self.port)})
    except:
      self.__class__.LOGGER.log.error("controller: %s, player: %s" % (str(self.controller), str(self.player)))
      return (self.__class__.error_value["AUTH_FAILED"],{"status":"auth failed"})
    #self.player.connect()

  @login_required
  def logout(self):
    self.__logged = False
    self.player.terminate()
    self.player = None
    self.controller = None
    #self.player.stop()
    #self.controller.close()
    #return

  @login_required
  def play(self):
    pass

  @login_required
  def refresh_meta(self):
    return self.controller.refresh()

  @login_required
  def get_playlist(self):
    return self.controller.get_playlist()

  @login_required
  def pause(self):
    self.player.stdin.write("pause\n")

  # TODO : in these two following methods, try to flush the buffer in order to avoid
  # sound glitches and improving reactivity

  @login_required
  def forward(self):
    return self.controller.forward()

  @login_required
  def prev(self):
    return self.controller.prev()

  @login_required
  def stop(self):
    self.__logged = False
    self.player.terminate()
    self.player = None
    self.controller = None
    #return self.player.stop()

  @login_required
  def mute(self):
    self.player.stdin.write("mute\n")
