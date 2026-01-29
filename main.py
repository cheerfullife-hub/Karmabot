import discord
import os
import asyncio
import random
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
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for victims... 💣"))
    except Exception as e:
        print(e)

# --- FEATURE 1: THE REACTION NUKE (Context Menu) ---
# This creates the "Right-Click" command!
@bot.tree.context_menu(name="💣 Reaction Nuke")
async def reaction_nuke(interaction: discord.Interaction, message: discord.Message):
    # 1. Tell you it's working (Hidden)
    await interaction.response.send_message("🚀 Launching Emoji Nuke...", ephemeral=True)
    
    # 2. List of funny emojis
    emojis = ["🤡", "💩", "💀", "😹", "🍌", "🌭", "👻", "👀", "👺", "🍆"]
    
    # 3. Pick 5 random ones and blast them!
    selected_emojis = random.sample(emojis, 5)
    
    for emoji in selected_emojis:
        try:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.5) # Fast but safe speed
        except discord.Forbidden:
            await interaction.followup.send("❌ I can't react here! (No permissions)", ephemeral=True)
            break

# --- FEATURE 2: THE CHAOS CONTROL PANEL ---
class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🚀 Attempting Hello Spam...", ephemeral=True)
        try:
            for i in range(5):
                await interaction.channel.send("Hello! 👋")
                await asyncio.sleep(1)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to talk here!", ephemeral=True)

    @discord.ui.button(label="PING EVERYONE (x5)", style=discord.ButtonStyle.red)
    async def ping_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Launching Nuke...", ephemeral=True)
        try:
            for i in range(5):
                await interaction.channel.send("@everyone")
                await asyncio.sleep(1)
        except discord.Forbidden:
            await interaction.followup.send("❌ I am not allowed to ping everyone here!", ephemeral=True)

@bot.tree.command(name="chaos", description="Open the Secret Admin Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    await interaction.response.send_message("👇 Choose your weapon:", view=ChaosView(), ephemeral=True)

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
