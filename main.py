import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl  # Use yt-dlp instead of youtube-dl
import os

# Load the bot token from the .env file
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

# YouTube downloader options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Function to join voice channel
async def join_voice_channel(interaction: discord.Interaction):
    channel = interaction.user.voice.channel
    if not interaction.guild.voice_client:
        await channel.connect()
    await interaction.response.send_message(f"Joined {channel}!")

# Join command
@bot.tree.command(name="join", description="Join a voice channel")
async def join(interaction: discord.Interaction):
    await join_voice_channel(interaction)

# Leave command
@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("Disconnected from the voice channel.")
    else:
        await interaction.response.send_message("I'm not in a voice channel.")

# Play command
@bot.tree.command(name="play", description="Play a song from YouTube")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.guild.voice_client:
        await join_voice_channel(interaction)
    else:
        interaction.guild.voice_client.stop()

    with ytdl:
        info = ytdl.extract_info(url, download=False)
        url = info['url']

    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: print(f'Finished playing: {e}'))
    await interaction.response.send_message(f"Now playing: {info['title']}")

# Pause command
@bot.tree.command(name="pause", description="Pause the currently playing audio")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("Paused the audio.")
    else:
        await interaction.response.send_message("No audio is currently playing.")

# Resume command
@bot.tree.command(name="resume", description="Resume the paused audio")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("Resumed the audio.")
    else:
        await interaction.response.send_message("No audio is currently paused.")

# Mute command (requires Administrator)
@bot.tree.command(name="mute", description="Mute a member in a voice channel")
async def mute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.edit(mute=True)
    await interaction.response.send_message(f"Muted {member.mention}.")

# Unmute command (requires Administrator)
@bot.tree.command(name="unmute", description="Unmute a member in a voice channel")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.edit(mute=False)
    await interaction.response.send_message(f"Unmuted {member.mention}.")

# Move command (requires Administrator)
@bot.tree.command(name="move", description="Move a member to another voice channel")
async def move(interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await member.move_to(channel)
    await interaction.response.send_message(f"Moved {member.mention} to {channel.name}.")

# Syncing commands with Discord
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

# Run the bot
bot.run(TOKEN)
