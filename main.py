import discord
import os
import asyncio
import random
from flask import Flask
from threading import Thread
from discord import app_commands
from discord.ext import commands

print("--- SYSTEM: SCRIPT STARTING ---") 

# --- WEBSITE SERVER (Keep Alive) ---
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
print("--- SYSTEM: LOADING INTENTS ---") 
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

# Check if Token exists
my_secret = os.getenv('TOKEN')
if my_secret is None:
    print("❌ CRITICAL ERROR: Token not found! Check Render Environment Variables.")
else:
    print("✅ SYSTEM: Token found. Attempting login...")

bot = commands.Bot(command_prefix="!", intents=intents)

# --- MEMORY LISTS ---
softbanned_users = set()
mocking_list = set()   

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ SUCCESS: {bot.user} is online and connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s) globally.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Procraft 👀"))
    except Exception as e:
        print(f"❌ ERROR SYNCING COMMANDS: {e}")

# ==========================================
#      🕹️ CHAOS PANEL (Buttons Logic)
#      (Must be defined BEFORE the command!)
# ==========================================

class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Buttons never expire

    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🚀 Spamming...", ephemeral=True)
        try:
            for i in range(5):
                await interaction.followup.send(f"Hello! 👋 (Message {i+1})", ephemeral=False)
                await asyncio.sleep(1)
        except Exception as e:
            await interaction.followup.send("❌ I can't talk here!", ephemeral=True)

    @discord.ui.button(label="PING EVERYONE (x5)", style=discord.ButtonStyle.red)
    async def ping_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ NUKE LAUNCHED...", ephemeral=True)
        try:
            for i in range(5):
                await interaction.followup.send("@everyone", ephemeral=False)
                await asyncio.sleep(1)
        except discord.Forbidden:
            await interaction.followup.send("❌ No permission!", ephemeral=True)

@bot.tree.command(name="chaos", description="Open the Secret Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    # This sends the menu with the buttons!
    await interaction.response.send_message("👇 **CHAOS CONTROL PANEL** 👇", view=ChaosView(), ephemeral=True)

# ==========================================
#      🤡 STEALTH FAKE PROMOTION
# ==========================================

@bot.tree.command(name="promote", description="👮‍♂️ Promotes a user to Admin (FAKE).")
async def promote(interaction: discord.Interaction, member: discord.Member):
    # 1. HIDE EVIDENCE: Reply only to YOU (Ephemeral)
    # Note: YOU will see "Procraft used /promote", but others will NOT.
    await interaction.response.send_message(f"🤫 **Prank launching against {member.name}...**", ephemeral=True)

    # 2. WAIT A SECOND
    await asyncio.sleep(1)

    # 3. SEND FAKE MESSAGE TO CHANNEL
    official_emoji = "<:system:1468254317633994844>" 
    
    embed = discord.Embed(
        title=f"{official_emoji} System Notification", 
        description=f"**Server Update:** {member.mention} has been promoted to **Administrator**.\nThey now have full access to ban members.",
        color=0x5865F2 
    )
    
    # Use channel.send so it looks like a real alert (not a command response)
    await interaction.channel.send(embed=embed)
    
    # 4. REVEAL
    await asyncio.sleep(5)
    await interaction.channel.send(f"🤡 Just kidding, {member.mention}. You are still a noob.")

# ==========================================
#      🦜 SPONGEBOB MOCK MODE
# ==========================================

@bot.tree.command(name="mock", description="🦜 Mock everything this user says for 5 minutes!")
async def mock(interaction: discord.Interaction, member: discord.Member):
    if member.id in mocking_list:
        mocking_list.remove(member.id)
        await interaction.response.send_message(f"✋ **Mercy!** Stopped mocking {member.name}.")
    else:
        mocking_list.add(member.id)
        await interaction.response.send_message(f"🦜 **ACTIVATED!** repeating everything {member.name} says.")
        
        await asyncio.sleep(300)
        if member.id in mocking_list:
            mocking_list.remove(member.id)

@bot.tree.command(name="unmock", description="😇 Force stop the mocking immediately.")
@app_commands.checks.has_permissions(administrator=True) 
async def unmock(interaction: discord.Interaction, member: discord.Member):
    if member.id in mocking_list:
        mocking_list.remove(member.id)
        await interaction.response.send_message(f"😇 **Saved.** {member.name} is free.")
    else:
        await interaction.response.send_message("❌ They aren't being mocked.", ephemeral=True)

@bot.tree.command(name="silence", description="🛑 STOP ALL MOCKING FOR EVERYONE.")
@app_commands.checks.has_permissions(administrator=True)
async def silence(interaction: discord.Interaction):
    mocking_list.clear()
    await interaction.response.send_message("🛑 **SILENCE!** I have stopped mocking everyone.")

# THE LISTENER (This deletes the messages)
@bot.event
async def on_message(message):
    if message.author == bot.user: return # Ignore self

    if message.author.id in mocking_list:
        try:
            original = message.content
            mocked_text = "".join(random.choice((str.upper, str.lower))(c) for c in original)
            await message.delete() # Delete original
            await message.channel.send(f"{message.author.mention} sAyS: \"**{mocked_text}**\" 🤡")
        except discord.Forbidden:
            print("❌ NEED PERMISSION: Go to Server Settings -> Roles -> Karmabot -> Turn ON 'Manage Messages'")
        except Exception as e:
            print(f"Mock Error: {e}")

    # CRITICAL: This allows other commands to run!
    await bot.process_commands(message)

# ==========================================
#      🛑 SOFT BAN & BASIC COMMANDS
# ==========================================

@bot.tree.command(name="softban", description="🚪 Kick them immediately every time they rejoin.")
@app_commands.checks.has_permissions(kick_members=True)
async def softban(interaction: discord.Interaction, member: discord.Member):
    softbanned_users.add(member.id)
    await interaction.response.send_message(f"😈 **{member.name} is now Soft Banned.**")
    try:
        await member.send("🚫 **Don't you try.**")
        await member.kick(reason="Soft Banned")
    except:
        pass 

@bot.tree.command(name="unsoftban", description="😇 Remove someone from the auto-kick list.")
@app_commands.checks.has_permissions(kick_members=True)
async def unsoftban(interaction: discord.Interaction, user_id: str):
    try:
        id_int = int(user_id)
        if id_int in softbanned_users:
            softbanned_users.remove(id_int)
            await interaction.response.send_message(f"😇 User {user_id} is free.")
        else:
            await interaction.response.send_message("❌ User not found.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Invalid ID.", ephemeral=True)

@bot.event
async def on_member_join(member):
    if member.id in softbanned_users:
        try:
            await member.send("🛑 **Don't you try.**")
            await member.kick(reason="Soft Ban Auto-Kick")
        except:
            pass

@bot.tree.command(name="hello", description="Says hello to Procraft!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! 👋 I am back online!")

@bot.tree.command(name="avatar", description="🖼️ Steal someone's profile picture (Privately!)")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title=f"🖼️ Stolen Avatar: {member.name}", color=member.color)
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Only you can see this. 🤫")
    await interaction.followup.send(embed=embed)

# --- RUN THE BOT ---
keep_alive()

if my_secret:
    try:
        bot.run(my_secret)
    except Exception as e:
        print(f"❌ ERROR STARTING BOT: {e}")
else:
    print("❌ ERROR: Cannot start bot. Token is missing.")
