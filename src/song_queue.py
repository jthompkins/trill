
from song import Song

class SongQueue():

  def __init__(self):
    self.front_song = None
    self.end_song = None

  def enqueue_song(self, song_name):
    
    #If no songs in queue then a new song is both the front and end of the queue
    if self.front_song == None:
      # Song at front of queue 
      new_song = Song(song_name)
      self.front_song = new_song
    elif self.end_song == None:
      new_song = Song(song_name)
      self.front_song.set_next_song(new_song)
      self.end_song = new_song
    else:
      #Create new song with name
      new_song = Song(song_name)
      self.end_song.set_next_song(new_song)
      self.end_song = new_song
    
  def dequeue_song(self):
    if self.front_song == None:
      return None
    #Get value of current front song
    next_song_value = self.front_song.get_this_song()
    #Set next song as the front
    self.front_song = self.front_song.get_next_song()
    
    return next_song_value
    
  def is_empty(self):
    if self.front_song == None:
      return True
    return False
  
  def get_queue(self):
    queue = []
    current_song = self.front_song.get_this_song()
    queue.append(current_song)
    next_song = self.front_song.get_next_song()
    while next_song is not None:
      queue.append(next_song.get_this_song())
      next_song = next_song.get_next_song()
    return queue

  def clear_queue(self):
    self.front_song = None
    self.end_song = None