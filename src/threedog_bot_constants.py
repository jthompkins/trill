#File for storing constant variables

import os

MAX_VOL = 1.99
MIN_VOL = 0.20
VOL_INC = 0.20
MUSIC_FILE =  'D:/Music/'
MUSIC_LIST_FILE = './music.txt'
MUSIC_EXTENSION = 'mp3'
YOUTUBE_SEARCH = "https://www.youtube.com/results?search_query="

NO_VOICE_CHANNEL = 'You are not in the voice channel!'

#User has to obtain this authentication code from Discord. Set as environment variable
THREEDOG_CODE = os.getenv("THREEDOGCODE")

HELP_MESSAGE = 'List of available commands:'\
				'\n$music - list available songs'\
				'\n!play <song name> or <youtube url> - play a song'\
				'\n!playing - print the song that is currently playing'\
				'\n!radio <playlist> - Plays a playlist as if it was on the radio'\
				'\n!stop - stop the player'\
 				'\n!pause - pause the player'\
				'\n!resume - resume the player'\
				'\n!shuffle - play a shuffled playlist'\
				'\n!next - play the next song in the playlist'\
				'\n!queue - show the songs currently in the queue'\
				'\n!clearqueue - remove all songs from the queue'\
				'\n!help - print this message'
