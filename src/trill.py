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
import trill_bot_constants
import time
import urllib
import urllib.request as urllib2
import youtube_dl
from bs4 import BeautifulSoup
import ytdlsource


class Trill():

    #Command prefix. Messages in discord that start with this character will be recognized by Trill.
    COMMAND_PREFIX = "!"
    ROOT_DIR = "."
    RECORDS_DIR = ROOT_DIR + "/songs/"
    SONGS_DIR = ROOT_DIR + "/songs/"
    
    intents = discord.Intents.all()
    
    client = discord.Client(intents=intents)
    bot = Bot(command_prefix = COMMAND_PREFIX)
    vc = None
    song_queue = SongQueue()
    radio_on = False
    current_song = "Nothing"
    stop_playing = False

    def __init__(self):
        print("Retrieving code from environment variable TRILLCODE")
        self.trill_code = trill_bot_constants.TRILL_CODE
        if trill_bot_constants.VOICELINES_DIR is not None:
            self.VOICELINES_DIR = trill_bot_constants.VOICELINES_DIR
        if self.trill_code is None:
            sys.exit("No bot code was defined for Trill. This OAuth code (TRILL_CODE) needs to be set as an environment variable.")
 
    def run(self):
        print("Starting bot trill client")
        self.client.run(self.trill_code)

    ''' Trill actions'''

    @client.event
    async def on_ready():
        print("Trill is ready.")
    
    @client.event
    async def on_message(message):
        if message.content.startswith(Trill.bot.command_prefix):
            command = message.content[len(Trill.bot.command_prefix):]
            mesg = message.content.lower()[len(Trill.bot.command_prefix):]
            print("Command received: "+command+"\nfrom user: "+str(message.author)+"\n")
            
            if mesg.startswith('radio'):
                Trill.stop_playing = False
                await Trill.radio_action(message)
                
            elif mesg.startswith('playing'):
                await Trill.playing_action(message)
                
            elif mesg.startswith('play'):
                Trill.stop_playing = False
                await Trill.play_action(message)
            
            elif mesg.startswith('pause'):
                await Trill.pause_action(message)
                
            elif mesg.startswith('stop'):
                await Trill.stop_action(message)
                
            elif mesg.startswith('resume'):
                await Trill.resume_action(message)
                
            elif mesg.startswith('next'):
                await Trill.next_action(message)
                
            elif mesg.startswith('logout'):
                await Trill.logout_action(message)
                
            elif mesg.startswith('help'):
                await Trill.help_action(message)
            
            elif mesg.startswith('queue'):
                await Trill.queue_action(message)

            elif mesg.startswith('clearqueue'):
                await Trill.clear_queue_action(message)

            else:
                await message.channel.send("Sorry pal. I didn't understand that command.")
        
        #Ignore all messages without the prefix.
        else:
            pass
            
            
    async def playing_action(message):
        await message.channel.send("Currently playing: " + str(Trill.current_song))
        
            
    #Method for Trill to DJ Galaxy News Radio
    async def radio_action(message):
        '''
        Structure: Play a voice line. Play 2-3 songs. Play a voice line.
    
        Shuffles through voice lines. Shuffles through songs.
    
        '''
        
        if message.content == '!radio':
            radio_dir = Trill.RECORDS_DIR + 'fallout'
            radio_playlist = 'fallout'
        else:
            radio_playlist = message.content[len(Trill.bot.command_prefix):].split('radio', 1)[1].replace(' ','')
            if os.path.isdir(Trill.RECORDS_DIR + radio_playlist):
                radio_dir = Trill.RECORDS_DIR + radio_playlist
            else:
                await message.channel.send("Invalid radio setting!")
                return
        
        if Trill.radio_on:
            await message.channel.send("Radio is already playing!")
            return
            
        await Trill.client.change_presence(status=discord.Status.online, activity=discord.Game(name='Galaxy News Radio'))
        channel = message.author.voice.channel
        if Trill.vc is None or not Trill.vc.is_connected():
            Trill.vc = await channel.connect()
        elif Trill.vc.is_connected():
            await Trill.vc.move_to(channel)
        
        #voiceline = str(Trill.item_shuffle(Trill.VOICELINES_DIR, '.mp3')[0])
        #Trill.current_song = "Currently in between songs"
        #Trill.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
        
        #print("Playing voice line: " + voiceline)
        #while Trill.vc.is_playing():
        #    time.sleep(1)
            
        #song = str(Trill.item_shuffle(radio_dir, '.mp3')[0])
        #Trill.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
        #print("Playing song: " + song)
        await message.channel.send("Playing radio playlist: "+str(radio_playlist))
        
        #await message.channel.send("Now playing:    "+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') )
        #Trill.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
        

        #Spin new thread to keep radio functions going. Pass the asyncio event loop to allow Trill to send messages.
        Trill.radio_on = True
        t = threading.Thread(target=Trill.radio_thread_action, args=(Trill, message, radio_dir, asyncio.get_event_loop()))
        t.start()
        
    
    #Method to keep the radio functions going. Ran in a separate thread from radio_action.
    def radio_thread_action(self, message, radio_dir, loop):
        while Trill.radio_on:
            while Trill.vc.is_playing():
                time.sleep(1)

            if Trill.song_queue.is_empty():
                songs = Trill.item_shuffle(radio_dir, '.mp3')
                for song in songs:
                    Trill.song_queue.enqueue_song(song)
            if not Trill.radio_on:
                return
            Trill.current_song = "Currently in between songs"

            voiceline = Trill.get_voiceline()
            if voiceline is not None:
                Trill.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
                print("Playing voice line: " + voiceline)
                while Trill.vc.is_playing():
                    time.sleep(1)
        
            if not Trill.radio_on:
                return
            song = Trill.song_queue.dequeue_song()
            Trill.vc.play(discord.FFmpegPCMAudio(song), after=lambda e: print("Finished playing song."))
            print("Playing song: " + song)
            
            #Create a task in the asyncio loop to send a message to the channel.
            #loop.create_task( message.channel.send("Now playing:    "+ song.replace(radio_dir, '').replace('\\','').replace('.mp3', '') ) )
            Trill.current_song = song.replace(radio_dir, '').replace('\\','').replace('.mp3', '')
        
    #Method for Trill to play a song.
    async def play_action(message):

        
        mesg = message.content[len(Trill.bot.command_prefix):].split('play', 1)[1]
        if mesg != '':
          Trill.song_queue.enqueue_song(mesg)
        elif mesg == '' and Trill.song_queue.is_empty():
          await message.channel.send("No song specified and nothing in the queue.")
          return
        else:
          pass
        channel = message.author.voice.channel
        
        if Trill.vc is not None and Trill.vc.is_playing():
            await message.channel.send("Song added to queue: " + mesg)
            #player = ytdlsource.YTDLSource.from_url_noasync(mesg, stream=False)
            return
        
        print("\nPlaying audio from: " + mesg)

        #Check if youtube url was passed.
        #if 'youtube.com/watch' in mesg or True:
        if Trill.vc is None or not Trill.vc.is_connected():
            Trill.vc = await channel.connect()
            time.sleep(2)
        elif Trill.vc.is_connected():
          await Trill.vc.move_to(channel)
          time.sleep(2)
        
        await message.channel.send("Now playing audio:    " + mesg)
        await Trill.client.change_presence(status=discord.Status.online, activity=discord.Game(name='Galaxy News Radio'))
        t = threading.Thread(target=Trill.play_thread_action, args=(Trill, message))
        t.start()

        

    def play_thread_action(self, message):
        while not Trill.song_queue.is_empty() and not Trill.stop_playing:
        
            #Play voice line.
            voiceline =  Trill.get_voiceline()
            if voiceline is not None:
                Trill.current_song = "Currently in between songs"
                Trill.vc.play(discord.FFmpegPCMAudio(voiceline), after=lambda e: print("Finished playing voice line."))
                print("Playing voice line: " + voiceline)
                while Trill.vc.is_playing():
                    time.sleep(1)

            if Trill.stop_playing:
                return

            source_file = Trill.song_queue.dequeue_song()
            player = ytdlsource.YTDLSource.from_url_noasync(source_file, stream=True)
            Trill.vc.play(player, after=lambda e: print("Finished playing song."))
            print("Playing song: " + source_file)
            Trill.current_song = source_file
            
            while Trill.vc.is_playing():
                    time.sleep(1)
        
    async def pause_action(message):
        if Trill.vc is  not None:
            Trill.vc.pause()
            await message.channel.send("Music paused.")
    async def stop_action(message):
        Trill.stop_playing = True
        if Trill.vc is  not None:
            Trill.vc.stop()
            await message.channel.send("Stopping the current song.")
            Trill.radio_on = False

            await Trill.client.change_presence(status=discord.Status.idle, activity=None)
    async def resume_action(message):
        if Trill.vc is  not None:
            Trill.vc.resume()
            await message.channel.send("Music resumed.")
            
    async def next_action(message):
        if Trill.vc is  not None:
            Trill.vc.stop()
            await message.channel.send("Skipping this track.")
                
    #Method for logging the bot client out.
    async def logout_action(message):
        if str(message.author) == 'Darict#4089':
            print("Logging off")
            await Trill.bot.close()
            await Trill.client.close()
        else:
            await message.channel.send("I can't let you do that " + str(message.author))

    async def queue_action(message):
        queue = Trill.song_queue.get_queue()
        if queue is None:
            await message.channel.send("No songs in the queue.")
            return
        queue_output = '\n'
        song_order = 1
        for song in queue:
            queue_output = queue_output + str(song_order) + ': ' + song + '\n'
            song_order += 1
        await message.channel.send("Current songs in queue:    " + queue_output)

    async def clear_queue_action(message):
        if str(message.author) == 'Darict#4089':
            Trill.song_queue.clear_queue()
            await message.channel.send("Queue has been cleared.")
        else:
            await message.channel.send("I can't let you do that " + str(message.author))

    async def help_action(message):
        await message.channel.send(trill_bot_constants.HELP_MESSAGE) 
        
        
    #Returns a random item in the provided directory
    def item_shuffle(dir, ext):
        print(dir)
        item_list = glob.glob(dir + '/*' + ext)
        list_len = len(item_list)
        rand = randint(0, list_len - 1)
        shuffle(item_list)
        #
        return item_list

    #Returns a random voiceline to play
    def get_voiceline():
        if trill_bot_constants.VOICELINES_DIR is not None:
            voiceline_list = Trill.item_shuffle(Trill.VOICELINES_DIR, '.mp3')
            if len(voiceline_list) > 0:
                return str(voiceline_list[0])
        return None
    
    
