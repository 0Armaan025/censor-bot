import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)
load_dotenv()
token = os.getenv('token')

def contains_prohibited_word(message_content):
    with open('swears.txt', 'r') as file:
        prohibited_words = [word.strip().lower() for word in file]

    for word in prohibited_words:
        if word in message_content.lower():
            
            return True
    return False

async def muteUser(message, member: discord.Member, sendAdmin=False, reason=None, time=False):
    muted = discord.utils.get(message.guild.roles, name='muted')
    muted_channel_id = 1126792149405536318  # Replace with the correct muted channel ID

    if sendAdmin:
        target_user_ids = [993431339338575884]

        for target_user_id in target_user_ids:
            target_user = await client.fetch_user(target_user_id)
            await target_user.send(f"{member} was muted by {message.author} for {reason}")

        await member.send("You have been muted for saying swear/bad/inappropriate words. Please review the rules and contact a staff member for unmute.")

    if not muted:
        muted = await message.guild.create_role(name='muted', reason="To mute users")
        for channel in message.guild.channels:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.read_messages = False
            await channel.set_permissions(muted, overwrite=overwrite)

    if muted in member.roles:
        await message.channel.send(':x: This person is already muted.')
    else:
        await member.add_roles(muted, reason=reason)

        for channel in message.guild.channels:
            if channel.id == muted_channel_id:
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = True
                overwrite.read_messages = True
            else:
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = False
                overwrite.read_messages = False

            await channel.set_permissions(muted, overwrite=overwrite)

        await message.channel.send(f':white_check_mark: **User {member.mention} was muted!**')
        await member.send("You have been muted for saying swear/bad/inappropriate words. Please review the rules and contact a staff member for unmute.")

@client.event
async def on_ready():
    while True:
        await client.change_presence(activity=discord.Game('disallowing swearing 24/7'), status=discord.Status.do_not_disturb)
        print("The bot is ready")

@client.event
async def on_message(message):
    if not message.author.bot:
        if contains_prohibited_word(message.content):
            await message.delete()
            await muteUser(message, message.author, True, "swearing", False)
        else:
            await client.process_commands(message)

def download_prohibited_words():
    response = requests.get('https://raw.githubusercontent.com/mmguero/cleanvid/main/src/cleanvid/swears.txt')
    if response.status_code == 200:
        with open('swears.txt', 'w') as file:
            file.write(response.text)

# Download the prohibited words file before running the bot

client.run(token)
