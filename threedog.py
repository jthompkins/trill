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
import sys
import threading
import threedog_bot_constants
import time
import urllib
import urllib.request as urllib2
import youtube_dl
from bs4 import BeautifulSoup


class ThreeDog():

	#Command prefix. Messages in discord that start with this character will be recognized by Three Dog.
	command_prefix = "$"
	client = discord.Client()
	bot = Bot(command_prefix = command_prefix)
	
	vc = None
	
	voicelines_dir = "./voicelines/"
	records_dir = "./records/"
	

	def __init__(self):
		

		print("Retrieving code from environment variable THREEDOGCODE")
		self.threedog_code = threedog_bot_constants.THREEDOG_CODE
		if self.threedog_code is None:
			sys.exit("No bot code was defined for Three Dog. This OAuth code needs to be set as an environment variable.")
	def run(self):
		print("Starting bot threedog client")
		self.client.run(self.threedog_code)

	''' Three Dog actions'''

	@client.event
	async def on_ready():
		print("Three Dog is ready.")
	
	@client.event
	async def on_message(message):
		if message.content.startswith(ThreeDog.bot.command_prefix):
			command = message.content[len(ThreeDog.bot.command_prefix):]
			mesg = message.content.lower()[len(ThreeDog.bot.command_prefix):]
			print("Command received: "+command+"\nfrom user: "+str(message.author)+"\n")
			
			#await message.channel.send("Hello there!")
			if mesg.startswith('radio'):
				await ThreeDog.radio_action(message)
			
			elif mesg.startswith('pause'):
				await ThreeDog.pause_action(message)
				
			elif mesg.startswith('stop'):
				await ThreeDog.stop_action(message)
				
			elif mesg.startswith('resume'):
				await ThreeDog.resume_action(message)
			
			elif  mesg.startswith('stock'):
				await ThreeDog.stock_action(message,mesg)
			
			elif mesg.startswith('logout'):
				await ThreeDog.logout_action(message)
			
			
		
		#Ignore all messages without the prefix.
		else:
			pass
			
			
	#Method for Three Dog to DJ Galaxy News Radio
	
	async def radio_action(message):
		'''
		Structure: Play a voice line. Play 2-3 songs. Play a voice line.
	
		Shuffles through voice lines. Shuffles through songs.
	
		'''
		
		channel = message.author.voice.channel
		if ThreeDog.vc is None or not ThreeDog.vc.is_connected():
			ThreeDog.vc = await channel.connect()
		elif ThreeDog.vc.is_connected():
			await ThreeDog.vc.move_to(channel)
		
		voiceline = str(ThreeDog.item_shuffle(ThreeDog.voicelines_dir, '.mp3')[0])
		ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
		print("Playing voice line: " + voiceline)
		while ThreeDog.vc.is_playing():
			time.sleep(1)

		song = str(ThreeDog.item_shuffle(ThreeDog.records_dir, '.mp3')[0])
		ThreeDog.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
		print("Playing song: " + song)
		await message.channel.send("Now playing:	"+ song.replace('./records', '').replace('\\','').replace('.mp3', '') )
		
		#while ThreeDog.vc.is_playing():
		#	time.sleep(1)
		
		
	async def pause_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.pause()
			await message.channel.send("Pausing the music.")
	async def stop_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.stop()
			await message.channel.send("Stopping the music.")
	async def resume_action(message):
		if ThreeDog.vc is  not None:
			ThreeDog.vc.resume()
			await message.channel.send("Resuming music.")
			
	#Method to read in a stock symbol and return the current price of that stock.
	async def stock_action(message, mesg):
		stock = mesg.split('stock', 1)[1].replace(' ','').upper()
		url = 'https://old.nasdaq.com/symbol/'+stock
		try:
			print(url)
			f = urllib2.urlopen(url)
		except urllib.error.HTTPError as error:
			print(error)
			return
		f_list = str(f.read())
		stock_element = '<div class="qwidget-symbol">'+stock+'&nbsp;</div>'
	
		try:
			price_element = '<div id="qwidget_lastsale" class="qwidget-dollar">'
			price_end = '</div>'
			price_found = f_list.split(price_element)[1].split(price_end)[0]
		
			stock_price = price_found
			await message.channel.send(stock +' is currently trading at '+stock_price)
		except IndexError:
			await message.channel.send('Could not find '+stock)
		
	#Method for logging the bot client out.
	async def logout_action(message):
		print("Logging off")
		await ThreeDog.bot.close()
		await ThreeDog.client.close()
		
		
	#Returns a random item in the provided directory
	def item_shuffle(dir, ext):
		item_list = glob.glob(dir + '/*' + ext)
		list_len = len(item_list)
		rand = randint(0, list_len - 1)
		shuffle(item_list)
		#
		return item_list
		

if __name__ == "__main__":
	try:
		dj = ThreeDog()
		dj.run()
	except KeyboardInterrupt:
		print("Keyboard interrupt detected.")
		sys.exit(0)
	#client = discord.Client()
	#client.run(threedog_bot_constants.THREEDOG_CODE)
	
	