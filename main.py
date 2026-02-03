#Importing section
import discord
import nacl
import ffmpeg
import asyncio
from discord.ext import commands
import os


#preparation Variable Code
TOKEN = "QWERTY12345" #Your Bot Token
Voice = 123456789 #Online bot message
Owner = 123456789  #for easter egg miss mention / trolling user target
MusicLibrary = "/path/to/song/folder" #Your song libraries

Queue = []
is_repeating = False 
queue_repeat = False 


#preparation data code
intents = discord.Intents.default()
intents.typing = True
intents.messages = True
intents.presences = True
intents.message_content = True

#bot intents preparation
bot = commands.Bot(command_prefix="ph!",intents = intents) #Setting prefix here

#Function
def play_next(ctx): #Running the Queue untill it finish
    global Queue
    global is_repeating
    global queue_repeat
    if len(Queue) > 0:
        if is_repeating: #if repeat current is active
            pass
        elif queue_repeat: #if repeat queue is active
            finished_song = Queue.pop(0)
            Queue.append(finished_song)
        else:
            Queue.pop(0)

        if len(Queue) > 0: # Theres song inside queue
            next_song = os.path.join(MusicLibrary, Queue[0])
            ctx.voice_client.play(discord.FFmpegPCMAudio(next_song), after=lambda e: play_next(ctx))

            label = "Looping" if is_repeating else "Coming up"
            asyncio.run_coroutine_threadsafe(ctx.send(f"{label}: **{Queue[0]}**"), bot.loop)
        
        else: # No more song in queue
            asyncio.run_coroutine_threadsafe(ctx.send("Queue Finished, you can add more by ph!queueadd"), bot.loop)


#Event Bot area
@bot.event
async def on_ready(): #Bot startup process
    #Succefully Logged In
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    message = await bot.fetch_channel(Voice)
    await message.send("**I'M ALIVE BABY!!!**")
    
    #Presence of Listening To
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name="My Owner yapping" # Change your discord activity gere
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_message(message): # if user tagged bot instead of the owner/trolling user target
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        await message.channel.send(f"{message.author.mention}! you tagged the wrong guy **You fool!**")
        await message.channel.send(f"The person that messing with you is <@{Owner}>")
    
    await bot.process_commands(message)

#Command bot area
@bot.command()
async def joinme(ctx): #Make the bot join to Voice
    if ctx.voice_client:
        await ctx.send("**I'M ALREADY CONNECTED BRO!**")
    
    elif ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("**I'm here**, What do you need from me mate?")

    else:
        await ctx.send("**BRO**, you are not even in any of the voice")

@bot.command() #Make the bot leave the voice
async def leaveme(ctx):
    global Queue, is_repeating
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("I left you now, **take care!**")
        Queue = []
        is_repeating = False
    else:
        await ctx.send("**Bruh**, I'm not in any of the voice bro")

@bot.command() #Sending all available Command
async def command(ctx):
    description_command = """
This is the following command that packed with the bot

The bot prefix is ph!

**ph!command**            #Show all the available command for the bot
**ph!joinme**             #Make the bot join your current voice
**ph!leaveme**            #Make the bot Leave your current voice
**ph!playlist**           #Show all the availabe song from the bot
**ph!queueadd <index>**   #Adding the selection song from the bot to queue
**ph!queue**              #Show current playing and incoming song
**ph!play**               #start play your queue
**ph!repeatcurrent**      #repeating current song playing
**ph!repeatqueue**        #repeating all queue
**ph!skip**               #skipping current playing song

Song once selected can't be removed, **choose wisely!**
proudly made by philip_ganteng
"""
    Embed = discord.Embed(
        title = "Bot Command",
        description = description_command,
        color = discord.Color.blue()
    )
    await ctx.send(embed=Embed)

@bot.command() #Showing all the Queue
async def queue(ctx):
    if(len(Queue) == 0):
        await ctx.send("**BRO**, your queue is empty")
        await ctx.send("**Try find and add your song from my library using ph!playlist and ph!queueadd!**")
    else:
        now_playing = Queue[0]
        upcoming = "\n".join([f"{i+1}. {song}" for i, song in enumerate(Queue[1:])]) or "No more songs in queue, add more to listen."

        Embed = discord.Embed(
            title="Current Queue",
            color= discord.Color.gold()
            )
        Embed.add_field(name="Now Playing", value=now_playing, inline=False)
        Embed.add_field(name="Next Up", value=upcoming, inline=False)
        await ctx.send(embed=Embed)

@bot.command() #Showing all the available song inside folder
async def playlist(ctx):
    Songs = [f for f in os.listdir(MusicLibrary) if f.endswith('.mp3')]
    if not Songs:
        await ctx.send("My Song library is empty at the moment")
        await ctx.send("Please retry again later")
        return
    
    song_list_text = "\n".join([f"{i+1}. {song}" for i,song in enumerate(Songs)])

    Embed = discord.Embed(
        title = "Available Song",
        description=song_list_text,
        color = discord.Color.blue()
    )
    await ctx.send(embed=Embed)

@bot.command() #Adding song to queue
async def queueadd(ctx, selection: int):
    global Queue
    Songs = [f for f in os.listdir(MusicLibrary) if f.endswith('.mp3')]
    if 0 < selection <= len(Songs):
        selected_song = Songs[selection - 1]
        Queue.append(selected_song)
        await ctx.send(f"Added **{selected_song}** to the queue!")
    else:
        await ctx.send(f"**Bruh**, Its not in my library, please pick a number, 1 to {len(Songs)}.")

@bot.command() #Start playing the song inside queue
async def play(ctx):
    if not ctx.voice_client:
        await ctx.send("Are you dumb or something??")
        await ctx.send("Invite me to one of your voice channel first")

    elif ctx.voice_client.is_playing():
        await ctx.send("I'm playing the song, Don't call me twice")    
    elif ctx.voice_client:
        if len(Queue) == 0:
            await ctx.send("Your Queue is empty bro...")
            await ctx.send("**Try add your song from my library using ph!playlist and ph!queueadd !!**")
        else:
            song_path = os.path.join(MusicLibrary, Queue[0])
            ctx.voice_client.play(discord.FFmpegPCMAudio(song_path), after=lambda e: play_next(ctx))
            await ctx.send(f"Now Playing: **{Queue[0]}**")

@bot.command() #Setting the repeat current
async def repeatcurrent(ctx):
    global is_repeating
    is_repeating = not is_repeating # Switch light
    status = "Enabled" if is_repeating else "Disabled"
    await ctx.send(f"Repeat Song mode is now **{status}**")

@bot.command() #Setting the repeat the queue
async def repeatqueue(ctx):
    global queue_repeat
    queue_repeat = not queue_repeat # Switch light
    status = "Enabled" if queue_repeat else "Disabled"
    await ctx.send(f"Repeat Queue mode is now **{status}**")

@bot.command() #skipping currently playing song
async def skip(ctx):
    global is_repeating
    if ctx.voice_client and ctx.voice_client.is_playing():
        if is_repeating:
            is_repeating = False
            await ctx.send("Repeat current is now Disabled, Re Enable if needed using ph!repeatcurrent")
        
        ctx.voice_client.stop()
        await ctx.send("Skipped current playing song")
    else:
        await ctx.send("i speak nothingh but emptiness... (Nothing is playing)")

#bot initialization
bot.run(TOKEN)