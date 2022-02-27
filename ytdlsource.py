import asyncio
import discord
import youtube_dl

class YTDLSource(discord.PCMVolumeTransformer):
	ytdl_format_options = {
    'format': 'bestaudio/best',
	'outtmpl' : 'songs/%(title)s_%(artist)s.%(ext)s',
    'restrictfilenames': True,
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

	ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
	
	ffmpeg_options = {
    'options': '-vn'
}

	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: YTDLSource.ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
            # take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else YTDLSource.ytdl.prepare_filename(data)
		filename = filename.replace('.webm','.mp3')
		return cls(discord.FFmpegPCMAudio(filename, **YTDLSource.ffmpeg_options), data=data)
		
	async def download(url):
		loop = asyncio.get_event_loop()
		info = await loop.run_in_executor(None, lambda: YTDLSource.ytdl.extract_info(url, download=False))
		filename = YTDLSource.ytdl.prepare_filename(info)
		YTDLSource.ytdl.download([url])
		return filename
		
	
