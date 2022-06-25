
from song import Song

class SongQueue():

  def __init__(self):
    self.front_song = None
    self.end_song = None

  def enqueue_song(self, song_name):
    
    #If no songs in queue then a new song is both the front and end of the queue
    if front_song == None:
      # Song at front of queue 
      new_song = Song(song_name, None)
      front_song = new_song
    else:
      #Create new song with name
      new_song = Song(song_name, end_song)
      end_song = new_song
    
      
    
  def dequeue_song(self):
    if front_song == None:
	  return None
	  
    next_song = front_song.get_this_song()
    front_song = next_song.get_next_song()
    
    return next_song
    
  def is_empty(self):
    if front_song == None:
      return True
    return False
  