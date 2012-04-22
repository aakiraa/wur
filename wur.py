#!/usr/bin/env python

import curses
import command
import core
import threading
import time

class Playlist_w:
  """
  Class managing the playlist panel
  """
  def __init__(self, parent_w):
    self.parent_w = parent_w
    self.parent_w_y,self.parent_w_x = parent_w.getmaxyx()
    self.playlist_w = parent_w.derwin(self.parent_w_y-7, self.parent_w_x/3, 5, 0)
    self.playlist_w_y, self.playlist_w_x = self.playlist_w.getmaxyx()
    self.playlist_w.refresh()
    for i in range(0,self.playlist_w_y):
      self.add_pos(i, "No artist - No music", 3)

  def refresh(self):
    self.playlist_w.refresh()

  def __reset_pos(self, pos):
    self.playlist_w.addstr(pos, 0, " " * (self.playlist_w_x - 1), curses.color_pair(0))

  def reset_all(self):
    for i in range(0,self.playlist_w_y):
      self.__reset_pos(i)

  def purge_list(self):
    self.reset_all()

  def add_pos(self, pos, string, color):
    self.playlist_w.addstr(pos, 0, string + " " * (self.playlist_w_x - 1 - len(string)),curses.color_pair(color))

  def add(self, strings):
    color = 0
    for i in range(0,min(self.playlist_w_y-1, len(strings)-1)):
      self.add_pos(i, strings[i][0] + " " + strings[i][1] + " (%02d:%02d)" % (strings[i][2]/60, strings[i][2]%60), color)
      if color == 0: color = 6
      else: color = 0

  def swap_pos(self, a, b):
    pass

class Search_w:
  """
  Class managing the search panel
  """
  def __init__(self, parent_w):
    self.parent_w = parent_w
    self.parent_w_y,self.parent_w_x = parent_w.getmaxyx()
    self.search_w = parent_w.derwin(self.parent_w_y-7, self.parent_w_x*2/3, 5, self.parent_w_x/3)
    self.search_w_y,self.search_w_x = self.search_w.getmaxyx()
    s = "/ NO SEARCH /"
    self.search_w.addstr(i, 0, s + " " * (self.search_w_x - 1 - len(s)))
    self.search_w.refresh()

