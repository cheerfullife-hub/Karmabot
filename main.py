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
    print(f"✅ {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Procraft 👀"))
    except Exception as e:
        print(e)

# --- THE CHAOS CONTROL PANEL ---
class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # BUTTON 1: Friendly Hello Spam
    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Private confirmation (Only you see this)
        await interaction.response.send_message("Launching Hello Spam! 🚀", ephemeral=True)
        # 2. Public Loop
        for i in range(5):
            await interaction.channel.send("Hello! 👋")
            await asyncio.sleep(1) 

    # BUTTON 2: The DANGEROUS Ping Spam
    @discord.ui.button(label="PING EVERYONE (x5)", style=discord.ButtonStyle.red)
    async def ping_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Private confirmation (Only you see this)
        await interaction.response.send_message("⚠️ NUKE LAUNCHED! ⚠️", ephemeral=True)
        # 2. Public Loop
        for i in range(5):
            await interaction.channel.send("@everyone")
            await asyncio.sleep(1)

# --- THE MAIN COMMAND ---
@bot.tree.command(name="chaos", description="Open the Secret Admin Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    # 'ephemeral=True' means ONLY YOU can see this menu!
    await interaction.response.send_message("👇 Choose your weapon:", view=ChaosView(), ephemeral=True)

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
