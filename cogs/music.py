import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import asyncio
import random

tick = "<:green_tick:916215569269784606>"

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.music_q = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.isp = False
    
    def clear_q(self):
      self.music_q.clear()

    def get_embed(self, type, song):
      if type.lower() == "np":
        name = "Now Playing ~"
      elif type.lower() == "add":
        name = "Added Song to Queue ~"
      embed = discord.Embed(description=f"{song.capitalize()}", color=0xff455b)
      embed.set_author(
        name=f"{name}",
        icon_url="https://i.imgur.com/TLAvSQj.png"
      )
      return embed

    def sr_embed(self, type, desc):
      if type.lower() == "s":
        name = tick + "Song Skipped."
      elif type.lower() == "r":
        name = tick + desc
      embed = discord.Embed(description=name, color=0xff455b)
      return embed

    def q_embed(self):
      if len(self.music_q) == 0:
        desc = "Nothing in the Queue right now, Play something to add in the Queue."
      else:
        desc = ""
        for i in range(0, len(self.music_q)):
          if i == 0:
            song = f"**{i+1} ~ {self.music_q[i]['title']} ~ {self.music_q[i]['duration']}**\n\n"
          else:
            song = f"{i+1} ~ {self.music_q[i]['title']} ~ {self.music_q[i]['duration']}\n\n"
          desc = desc + song
      embed = discord.Embed(description=desc, color=0xff455b)
      embed.set_author(
        name="Player Queue",
        icon_url="https://i.imgur.com/TLAvSQj.png"
      )
      return embed

    def add_to_q(self, args):
        dur = args['duration']
        mins = dur//60
        sec = dur%60
        if sec<10:
            sec = f"0{sec}"
        song = {"title": f"{args['title']}", "duration": f"{mins}:{sec}", "data": f"{args['formats'][0]['url']}"}
        self.music_q.append(song)

    def search_yt(self, args):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{args}",download=False)['entries'][0]
            print(info['title'])
            dur = info['duration']
            print(dur)
            print(f"{dur//60}:{dur%60}")
        self.add_to_q(info)

    def get_title(self, args):
      with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{args}",download=False)['entries'][0]
      return(info['title'])
      
    async def connect_vc(self, ctx):
      if ctx.author.voice is None:
            await ctx.reply("You are not in any voice channel!")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
          await voice_channel.connect()
          embed = discord.Embed(description=f"{tick} Joined Channel {voice_channel.mention}.", color=0xff455b)
          await ctx.reply(embed=embed)
      elif ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.reply("I'm already playing in a VC.")
      elif ctx.voice_client and not ctx.voice_client.is_playing():
        await ctx.voice_client.move_to(voice_channel)
        embed = discord.Embed(description=f"{tick} Joined Channel {voice_channel.mention}.", color=0xff455b)
        await ctx.reply(embed=embed)

    async def play_next(self, ctx):
      if len(self.music_q) > 0:
        vc = ctx.voice_client
        self.music_q.pop(0)
        m_url = self.music_q[0]['data']
        source = await discord.FFmpegOpusAudio.from_probe(m_url, **self.FFMPEG_OPTIONS)
        vc.play(source, after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))
        embed = self.get_embed("np", self.music_q[0]['title'])
        await ctx.send(embed=embed)

    @commands.command()
    async def join(self, ctx):
        await self.connect_vc(ctx)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
      if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
        await ctx.voice_client.disconnect()
        self.clear_q()
        embed = discord.Embed(description=f"{tick} Disconnected and Cleared the Queue.", color=0xff455b)
        await ctx.send(embed=embed)
      else:
        await ctx.reply("You have to be in the sam VC as me to disconnect me.")

    @commands.command()
    async def pause(self, ctx):
      if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
        await ctx.voice_client.pause()
        embed = discord.Embed(description=f"{tick} Paused the Player.", color=0xff455b)
        await ctx.send(embed=embed)
      else:
        await ctx.reply("You need to be in the same VC.")

    @commands.command()
    async def resume(self, ctx):
      if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
        await ctx.voice_client.resume()
        embed = discord.Embed(description=f"{tick} Resumed the Player.", color=0xff455b)
        await ctx.send(embed=embed)
      else:
        await ctx.reply("You need to be in the same VC.")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, args):
        if ctx.voice_client is None:
          await self.connect_vc(ctx)
        print(ctx.voice_client.is_playing())
        if ctx.voice_client.is_playing() is False:
          vc = ctx.voice_client
          self.search_yt(args)
          m_url = self.music_q[0]['data']
          source = await discord.FFmpegOpusAudio.from_probe(m_url, **self.FFMPEG_OPTIONS)
          vc.play(source, after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))
          emb1 = self.get_embed("np", self.get_title(args))
          await ctx.send(embed=emb1)
        elif ctx.voice_client.is_paused():
          self.search_yt(args)
          emb2 = self.get_embed("add", self.get_title(args))
          await ctx.send(embed=emb2)
        else:
          self.search_yt(args)
          emb3 = self.get_embed("add", self.get_title(args))
          await ctx.send(embed=emb3)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
      embed=self.q_embed()
      await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx):
      if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
        self.clear_q()
        ctx.voice_client.stop()
        embed = discord.Embed(description=f"{tick} Cleared the Queue.", color=0xff455b)
        await ctx.reply(embed=embed)
      else:
        await ctx.reply("You have to be in the same VC to clear the Queue.")

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
      if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
        ctx.voice_client.stop()
        embed = self.sr_embed("s", "desc")
        await ctx.send(embed=embed)
        #await self.queue(ctx)
        #await self.play_next(ctx)
        #await ctx.reply("Skipped the current song.")
      else:
        await ctx.reply("You have to be in the same VC to skip any song.")

    @commands.command()
    async def remove(self, ctx, *, index):
      for i in range(0, len(self.music_q)):
        flag = 0
        if int(index) == i+1:
          print("yes")
          self.music_q.pop(i)
          flag = flag + 1
          break
      print(flag)
      if flag == 1:
        embed = self.sr_embed("r", f"Removed Song at position {index} from Queue.")
        await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx):
      top = self.music_q.pop(0)
      random.shuffle(self.music_q)
      self.music_q.append(top)
      embed = discord.Embed(description=f"{tick} Shuffled the Queue.", color=0xff455b)
      await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Music(client))
    print(">> Music loaded")