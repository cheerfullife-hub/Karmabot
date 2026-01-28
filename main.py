import discord
import os
import asyncio
from flask import Flask
from threading import Thread
from discord import app_commands
from discord.ext import commands

# --- WEBSITE SERVER (For UptimeRobot) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        await bot.change_presence(activity=discord.Game(name="Spamming Pings 🔔"))
    except Exception as e:
        print(e)

# --- COMMAND 1: HELLO ---
@bot.tree.command(name="hello", description="Says hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! 👋 I am your new bot!")

# --- COMMAND 2: THE FIXED BUTTON ---
class SimpleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # This keeps the button alive!

    @discord.ui.button(label="spam 5 times", style=discord.ButtonStyle.green)
    async def my_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✨ IT WORKS! ✨", ephemeral=True)

@bot.tree.command(name="spam", description="Spam 5 times")
async def write(interaction: discord.Interaction):
    await interaction.response.send_message("Click below:", view=SimpleView(), ephemeral=True)

# --- COMMAND 3: THE CHAOS ANNOUNCER ---
@bot.tree.command(name="pingspam", description="Ping EVERYONE 5 times! 🔔")
async def announce(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"📢 **STARTING!** 📢\nMessage: {message}")
    for i in range(5):
        await interaction.channel.send(f"@everyone 🔔 {message}")
        await asyncio.sleep(1)

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
