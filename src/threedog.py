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
    ROOT_DIR = "."
    VOICELINES_DIR = ROOT_DIR + "/voicelines/"
    RECORDS_DIR = ROOT_DIR + "/songs/"
    SONGS_DIR = ROOT_DIR + "/songs/"
    
    client = discord.Client()
    bot = Bot(command_prefix = COMMAND_PREFIX)
    vc = None
    song_queue = SongQueue()
    radio_on = False
    current_song = "Nothing"
    stop_playing = False

    def __init__(self):
        print("Retrieving code from environment variable THREEDOGCODE")
        self.threedog_code = threedog_bot_constants.THREEDOG_CODE
        if self.threedog_code is None:
            sys.exit("No bot code was defined for Three Dog. This OAuth code (THREEDOG_CODE) needs to be set as an environment variable.")
 
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
            
            if mesg.startswith('radio'):
                ThreeDog.stop_playing = False
                await ThreeDog.radio_action(message)
                
            elif mesg.startswith('playing'):
                await ThreeDog.playing_action(message)
                
            elif mesg.startswith('play'):
                ThreeDog.stop_playing = False
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
            
            elif mesg.startswith('queue'):
                await ThreeDog.queue_action(message)
            
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
            radio_playlist = 'fallout'
        else:
            radio_playlist = message.content[len(ThreeDog.bot.command_prefix):].split('radio', 1)[1].replace(' ','')
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
        
        #voiceline = str(ThreeDog.item_shuffle(ThreeDog.VOICELINES_DIR, '.mp3')[0])
        #ThreeDog.current_song = "Currently in between songs"
        #ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
        
        #print("Playing voice line: " + voiceline)
        #while ThreeDog.vc.is_playing():
        #    time.sleep(1)
            
        #song = str(ThreeDog.item_shuffle(radio_dir, '.mp3')[0])
        #ThreeDog.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
        #print("Playing song: " + song)
        await message.channel.send("Playing radio playlist: "+str(radio_playlist))
        
        #await message.channel.send("Now playing:    "+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') )
        #ThreeDog.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
        

        #Spin new thread to keep radio functions going. Pass the asyncio event loop to allow Three Dog to send messages.
        ThreeDog.radio_on = True
        t = threading.Thread(target=ThreeDog.radio_thread_action, args=(ThreeDog, message, radio_dir, asyncio.get_event_loop()))
        t.start()
        
    
    #Method to keep the radio functions going. Ran in a separate thread from radio_action.
    def radio_thread_action(self, message, radio_dir, loop):
        while ThreeDog.radio_on:
            while ThreeDog.vc.is_playing():
                time.sleep(1)

            if ThreeDog.song_queue.is_empty():
                songs = ThreeDog.item_shuffle(radio_dir, '.mp3')
                for song in songs:
                    ThreeDog.song_queue.enqueue_song(song)
            if not ThreeDog.radio_on:
                return
            voiceline = str(ThreeDog.item_shuffle(ThreeDog.VOICELINES_DIR, '.mp3')[0])
            ThreeDog.current_song = "Currently in between songs"
            ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
            
            print("Playing voice line: " + voiceline)
            while ThreeDog.vc.is_playing():
                time.sleep(1)
        
            if not ThreeDog.radio_on:
                return
            song = ThreeDog.song_queue.dequeue_song()
            ThreeDog.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
            print("Playing song: " + song)
            
            #Create a task in the asyncio loop to send a message to the channel.
            #loop.create_task( message.channel.send("Now playing:    "+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') ) )
            ThreeDog.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
        
    #Method for Three Dog to play a song.
    async def play_action(message):

        channel = message.author.voice.channel
        mesg = message.content[len(ThreeDog.bot.command_prefix):].split('play', 1)[1]
        ThreeDog.song_queue.enqueue_song(mesg)
        
        if ThreeDog.vc is not None and ThreeDog.vc.is_playing():
            await message.channel.send("Song added to queue.")
            #player = ytdlsource.YTDLSource.from_url_noasync(mesg, stream=False)
            return
        
        print("\nPlaying audio from: " + mesg)

        #Check if youtube url was passed.
        #if 'youtube.com/watch' in mesg or True:
        if ThreeDog.vc is None or not ThreeDog.vc.is_connected():
            ThreeDog.vc = await channel.connect()
            time.sleep(2)
        elif ThreeDog.vc.is_connected():
          await ThreeDog.vc.move_to(channel)
          time.sleep(2)
        
        await message.channel.send("Now playing audio from:    " + mesg)
        await ThreeDog.client.change_presence(status=discord.Status.online, activity=discord.Game(name='Galaxy News Radio'))
        t = threading.Thread(target=ThreeDog.play_thread_action, args=(ThreeDog, message))
        t.start()

        

    def play_thread_action(self, message):
        while not ThreeDog.song_queue.is_empty() and not ThreeDog.stop_playing:
        
            #Play voice line.
            voiceline = str(ThreeDog.item_shuffle(ThreeDog.VOICELINES_DIR, '.mp3')[0])
            ThreeDog.current_song = "Currently in between songs"
            ThreeDog.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
            print("Playing voice line: " + voiceline)
            while ThreeDog.vc.is_playing():
                    time.sleep(1)
            if ThreeDog.stop_playing:
                return
            source_file = ThreeDog.song_queue.dequeue_song()
            player = ytdlsource.YTDLSource.from_url_noasync(source_file, stream=True)
            ThreeDog.vc.play(player, after=lambda e: print("Finished playing song."))
            
            
            while ThreeDog.vc.is_playing():
                    time.sleep(1)
        
    async def pause_action(message):
        if ThreeDog.vc is  not None:
            ThreeDog.vc.pause()
            await message.channel.send("Music paused.")
    async def stop_action(message):
        ThreeDog.stop_playing = True
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

    async def queue_action(message):
        queue = ThreeDog.song_queue.get_queue()
        queue_output = '\n'
        for song in queue:
            queue_output = queue_output + song + '\n'
        await message.channel.send("Current songs in queue:    " + queue_output)
    async def clear_queue_action(message):
        ThreeDog.song_queue.clear_queue()
        await message.channel.send("Queue has been cleared.")

    async def help_action(message):
        if ThreeDog.vc is  not None:
            await message.channel.send(threedog_bot_constants.HELP_MESSAGE) 
        
        
    #Returns a random item in the provided directory
    def item_shuffle(dir, ext):
        print(dir)
        item_list = glob.glob(dir + '/*' + ext)
        list_len = len(item_list)
        rand = randint(0, list_len - 1)
        shuffle(item_list)
        #
        return item_list
    
    