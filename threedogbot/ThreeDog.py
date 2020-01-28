import asyncio
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import glob
import logging
from mutagen.id3 import ID3
import os
from pathlib import Path
import queue
from random import randint
from random import shuffle
import _thread
import threading
import threedog_bot_constants
import time
import urllib
import urllib.request as urllib2
from bs4 import BeautifulSoup

class ThreeDog(discord.Client):

	logger = logging.getLogger('discord')
	logger.setLevel(logging.DEBUG)
	handler = logging.FileHandler(filename='threedog.log', encoding='utf-8', mode='w')
	handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
	logger.addHandler(handler)
	Client = discord.Client()
	client = Bot(command_prefix = "$")

	#global variables
	connection = None
	voice = None
	player = None
	playing = False
	userdisconnect = False
	next = False
	curr_vol = 0.05
	q = queue.Queue()
	loop = asyncio.get_event_loop()
	def __init__(self):
		
		threading.Thread(target=self.worker).start()
		
		
	def worker(self):
		while True:
			
			items = self.q.get()
			if item is None:
				continue
			func = items[0]
			args = items[1:]
			func(*args)
			self.q.task_done()
		
	@asyncio.coroutine
	async def on_ready():
		print('Three Dog is ready.')
		print('User name: '+self.client.user.name)
		print('User id:   '+self.client.user.id)
		print('------------')
		open('./threedogbot.lock', 'a')
	
	#def run(self, code):
	#	self.client.run(code)

	@asyncio.coroutine
	async def on_message(self, message):
		
		if message.content.startswith(self.client.command_prefix):
			mesg = message.content.lower()[len(self.client.command_prefix):]
			mesg_orig = message.content[len(self.client.command_prefix):]
			print('\ncommand: '+mesg+'\nuser: '+str(message.author)+'\n')
			
			#HELP
			#
			#
			if mesg.lower() == 'help':
				await self.client.send_message(message.channel, threedog_bot_constants.HELP_MESSAGE) 
				
			#PAUSE
			#
			#
			elif mesg.lower() == 'pause':
				if message.author.voice_channel:
					if player is not None and voice is not None and playing:
						player.pause()
						print("player paused")
						playing = False
					else:
						print("nothing playing")
					print('done')
				else:
					await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)
				
				
			#RESUME
			#
			#
			elif mesg.lower() == 'resume':
				if message.author.voice_channel:
					if player is not None and voice is not None:
						if playing:
							await client.send_message(message.channel, 'Already playing a song.')
							return
						player.resume()
						print("player resumed")
						playing = True
					else:
						await client.send_message(message.channel, "Nothing is paused.")
				else:
					await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)

			#STOP
			#
			#
			elif mesg.lower() == 'stop':
				if message.author.voice_channel:
					if player is not None and voice is not None and userdisconnect is False:
						await voice.disconnect()
						player.stop()
						player = None
						voice = None
						time.sleep(1)
						playing = False
						userdisconnect = True
						print("player stopped")
						await client.change_presence(game=discord.Game(name=None))
					else:
						await client.send_message(message.channel, "Nothing is playing.")
				else:
					await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)
					
			#VOLUME
			#
			#
			elif mesg.lower().startswith('volume'):
				if message.author.voice_channel:
					try:
						vol_direction = mesg.split('volume', 1)[1].replace(' ','').lower()
						if vol_direction == 'up':
							if curr_vol <= threedog_bot_constants.MAX_VOL:
								curr_vol += threedog_bot_constants.VOL_INC
								curr_vol = round(curr_vol, 1)
								try:
									player.volume = curr_vol
								except:
									pass
								await client.send_message(message.channel, 'Increasing volume to '+str(int(curr_vol*100))+'%')
							else:
								await client.send_message(message.channel, 'At max volume...')
								return
						elif vol_direction == 'down':
							if curr_vol >= threedog_bot_constants.MIN_VOL:
								curr_vol -= threedog_bot_constants.VOL_INC
								curr_vol = round(curr_vol, 1)
								try:
									player.volume = curr_vol
								except:
									pass
								await client.send_message(message.channel, 'Decreasing volume to '+str(int(curr_vol*100))+'%')
							else:
								await client.send_message(message.channel, 'At minimum volume...')
								
						elif isinstance(int(vol_direction), int):
							vol_set = int(vol_direction)
							try:
								if vol_set <= 200 and vol_set >= 0:
									curr_vol = float(vol_set/100)
									try:
										player.volume = curr_vol
									except:
										pass
									await client.send_message(message.channel, 'Setting volume to '+str(int(curr_vol*100))+'%')
								else:
									await client.send_message(message.channel, 'Invalid volume setting.')
							except TypeError as e:
								await client.send_message(message.channel, 'Invalid volume setting.')
								print(e)
						else:
							await client.send_message(message.channel, 'Invalid argument: type [up] or [down] or [<integer between 0 and 200>]')
					except Exception as e:
						pass
				else:
					await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)


			#MUSIC
			#
			#
			elif mesg == 'music':
				options = list_options(threedog_bot_constants.MUSIC_FILE)
				music_count = 0
				f = open(threedog_bot_constants.MUSIC_LIST_FILE, 'w')
				for i in options:
					i_split = i.split('.', 1)[0]
					#only add to list if mp3
					try:
						if i.split('.', 1)[1] == threedog_bot_constants.MUSIC_EXTENSION:
							artist = 'Unknown'
							try:
								artist = ID3(threedog_bot_constants.MUSIC_FILE+i)['TPE1'].text[0]
							except KeyError as e:
								pass
							except IndexError as e:
								pass
							f.write('Song:   '+str(i_split)+'\nArtist: '+artist+'\n\n')
							music_count += 1
					except IndexError as e:
						pass
				f.close()
				await client.send_message(message.channel, 'Available songs: '+str(music_count))
				await client.send_file(message.channel, threedog_bot_constants.MUSIC_LIST_FILE)
				
				
			#PLAY
			#
			#
			elif mesg.lower().startswith('play'):
				file_valid = False
				if player is not None and playing:
					try:
						await voice.disconnect()
						userdisconnect = True
						player.stop()
						player = None
						voice = None
						youtube = None
						time.sleep(1)
					except Exception as e:
						print("not playing anything")
						print(e)
				s_split = play_split(mesg)
				try:
					if 'youtube.com/watch' in mesg.split('play', 1)[1]:
						source_file = mesg_orig.split('play', 1)[1].replace(' ', '')
						youtube = True
						file_valid = True
					#Takes in a string and searches youtube using that string; outputs url for 
					elif mesg.startswith('playyoutube'):
						search = mesg_orig.split('playyoutube ', 1)[1]
						query = urllib.parse.quote(search)
						url = threedog_bot_constants.YOUTUBE_SEARCH + query
						response = urllib2.urlopen(url)
						html = response.read()
						soup = BeautifulSoup(html, 'html.parser')
						
						vidList = []
						for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
							vidList.append('https://www.youtube.com' + vid['href'])
						source_file = vidList[0]
						print(source_file)
						
						if source_file.startswith('https://www.youtube.com/watch'):
							file_valid = True
							youtube = True
					else:
						source_file = glob.glob(threedog_bot_constants.MUSIC_FILE+'*'+s_split+'*'+threedog_bot_constants.MUSIC_EXTENSION)[0]
						file_valid = True
						youtube = False
				except IndexError as e:
					print("index not there")
					print(str(e))
				
				
				
				
				if file_valid:
					if message.author.voice_channel and not youtube:
						try:
							voice = await client.join_voice_channel(message.author.voice_channel)
							player = voice.create_ffmpeg_player(source_file)
							player.volume = curr_vol
							player.start()
							await client.change_presence(game=discord.Game(name='Galaxy News Radio'))
							playing = True
							userdisconnect = False
						except Exception as e:
							print(e)
					
					elif message.author.voice_channel and youtube:
						voice = await client.join_voice_channel(message.author.voice_channel)
						print(source_file)
						player = await voice.create_ytdl_player(source_file)
						player.volume = curr_vol
						player.start()
						await client.change_presence(game=discord.Game(name='Galaxy News Radio'))
						playing = True
						userdisconnect = False
					else:
						await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)
						pass
					count = 0
					
					artist = 'Unknown'
					try:
						artist = ID3(source_file)['TPE1'].text[0]
					except:
						pass
					if youtube == False:
						tmp = await client.send_message(message.channel, 'Playing:\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
					else:
						tmp = await client.send_message(message.channel, 'Playing from source:  '+str(source_file)+'\n'+time_stamp(count))
					while True:
						try:
							if len(voice.channel.voice_members) == 1:
								print ('channel is empty')
								player.pause()
								while len(voice.channel.voice_members) == 1:
									time.sleep(1)
							if playing:
								count+=1
								time.sleep(1)
								
							if youtube == False:
								await client.edit_message(tmp, 'Playing:\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
							else:
								await client.edit_message(tmp, 'Playing from source:  '+str(source_file)+'\n'+time_stamp(count))
											
							if player.is_done():
								await voice.disconnect()
								player.stop()
								print('done playing')
								await client.change_presence(game=None)
								if youtube == False:
									tmp = await client.send_message(message.channel, 'Finished Playing:\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
								else:
									tmp = await client.send_message(message.channel, 'Finished Playing from source:  '+str(source_file)+'\n'+time_stamp(count))
								break
							if not playing:
									await client.wait_for_message(author=message.author, content='$resume')
									player.resume()
						except Exception as e:
							print(e)
							break	
					
				else:
					await client.send_message(message.channel, "We don't have that record.")
				
					
			#NEXT
			#
			#
			elif mesg == 'next':
				if message.author.voice_channel:
					if playing and player is not None:
						next = True
						await client.send_message(message.channel, 'Playing next song...')
					else:
						return
				else:
					await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)
			
			#SHUFFLE
			#
			#
			elif mesg == 'shuffle':
				if player is not None and playing:
					try:
						await voice.disconnect()
						userdisconnect = True
						player.stop()
						player = None
						voice = None
						time.sleep(1)
					except Exception as e:
						print("not playing anything")
						print(e)

				userdisconnect = False
				
				
				shuffled_list = player_shuffle(threedog_bot_constants.MUSIC_FILE+'/*.mp3')
				song_count = 0
				while not userdisconnect:
					next = False
					if song_count >= len(shuffled_list):
						shuffled_list = player_shuffle(threedog_bot_constants.MUSIC_FILE+'/*.mp3')
						song_count = 0
					source_file = str(shuffled_list[song_count])
					song_count += 1
					num_songs = len(shuffled_list)
					
					if file_exists(source_file):
						print("Playing "+source_file)
						if message.author.voice_channel or player is not None:
							try:
								if voice is None:
									voice = await client.join_voice_channel(message.author.voice_channel)
								player = voice.create_ffmpeg_player(source_file)
								player.volume = curr_vol
								player.start()
								playing = True
							except Exception as e:
								print('problem creating shuffle player: '+str(e))
								return
							
						else:
							await client.send_message(message.channel, threedog_bot_constants.NO_VOICE_CHANNEL)
							break
							
						count = 0
						artist = 'Unknown'
						try:
							artist = ID3(source_file)['TPE1'].text[0]
						except:
							pass
						await client.change_presence(game=discord.Game(name='Galaxy News Radio'))
						tmp = await client.send_message(message.channel, '('+str(song_count)+'/'+str(num_songs)+') Playing:\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
						while not userdisconnect:
							try:
								
								if len(voice.channel.voice_members) == 1:
									print ('channel is empty: '+str(len(voice.channel.voice_members)))
									player.pause()
									while len(voice.channel.voice_members) == 1:
										time.sleep(1)
							
								time.sleep(1)
								#await client.send_message(message.channel, '$resume')
								if player.is_done() or next:
									print('done playing')
									await client.edit_message(tmp, '('+str(song_count)+'/'+str(num_songs)+') Finished playing\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
									player.stop()
									if userdisconnect:
										await voice.disconnect()
										return
									break
								elif playing:
									count+=1
									await client.edit_message(tmp, '('+str(song_count)+'/'+str(num_songs)+') Playing:\nSong:  '+str(source_file).split('\\', 1)[1].split('.mp3',1)[0]+'\nArtist: '+artist+'\n'+time_stamp(count))
								elif userdisconnect:
									await voice.disconnect()
									await client.change_presence(None)
									return
								if not playing:
									await client.wait_for_message(author=message.author, content='$resume')
									player.resume()
							except Exception as e:
								print('shuffle loop problem: '+str(e))
								return
					else:
						await client.send_message(message.channel, "We don't have that record.")
						
			elif mesg == 'logout':
				if str(message.author) == 'Darict#4089':
					print('logging out')
					await client.send_message(message.channel, 'Goodbye.')
					try:
						player.stop()
						await voice.disconnect()
					except:
						pass
					await client.logout()
				else:
					await client.send_message(message.channel, 'You are not the one.')
					await client.move_member(message.author, client.server.get_channel('AFK'))

			else:
				await client.send_message(message.channel, "Doesn't look like anything to me.")
		
		
	#Checks if file exists at given file path s
	def file_exists(self, s):
		my_file = Path(s)
		if my_file.exists():
			return True
		else:
			return False
		
	#Lists all files in the given directory
	def list_options(self, s):
		return os.listdir(s)
		
	#Takes an integer and converts to a minute/second time stamp
	def time_stamp(self, i):
		if i > 0:
			m, s = divmod(i, 60)
			return "%02d:%02d" % (m,s)
		else:
			return "00:00"
			
	#Splits strings after 'play' to parse what the user wants to play
	def play_split(self, s):
		if 'play' in s and ' ' in s:
			return s.split('play',1)[1].split(' ', 1)[1]
		elif 'play' in s:
			return s.split('play',1)[1]
		else:
			return s
		
	#Returns a random song in the music directory
	def player_shuffle(self, s):
		song_list = glob.glob(s)
		list_len = len(song_list)
		rand = randint(0, list_len - 1)
		self.shuffle(song_list)
		#
		return song_list	
		
		
if __name__ == '__main__':
	try:
		threedog = ThreeDog()
		threedog.run(threedog, threedog_bot_constants.THREEDOG_CODE)
	except KeyboardInterrupt:
		os.exit(0)
	