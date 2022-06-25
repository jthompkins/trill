#!/usr/bin/python

#IMPORTS
import asyncio
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get
import glob
import logging
from mutagen.id3 import ID3
import os
from pathlib import Path
from random import randint
from random import shuffle
from song_queue import SongQueue
import sys
import threading
import threedog_bot_constants
import time
import urllib
import urllib.request as urllib2
import youtube_dl
from bs4 import BeautifulSoup
import ytdlsource


class ThreeDog():

	#Command prefix. Messages in discord that start with this character will be recognized by Three Dog.
	COMMAND_PREFIX = "!"
	ROOT_DIR = ".."
	VOICELINES_DIR = "$ROOT_DIR/voicelines/"
	RECORDS_DIR = "$ROOT_DIR/songs/"
	SONGS_DIR = "$ROOT_DIR/songs/"
	
	client = discord.Client()
	
	def __init__(self):
		print("Retrieving code from environment variable THREEDOGCODE")
		self.threedog_code = threedog_bot_constants.THREEDOG_CODE
		if self.threedog_code is None:
			sys.exit("No bot code was defined for Three Dog. This OAuth code (THREEDOG_CODE) needs to be set as an environment variable.")
		
		self.vc = None
		self.radio_on = False
		self.current_song = "Nothing"
		
		self.bot = Bot(command_prefix = ThreeDog.COMMAND_PREFIX)
		
		
	def run(self):
		print("Starting bot threedog client")
		self.client.run(self.threedog_code)

	''' Three Dog actions'''

	@client.event
	async def on_ready():
		print("Three Dog is ready.")
	
	@client.event
	async def on_message(message):
		if message.content.startswith(ThreeDog.bot.COMMAND_PREFIX):
			command = message.content[len(ThreeDog.bot.COMMAND_PREFIX):]
			mesg = message.content.lower()[len(ThreeDog.bot.COMMAND_PREFIX):]
			print("Command received: "+command+"\nfrom user: "+str(message.author)+"\n")
			
			if mesg.startswith('radio'):
				await ThreeDog.radio_action(message)
				
			elif mesg.startswith('playing'):
				await ThreeDog.playing_action(message)
				
			elif mesg.startswith('play'):
				await ThreeDog.play_action(message)
			
			elif mesg.startswith('pause'):
				await ThreeDog.pause_action(message)
				
			elif mesg.startswith('stop'):
				await ThreeDog.stop_action(message)
				
			elif mesg.startswith('resume'):
				await ThreeDog.resume_action(message)
				
			elif mesg.startswith('next'):
				await ThreeDog.next_action(message)
				
			elif mesg.startswith('logout'):
				await ThreeDog.logout_action(message)
				
			elif mesg.startswith('help'):
				await ThreeDog.help_action(message)
			
			else:
				await message.channel.send("Sorry pal. I didn't understand that command.")
		
		#Ignore all messages without the prefix.
		else:
			pass
			
			
	async def playing_action(message):
		await message.channel.send("Currently playing: " + str(ThreeDog.current_song))
		
			
	#Method for Three Dog to DJ Galaxy News Radio
	async def radio_action(message):
		'''
		Structure: Play a voice line. Play 2-3 songs. Play a voice line.
	
		Shuffles through voice lines. Shuffles through songs.
	
		'''
		
		if message.content == '!radio':
			radio_dir = ThreeDog.RECORDS_DIR + 'fallout'
		else:
			radio_playlist = message.content[len(ThreeDog.bot.COMMAND_PREFIX):].split('radio', 1)[1].replace(' ','')
			if os.path.isdir(ThreeDog.RECORDS_DIR + radio_playlist):
				radio_dir = ThreeDog.RECORDS_DIR + radio_playlist
			else:
				await message.channel.send("Invalid radio setting!")
				return
		
		if ThreeDog.radio_on:
			await message.channel.send("Radio is already playing!")
			return
			
		await ThreeDog.client.change_presence(status=discord.Status.online, activity=discord.Game(name='Galaxy News Radio'))
		channel = message.author.voice.channel
		if ThreeDog.vc is None or not ThreeDog.vc.is_connected():
			ThreeDog.vc = await channel.connect()
		elif ThreeDog.vc.is_connected():
			await ThreeDog.vc.move_to(channel)
		
		voiceline = str(ThreeDog.item_shuffle(ThreeDog.VOICELINES_DIR, '.mp3')[0])
		ThreeDog.current_song = "Currently in between songs"
		ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
		
		print("Playing voice line: " + voiceline)
		while ThreeDog.vc.is_playing():
			time.sleep(1)
			
		song = str(ThreeDog.item_shuffle(radio_dir, '.mp3')[0])
		ThreeDog.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
		print("Playing song: " + song)
		await message.channel.send("Playing radio playlist: "+str(radio_playlist))
		
		#await message.channel.send("Now playing:	"+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') )
		ThreeDog.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
		

		#Spin new thread to keep radio functions going. Pass the asyncio event loop to allow Three Dog to send messages.
		ThreeDog.radio_on = True
		t = threading.Thread(target=ThreeDog.radio_thread_action, args=(ThreeDog, message, radio_dir, asyncio.get_event_loop()))
		t.start()
		
	
	#Method to keep the radio functions going. Ran in a separate thread from radio_action.
	def radio_thread_action(self, message, radio_dir, loop):
		while self.radio_on:
			while ThreeDog.vc.is_playing():
				time.sleep(1)
			
			voiceline = str(ThreeDog.item_shuffle(ThreeDog.VOICELINES_DIR, '.mp3')[0])
			ThreeDog.current_song = "Currently in between songs"
			ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
			
			print("Playing voice line: " + voiceline)
			while ThreeDog.vc.is_playing():
				time.sleep(1)
		
			song = str(ThreeDog.item_shuffle(radio_dir, '.mp3')[0])
			ThreeDog.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
			print("Playing song: " + song)
			
			#Create a task in the asyncio loop to send a message to the channel.
			#loop.create_task( message.channel.send("Now playing:	"+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') ) )
			ThreeDog.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
		
	#Method for Three Dog to play a song.
	async def play_action(message):
	
		if ThreeDog.vc is not None:
			await ThreeDog.stop_action(message)
	
		
		channel = message.author.voice.channel
		mesg = message.content[len(ThreeDog.bot.COMMAND_PREFIX):].split('play', 1)[1]
		
		print("\nPlaying audio from: " + mesg)

		#Check if youtube url was passed.
		if 'youtube.com/watch' in mesg or True:
			source_file = mesg
			if ThreeDog.vc is None:
				ThreeDog.vc = await channel.connect()
			player = await ytdlsource.YTDLSource.from_url(source_file, stream=False)
			ThreeDog.vc.play(player, after=lambda e: print("Finished playing song."))
			await message.channel.send("Now playing audio from:	" + mesg)
			await ThreeDog.client.change_presence(status=discord.Status.online, activity=discord.Game(name='Galaxy News Radio'))
			
			
			
		
	async def pause_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.pause()
			await message.channel.send("Music paused.")
	async def stop_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.stop()
			#await message.channel.send("Stopping the current song.")
			ThreeDog.radio_on = False
			await ThreeDog.client.change_presence(status=discord.Status.idle, activity=None)
	async def resume_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.resume()
			await message.channel.send("Music resumed.")
			
	async def next_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.stop()
			await message.channel.send("Skipping this track.")
				
	#Method for logging the bot client out.
	async def logout_action(message):
		print("Logging off")
		await ThreeDog.bot.close()
		await ThreeDog.client.close()
		
	async def help_action(message):
		if ThreeDog.vc is  not None:
			await message.channel.send(threedog_bot_constants.HELP_MESSAGE) 
		
		
	#Returns a random item in the provided directory
	def item_shuffle(dir, ext):
		item_list = glob.glob(dir + '/*' + ext)
		list_len = len(item_list)
		rand = randint(0, list_len - 1)
		shuffle(item_list)
		#
		return item_list
	
	