import discord
import os
import asyncio
from flask import Flask
from threading import Thread
from discord import app_commands
from discord.ext import commands

# --- WEBSITE SERVER ---
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
        # This syncs the commands to ALL servers (Global Sync)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Procraft 👀"))
    except Exception as e:
        print(e)

# --- THE CHAOS CONTROL PANEL ---
class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # BUTTON 1: Friendly Hello Spam (Works everywhere if perms allow)
    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Private confirmation
        await interaction.response.send_message("🚀 Attempting Hello Spam...", ephemeral=True)
        
        # 2. Public Loop with Error Handling
        try:
            for i in range(5):
                await interaction.channel.send("Hello! 👋")
                await asyncio.sleep(1)
        except discord.Forbidden:
            # If the bot is not allowed to speak in this channel:
            await interaction.followup.send("❌ I don't have permission to talk in this channel!", ephemeral=True)

    # BUTTON 2: The DANGEROUS Ping Spam (Fails gracefully if no perms)
    @discord.ui.button(label="PING EVERYONE (x5)", style=discord.ButtonStyle.red)
    async def ping_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Private confirmation
        await interaction.response.send_message("⚠️ Launching Nuke...", ephemeral=True)
        
        # 2. Public Loop with Error Handling
        try:
            for i in range(5):
                await interaction.channel.send("@everyone")
                await asyncio.sleep(1)
        except discord.Forbidden:
            # If the bot can't ping everyone:
            await interaction.followup.send("❌ I am not allowed to ping everyone here! (Missing Permissions)", ephemeral=True)

# --- THE MAIN COMMAND ---
@bot.tree.command(name="chaos", description="Open the Secret Admin Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    await interaction.response.send_message("👇 Choose your weapon:", view=ChaosView(), ephemeral=True)

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
