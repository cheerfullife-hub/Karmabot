import discord
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
from discord import app_commands
from discord.ext import commands

# 1. Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. Startup Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
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
        # Acknowledgement (hidden)
        await interaction.response.send_message("Here we go! 🚀", ephemeral=True)
        
        # NOTE: The bot will still post the "Hello!" messages publicly in the channel
        # so everyone can see the result, but only YOU saw the button.
        for i in range(5):
            await interaction.channel.send("Hello!")

@bot.tree.command(name="write", description="Spawns a magical button (Only for you!)")
async def write(interaction: discord.Interaction):
    # 👇 I added 'ephemeral=True' here! This makes the message private.
    await interaction.response.send_message("Click the button below to start!", view=SpamView(), ephemeral=True)

# 4. The Key
# 👇 PASTE YOUR TOKEN BELOW 👇
keep_alive()
bot.run(os.getenv('TOKEN'))