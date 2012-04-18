#!/usr/bin/env python

import log

class Command: 
  """
  Command handle every input request and helps dispatching command through
  the core engine, it also allows to check user input
  """
  LOGGER = log.Log()

  def __init__(self, core):
    self.command_set = {'login':     self.__process_login,
                        'logout':    self.__process_logout,
                        'play':      self.__process_play,
                        'stop':      self.__process_stop,
                        'mute':      self.__process_mute,
                        'pause':     self.__process_pause,
                        'next':      self.__process_next,
                        'prev':      self.__process_prev,
                        'wait':      self.__process_wait,
                        'add':       self.__process_add,
                        'load':      self.__process_load,
                        'run':       self.__process_run,
                        'playlist':  self.__process_playlist,
                        'timetable': self.__process_timetable,
                        'alias':     self.__process_alias,
                        '+':         self.__process_add_from,
                        '-':         self.__process_delete_from,
                  }
    self.alias_set = {}
    self.core = core 
    self.ask_pass_callback = None
    self.pass_cleaning_callback = None

  def process_command(self, user_input):
    commands = self.__parse_command(user_input)
    for command in commands:
      splitted_command = command.split()
      if self.command_set.has_key(splitted_command[0]):
        self.__class__.LOGGER.log.error("got command")
        try:
          self.function = self.command_set[splitted_command[0]]
          code, messages = self.function(splitted_command[1:])
        except Exception, e:
          self.__class__.LOGGER.log.error("%s" % (e))
          messages = None
          code = 200
      elif self.alias_set.has_key(splitted_command[0]):
        self.process_command("%s %s" % (self.alias_set[splitted_command[0]])) 
      else:
        messages = None
        code = 201
    return (code, messages)

  def __parse_command(self, user_input):
    return user_input.split('&')

  def __process_login(self, params):
    try:
      args = params[0].split('@')
      user = args[0]
      host = args[1].split(':')[0]
      port = int(args[1].split(':')[1])
    except:
      self.__class__.LOGGER.log.error("wrong parameters : %s %s %d" % (user, host, port))
      return (127, {"status":"wrong parameters"})
    password = self.ask_pass_callback()
    self.pass_cleaning_callback()
    return self.core.login(user, host, port, password)

  def __process_logout(self, params):
    self.core.logout()
    buf = ["","not connected",""]
    return (0, None)

  def __process_play(self, param):
    (self.artist, self.song, self.time) = self.core.play()
    return (1, {"onair":(self.artist, self.song, self.time)})

  def __process_stop(self, param):
    self.core.stop()
    buf = ["","not connected",""]
    return (0, None)

  def __process_pause(self, params):
    self.core.pause()
    buf = ["","not connected",""]
    return (0, None)

  def __process_next(self):
    self.core.forward()
  
  def __process_mute(self):
    self.core.mute()

  def __process_prev(self):
    self.core.previous()
       
  def __process_wait(self, param):
    sleep_time = int(param)
    try:
      time.sleep(sleep_time)
    except:
      pass

  def __process_add(self):
    pass
       
  def __process_load(self):
    pass

  def __process_run(self):
    pass

  def __process_playlist(self):
    pass

  def __process_timetable(self):
    pass

  def __process_alias(self, params):
    pass

  def __process_add_from(self, params):
    pass

  def __process_delete_from(self, params):
    pass
