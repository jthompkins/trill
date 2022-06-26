import asyncio
import discord
import youtube_dl

class YTDLSource(discord.PCMVolumeTransformer):
	YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
	'outtmpl' : 'songs/%(title)s_%(artist)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'no-overwrites': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes,
	'postprocessors' : [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
	}
	
	YTDL_PRE_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
	'outtmpl' : 'songs/%(title)s_%(artist)s.%(ext)s',
    'restrictfilenames': True,
    'simulate': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes,
	'postprocessors' : [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
	}

	FFMPEG_OPTIONS = {
    'options': '-vn'
}

	ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)
	ytdl_pre = youtube_dl.YoutubeDL(YTDL_PRE_FORMAT_OPTIONS)

	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')
		
		

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: YTDLSource.ytdl.extract_info(url, download=not stream))

		if 'entries' in data and len(data['entries']) > 0:
            # take first item from a playlist
			data = data['entries'][0]
		
		filename = data['url'] if stream else YTDLSource.ytdl.prepare_filename(data)
		filename = filename.replace('.webm','.mp3')
		filename = filename.replace('.m4a', '.mp3')

		return cls(discord.FFmpegPCMAudio(filename, **YTDLSource.FFMPEG_OPTIONS), data=data)

	def from_url_noasync(url, stream=False):

		#pre_data = YTDLSource.ytdl_pre.extract_info(url, download=not stream)
        #filename = pre_data

		#loop = loop or asyncio.get_event_loop()
		data = YTDLSource.ytdl.extract_info(url, download=not stream)

		if 'entries' in data and len(data['entries']) > 0:
            # take first item from a playlist
			data = data['entries'][0]
		
		filename = data['url'] if stream else YTDLSource.ytdl.prepare_filename(data)
		filename = filename.replace('.webm','.mp3')
		filename = filename.replace('.m4a', '.mp3')

		return discord.FFmpegPCMAudio(filename, **YTDLSource.FFMPEG_OPTIONS) #, data=data)
	
