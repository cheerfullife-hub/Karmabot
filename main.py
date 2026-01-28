import discord
import os
import asyncio  # <--- NEW: Needed for the sleep timer!
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
# We usually turn this on to be safe, even if we just use slash commands
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        # Let's change the status to look cool
        await bot.change_presence(activity=discord.Game(name="Annoying Everyone 🔔"))
    except Exception as e:
        print(e)

# --- COMMAND 1: HELLO ---
@bot.tree.command(name="hello", description="Says hello to Procraft!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! 👋 I am your new bot!")

# --- COMMAND 2: THE SECRET BUTTON ---
class SpamView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Write", style=discord.ButtonStyle.green)
    async def write_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Here we go! 🚀", ephemeral=True)
        for i in range(5):
            await interaction.channel.send("Hello!")

@bot.tree.command(name="write", description="Spawns a magical button (Only for you!)")
async def write(interaction: discord.Interaction):
    await interaction.response.send_message("Click the button below to start!", view=SpamView(), ephemeral=True)

# --- COMMAND 3: THE CHAOS ANNOUNCER (NEW!) ---
@bot.tree.command(name="announce", description="Ping EVERYONE 5 times! 🔔")
async def announce(interaction: discord.Interaction, message: str):
    # 1. Reply to you first so the bot doesn't crash
    await interaction.response.send_message(f"📢 **ANNOUNCEMENT STARTING!** 📢\nMessage: {message}")
    
    # 2. Loop 5 times
    for i in range(5):
        await interaction.channel.send(f"@everyone 🔔 {message}")
        await asyncio.sleep(1) # Wait 1 second between pings

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
