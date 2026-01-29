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

# --- FEATURE 1: THE MEGA REACTION NUKE ☢️ ---
@bot.tree.context_menu(name="💣 Reaction Nuke")
async def reaction_nuke(interaction: discord.Interaction, message: discord.Message):
    # 1. Hidden confirmation
    await interaction.response.send_message("☢️ LAUNCHING 15 WARHEADS...", ephemeral=True)
    
    # 2. HUGE Arsenal of Emojis
    emojis = [
        "🤡", "💩", "💀", "😹", "🍌", "🌭", "👻", "👀", "👺", "🍆",
        "🐔", "🦀", "🐛", "🌵", "🌚", "🧊", "🍅", "🍩", "🗿", "🧨",
        "🤢", "🤬", "🤖", "👽", "🙉", "🍄", "🧀", "🌭", "🦍", "🧦"
    ]
    
    # 3. Pick 15 unique random ones
    selected_emojis = random.sample(emojis, 15)
    
    for emoji in selected_emojis:
        try:
            await message.add_reaction(emoji)
            # We wait 0.4 seconds so Discord doesn't block us for spamming
            await asyncio.sleep(0.4) 
        except discord.Forbidden:
            await interaction.followup.send("❌ I hit a wall! (No permissions)", ephemeral=True)
            break
        except Exception as e:
            # If something else happens, just keep going!
            print(f"Failed to react: {e}")

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
