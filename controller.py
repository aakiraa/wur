#!/usr/bin/python

import urllib2, base64
import json
import time
import log

# TODO : 
# Improve the way try block are manipulated and the way exception are caught
# Review the way the log is called

class Controller:
  """
  Controller based object manipulates json to send/receive 
  information to/from the streaming server
  """
  JSON_KEY_CURRENT_SONG   = "current_song"
  JSON_KEY_PLAYLIST       = "play_queue"
  JSON_KEY_PLAYLIST_SONGS = "songs"

  JSON_KEY_ARTIST         = "artist"
  JSON_KEY_TITLE          = "title"
  JSON_KEY_ELAPSED        = "elapsed"
  JSON_KEY_TOTAL          = "duration"

  JSON_TPL_NEXT    = open("json/json_next_tpl", "r").read()
  JSON_TPL_PREV    = open("json/json_prev_tpl", "r").read()
  JSON_TPL_REFRESH = open("json/json_refresh_tpl", "r").read()

  SERVER_URL_TPL = "http://%(host)s:%(port)d/api/json"
  LOGGER = log.Log()

  def __init__(self, host, port, user, password):
    self.host = host
    self.port = port
    self.log = log.Log()
    self.playlist = []
    try:
      request = urllib2.Request("http://%s:%d/api/json" % (host, port), "{\"timestamp\":123445678}")
      self.base64string = base64.encodestring('%s:%s' % (user, password))
      request.add_header("Authorization", "Basic %s" % self.base64string)
      result = urllib2.urlopen(request)
      response = result.read()
    except Exception, e:
      # check 401 and change base64string + decorator around send request
      self.__class__.LOGGER.log.error("%s" % (str(e)))

  def send_request(self, payload):
    try:
      request = urllib2.Request("http://%s:%d/api/json" % (self.host, self.port), payload)
      request.add_header("Authorization", "Basic %s" % self.base64string)
      result = urllib2.urlopen(request)
      return result.read()
    except urllib2.HTTPError, err:
      self.__class__.LOGGER.log.error("%s" % (err.args))
    except urllib2.URLError, e:
      self.__class__.LOGGER.log.error("%s" % (e.args))
    return None
  
  def refresh(self):
    self.__class__.LOGGER.log.debug("Entering refresh.")
    response = self.send_request("{\"timestamp\":1203333}")
    try:
      data = json.loads(response)
      curr_title = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TITLE] 
      curr_artist = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ARTIST] 
      curr_elapsed = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ELAPSED]
      curr_total = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TOTAL]
      return (curr_artist, curr_title, curr_elapsed, curr_total)
    except Exception, e:
      self.__class__.LOGGER.log.error("%s" % (str(e)))
      return ("", "", 0, 0)
 
  def get_playlist_cache(self):
    return self.playlist

  def get_playlist(self):
    self.__class__.LOGGER.log.debug("Entering get_playlist.")
    response = self.send_request("{\"timestamp\":0}")
    playlist = []
    try:
      data = json.loads(response)
      for song in data[self.__class__.JSON_KEY_PLAYLIST][self.__class__.JSON_KEY_PLAYLIST_SONGS]:
        title = song[self.__class__.JSON_KEY_TITLE] 
        artist = song[self.__class__.JSON_KEY_ARTIST] 
        total = song[self.__class__.JSON_KEY_TOTAL]
	playlist.append((artist, title, total))
      return playlist
    except Exception, e:
      self.__class__.LOGGER.log.error("%s" % (str(e)))
      return None

  def forward(self):
    response = self.send_request("{\"timestamp\":12134567, \"action\":{\"name\":\"next\"}}")
    playlist = []
    try:
      data = json.loads(response)
      curr_title = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TITLE] 
      curr_artist = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ARTIST] 
      curr_elapsed = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ELAPSED]
      curr_total = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TOTAL]
      for song in data[self.__class__.JSON_KEY_PLAYLIST][self.__class__.JSON_KEY_PLAYLIST_SONGS]:
        title = song[self.__class__.JSON_KEY_TITLE] 
        artist = song[self.__class__.JSON_KEY_ARTIST] 
        total = song[self.__class__.JSON_KEY_TOTAL]
	playlist.append((artist, title, total))
      return {"current":(curr_artist, curr_title, curr_elapsed, curr_total), "playlist":playlist}
    except Exception, e:
      self.__class__.LOGGER.log.error("%s" % (str(e)))
      return None
    
  def prev(self):
    response = self.send_request("{\"timestamp\":12134567, \"action\":{\"name\":\"previous\"}}")
    playlist = []
    try:
      data = json.loads(response)
      curr_title = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TITLE] 
      curr_artist = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ARTIST] 
      curr_elapsed = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_ELAPSED]
      curr_total = data[self.__class__.JSON_KEY_CURRENT_SONG][self.__class__.JSON_KEY_TOTAL]
      for song in data[self.__class__.JSON_KEY_PLAYLIST][self.__class__.JSON_KEY_PLAYLIST_SONGS]:
        title = song[self.__class__.JSON_KEY_TITLE] 
        artist = song[self.__class__.JSON_KEY_ARTIST] 
        total = song[self.__class__.JSON_KEY_TOTAL]
	playlist.append((artist, title, total))
      return {"current":(curr_artist, curr_title, curr_elapsed, curr_total), "playlist":playlist}
    except Exception, e:
      self.__class__.LOGGER.log.error("%s" % (str(e)))
      return None