class Onair_w:
  """
  Class managing the display of the current song and the status bar under it
  """
  def __init__(self, parent_w):
    self.parent_w = parent_w
    self.parent_w_y,self.parent_w_x = parent_w.getmaxyx()
    self.onair_w = parent_w.derwin(4, self.parent_w_x, 0, 0)
    self.onair_w_y,self.onair_w_x = self.onair_w.getmaxyx()

    self.onair_w.addstr(3, 0, " " * (self.onair_w_x-1),curses.color_pair(5))
    self.onair_w.addstr(0, 0, "--------------------")
    self.onair_w.addstr(1, 0, "--------------------")
    self.onair_w.addstr(2, 0, "-- : --")
    self.onair_w.refresh()

  def set_onair(self, current_song):
    self.onair_w.addstr(0, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.onair_w.addstr(1, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.onair_w.addstr(2, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.onair_w.addstr(0, 0, str(current_song[0]))
    self.onair_w.addstr(1, 0, str(current_song[1]))
    self.onair_w.addstr(3, 0, " " * (self.onair_w_x-1),curses.color_pair(5))
    if current_song is not None:
      self.minute = current_song[2]/60
      self.second = current_song[2]%60
      self.minute_total = current_song[3]/60
      self.second_total = current_song[3]%60
    else:
      self.minute = 0
      self.second = 0
      self.minute_total = 0
      self.second_total = 0
    self.onair_w.addstr(2, 0, "%02d:%02d / %02d:%02d" % (self.minute, self.second, self.minute_total, self.second_total))
    self.onair_w.refresh()

  def set_artist(self, current_artist):
    self.onair_w.addstr(0, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.onair_w.addstr(0, 0, current_artist)

  def set_title(self, current_title):
    self.onair_w.addstr(1, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.onair_w.addstr(1, 0, current_title)

  def set_time(self, current_time, current_total):
    self.onair_w.addstr(2, 0, " " * (self.onair_w_x-1),curses.color_pair(0))
    self.minute = current_time/60
    self.second = current_time%60
    self.minute_total = current_total/60
    self.second_total = current_total%60
    self.onair_w.addstr(2, 0, "%02d:%02d / %02d:%02d" % (self.minute, self.second, self.minute_total, self.second_total))

  def refresh(self):
    self.onair_w.refresh()

  def set_status_bar(self, string):
    self.onair_w.addstr(3,0,string, curses.color_pair(5))
    self.onair_w.addstr(3,len(string), " " * (self.onair_w_x - len(string) - 1), curses.color_pair(5))
    self.onair_w.refresh()

class Buffer_w:
  """
  Class managing the user input panel located at the bottom
  It's quite a big class because it handles every input in this field
  It communicates with Command to enter in the Core engine
  """

  def __init__(self, parent_w, onair_w, command_obj, refresh_thread):
    self.parent_w = parent_w
    self.onair_w = onair_w
    self.parent_w_y,self.parent_w_x = parent_w.getmaxyx()
    self.buffer_w = parent_w.derwin(2, self.parent_w_x, self.parent_w_y-2, 0)
    self.buffer_w_y, self.buffer_w_x = self.buffer_w.getmaxyx()

    self.channel = ""
    self.connected = False
    self.logged_at = ""
    self.role = ""
    self.status_bar  = "[c] [%s] [%s]" % (self.role,self.logged_at)
    self.buffer_w.addstr(0, 0, self.status_bar +  " " * (self.buffer_w_x - 1 - len(self.status_bar)), curses.color_pair(5))
    self.buffer_w.refresh()

    self.history = []
    self.user_input = ""
    self.prompt =  "[%s]: " % (self.channel)
    self.default_prompt =  "[%s]: " % (self.channel)
    self.current_pos = len(self.prompt)

    self.command_obj = command_obj
    self.command_obj.ask_pass_callback = self.ask_pass_callback
    self.command_obj.pass_cleaning_callback = self.pass_cleaning_callback
    self.refresh_thread = refresh_thread

  def refresh_mode(self, mode="c"):
    self.buffer_w.addstr(0, 1, mode, curses.color_pair(5))
    self.buffer_w.refresh()

  def refresh_status(self):
    self.status_bar  = "[i] [%s] [%s]" % (self.role,self.logged_at)
    self.buffer_w.addstr(0, 0, self.status_bar +  " " * (self.buffer_w_x - 1 - len(self.status_bar)), curses.color_pair(5))
    self.buffer_w.refresh()

  def refresh_prompt(self):
    self.buffer_w.addstr(1, 0, self.prompt + self.user_input)
    self.buffer_w.addstr(1, len(self.prompt) + len(self.user_input), " " * (self.buffer_w_x - 1 - len(self.prompt) - len(self.user_input)))
    self.buffer_w.refresh()

  def set_channel(self, channel):
    self.channel = channel
    self.prompt =  "[%s]: " % (self.channel)

  def set_logged_at(self, logged_at):
    self.logged_at = logged_at

  def add_history(self, command):
    pass

  def ask_pass_callback(self):
    """ Callback passed to core module for a secure password input when requesting login """
    self.prompt = "pass : "
    self.user_input = ""
    self.current_pos = len(self.prompt)
    self.password = ""
    while True:
      self.refresh_prompt()
      event = self.buffer_w.getkey(1, self.current_pos)
      if ord(event) == 127: # got BACKSPACE, deleting
        self.buffer_w.addstr(1, len(self.prompt) + len(self.user_input)-1, " ")
        self.user_input = self.user_input[:-1]
      elif ord(event) == 10:# got ENTER, return pass
        event = '0'
        self.current_pos = self.default_prompt
        self.user_input = ""
        self.prompt = self.default_prompt
        return self.password
      else:
        self.password = self.password + str(event)
        self.user_input = self.user_input + "*"
        self.current_pos = self.current_pos + 1

  def pass_cleaning_callback(self):
    """ get the pass length to erase the password memory area and erase the length value"""
    pass_length = len(self.password)
    self.password = "0" * pass_length
    pass_length = 0

  def insert_mode(self):
    self.buffer_w.addstr(1,0, self.prompt)
    self.refresh_mode("i")
    while True:
      self.buffer_w.noutrefresh()
      curses.doupdate()
      event = self.buffer_w.getkey(1, self.current_pos)

      if ord(event) == 27 : # got ESC, exiting from insert mode
        self.refresh_mode("c")
        break
      elif ord(event) == 410: continue # got SIGWINCH, resize elements (not implemented yet)
      elif ord(event) == 127: # got BACKSPACE, deleting
        self.buffer_w.addstr(1, len(self.prompt) + len(self.user_input)-1, " ")
        self.user_input = self.user_input[:-1]
      elif ord(event) == 10:# got ENTER, refresh and process command
        #continue if there is nothing interesting on the command line
        if self.user_input == "" or self.user_input[0] == " ":
          self.user_input = ""
          self.current_pos = len(self.prompt)
          self.refresh_prompt()
          continue # jump back to get keystroke with a new fresh prompt
        (code, display_params) = self.command_obj.process_command(self.user_input)
        if code == 0:
          pass
        if code == 1:
          if display_params is not None:
            if display_params.has_key("onair"):
              self.onair_w.set_onair(display_params["onair"])
            if display_params.has_key("playlist"):
              self.playlist_w.add(display_params["playlist"])
            if display_params.has_key("status"):
              self.role = "~"
              self.set_logged_at(display_params["status"])
              self.refresh_status()
              self.set_channel("john")
              self.refresh_prompt()
            self.connected = True
            self.refreshing = threading.Thread(target=self.refresh_thread)
            self.refreshing.start()
          self.onair_w.set_status_bar(self.user_input)
          self.add_history(self.user_input)
        elif code == 128:
          self.onair_w.set_status_bar(self.user_input + ": command not found")
        else:
          self.onair_w.set_status_bar(self.user_input + ": %d" % (code))
        self.user_input = ""
        self.current_pos = len(self.prompt)
      else: # got any other key
        self.user_input = self.user_input + str(event)
        self.current_pos = self.current_pos + 1

      self.refresh_prompt()

#curses.endwin()
class JUI:

  def __init__(self):
    self.main_w = curses.initscr()
    self.main_w_y,self.main_w_x = self.main_w.getmaxyx()
    curses.noecho()
    curses.curs_set(0)
    self.main_w.keypad(1)
    self.core = core.Core()
    self.command_obj = command.Command(self.core)
    self.stop_refreshing = 1
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN);
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE);
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK);
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK);
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE);
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK);

    self.onair_w = Onair_w(self.main_w)
    self.playlist_w = Playlist_w(self.main_w)
    self.search_w = Search_w(self.main_w)
    self.buffer_w = Buffer_w(self.main_w,self.onair_w, self.command_obj, self.refresh_thread)

  def refresh_thread(self):
    timer = 0
    total = 0
    self.playlist_w.reset_all()
    while self.stop_refreshing:
      song = self.core.refresh_meta()
      songs = self.core.get_playlist()
      if song is None:
        continue
      timer = song[2]
      total = song[3]
      self.onair_w.set_onair(song)
      self.playlist_w.add(songs)
      for i in range(0,9):
        time.sleep(1)
        timer = timer + 1
        self.onair_w.set_time(timer, total)
        self.onair_w.refresh()
        self.playlist_w.refresh()

  def set_last_command(self, command):
    self.onair_w.set_status_bar(command)

  def process_command(self):
    pass

  def main(self):
    while True:
      curses.curs_set(0)
      event = self.main_w.getch()
      if event == ord("q"):
        self.stop_refreshing = 0
        break
      elif event == ord("i"):
        self.buffer_w.insert_mode()
      elif event == ord("n"):
        update = self.core.forward()
        if update is not None:
          self.onair_w.set_onair(update["current"])
          self.playlist_w.add(update["playlist"])
          self.onair_w.refresh()
          self.playlist_w.refresh()
      elif event == ord("p"):
        update = self.core.prev()
        if update is not None:
          self.onair_w.set_onair(update["current"])
          self.playlist_w.add(update["playlist"])
          self.onair_w.refresh()
          self.playlist_w.refresh()
      elif event == ord("m"):
        self.core.mute()
      elif event == ord(" "):
        self.core.pause()
      else:
        #self.process_command(event)
        self.onair_w.set_status_bar(str(event))

if __name__ == "__main__":
  ui = JUI()
  ui.main()
