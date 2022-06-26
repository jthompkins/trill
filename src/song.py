

class Song():
  """
  Song class used as a node for the Song Queue.
  Song stores a value that is either a Youtube URL or a string describing what
  needs to be searched on Youtube to find the requested song.
  """
  def __init__(self, value):
    #Assign a value to this song
    self._value = value
    #Keep track of the next song
    self._next_song = None

  def get_this_song(self):
    #Return the value of this song
    return self._value

  def set_next_song(self, next_song):
    self._next_song = next_song

  def get_next_song(self):
    #Return the next song
    return self._next_song