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
intents.message_content = True # MUST BE ON IN DEVELOPER PORTAL
intents.members = True 

my_secret = os.getenv('TOKEN')
bot = commands.Bot(command_prefix="!", intents=intents)

# --- MEMORY LISTS ---
softbanned_users = set()
mocking_list = set()   

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ SUCCESS: {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s).")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Procraft 👀"))
    except Exception as e:
        print(f"❌ ERROR SYNCING: {e}")

# ==========================================
#      🕹️ CHAOS PANEL (Buttons)
# ==========================================

class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Uses the TRICK (response) so it always works
        await interaction.response.send_message("🚀 Spamming...", ephemeral=True)
        for i in range(5):
            await interaction.followup.send(f"Hello! 👋 (Message {i+1})", ephemeral=False)
            await asyncio.sleep(1)

    @discord.ui.button(label="PING EVERYONE (x5)", style=discord.ButtonStyle.red)
    async def ping_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Uses the TRICK
        await interaction.response.send_message("⚠️ NUKE LAUNCHED...", ephemeral=True)
        for i in range(5):
            await interaction.followup.send("@everyone", ephemeral=False)
            await asyncio.sleep(1)

@bot.tree.command(name="chaos", description="Open the Secret Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    await interaction.response.send_message("👇 **CHAOS CONTROL PANEL** 👇", view=ChaosView(), ephemeral=True)

# ==========================================
#      🤡 FAKE PROMOTION (UNBREAKABLE MODE)
# ==========================================

@bot.tree.command(name="promote", description="👮‍♂️ Promotes a user to Admin (FAKE).")
async def promote(interaction: discord.Interaction, member: discord.Member):
    official_emoji = "<:system:1468254317633994844>" 
    
    embed = discord.Embed(
        title=f"{official_emoji} System Notification", 
        description=f"**Server Update:** {member.mention} has been promoted to **Administrator**.\nThey now have full access to ban members.",
        color=0x5865F2 
    )
    
    # ⚡ THE TRICK: No channel.send! We use response!
    # Everyone sees "Procraft used /promote", but it guarantees the message sends.
    await interaction.response.send_message(embed=embed)
    
    await asyncio.sleep(5)
    
    # ⚡ TRICK AGAIN: Followup works everywhere
    await interaction.followup.send(f"🤡 Just kidding, {member.mention}. You are still a noob.")

# ==========================================
#      🚫 FAKE BAN (UNBREAKABLE MODE)
# ==========================================

@bot.tree.command(name="fakeban", description="🔨 Fake ban a user (Scare them!)")
async def fakeban(interaction: discord.Interaction, member: discord.Member):
    official_emoji = "<:system:1468254317633994844>" 
    
    embed = discord.Embed(
        title=f"{official_emoji} System Notification",
        description=f"🚫 **{member.mention} has been BANNED from the server.**\n\n**Reason:** Violation of Community Guidelines.\n**Action Taken:** Permanent Ban.",
        color=0xFF0000 
    )
    
    # ⚡ THE TRICK
    await interaction.response.send_message(embed=embed)
    
    await asyncio.sleep(4)
    await interaction.followup.send(f"🤡 Just kidding, {member.mention}. You are safe!")

# ==========================================
#      ☑️ FAKE VERIFIED BADGE
# ==========================================

@bot.tree.command(name="verified", description="☑️ Prove you are a verified bot (FAKE).")
async def verified(interaction: discord.Interaction):
    # Use a verified bot emoji here if you have one, or just the checkmark
    verified_emoji = "✅" 
    
    embed = discord.Embed(
        title=f"System Check {verified_emoji}",
        description="✅ **Karmabot Identity Confirmed.**\nThis bot is verified by Discord.",
        color=0x5865F2
    )
    # ⚡ THE TRICK
    await interaction.response.send_message(embed=embed)

# ==========================================
#      🎭 THE MIMIC (Requires Permission!)
#      Note: This is the ONLY one that needs specific permission (Webhooks)
# ==========================================

@bot.tree.command(name="mimic", description="🎭 Make the bot speak as someone else!")
async def mimic(interaction: discord.Interaction, member: discord.Member, message: str):
    # ⚡ TRICK: Confirmation message
    await interaction.response.send_message("🤐 **Stealing identity...**", ephemeral=True)

    try:
        # We MUST use a Webhook here (The trick doesn't create webhooks)
        webhook = await interaction.channel.create_webhook(name=member.display_name)
        await webhook.send(str(message), username=member.display_name, avatar_url=member.display_avatar.url)
        await webhook.delete()
    except:
        await interaction.followup.send("❌ I need 'Manage Webhooks' permission to do this!", ephemeral=True)

# ==========================================
#      🦜 SPONGEBOB MOCK (UNSTOPPABLE)
# ==========================================

@bot.tree.command(name="mock", description="🦜 Mock everything this user says for 5 minutes!")
async def mock(interaction: discord.Interaction, member: discord.Member):
    if member.id in mocking_list:
        mocking_list.remove(member.id)
        # ⚡ TRICK
        await interaction.response.send_message(f"✋ **Mercy!** Stopped mocking {member.name}.", ephemeral=True)
    else:
        mocking_list.add(member.id)
        # ⚡ TRICK
        await interaction.response.send_message(f"🦜 **ACTIVATED!** I will mock {member.name}.", ephemeral=True)
        await asyncio.sleep(300)
        if member.id in mocking_list:
            mocking_list.remove(member.id)

# THE LISTENER (Still needs permissions to delete, but wont crash)
@bot.event
async def on_message(message):
    if message.author == bot.user: return 

    if message.author.id in mocking_list:
        try:
            original = message.content
            if not original: return 
            mocked_text = "".join(random.choice((str.upper, str.lower))(c) for c in original)
            
            # Try to delete (Pass if fails)
            try: await message.delete()
            except: pass 

            # Send the mock
            await message.channel.send(f"{message.author.mention} sAyS: \"**{mocked_text}**\" 🤡")
        except: pass

    await bot.process_commands(message)

# ==========================================
#      🛑 SOFT BAN
# ==========================================

@bot.tree.command(name="softban", description="🚪 Kick them immediately every time they rejoin.")
@app_commands.checks.has_permissions(kick_members=True)
async def softban(interaction: discord.Interaction, member: discord.Member):
    softbanned_users.add(member.id)
    # ⚡ TRICK
    await interaction.response.send_message(f"😈 **{member.name} is now Soft Banned.**")
    try:
        await member.kick(reason="Soft Banned")
    except:
        await interaction.followup.send("❌ I couldn't kick them (Are they Admin?)", ephemeral=True)

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
        except: pass

@bot.tree.command(name="hello", description="Says hello to Procraft!")
async def hello(interaction: discord.Interaction):
    # ⚡ TRICK
    await interaction.response.send_message("Hello there! 👋 I am back online!")

# --- RUN THE BOT ---
keep_alive()
if my_secret:
    try:
        bot.run(my_secret)
    except Exception as e:
        print(f"❌ ERROR STARTING BOT: {e}")
