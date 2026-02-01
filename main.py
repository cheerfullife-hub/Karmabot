import discord
import os
import asyncio
import random
from flask import Flask
from threading import Thread
from discord import app_commands
from discord.ext import commands

print("--- SYSTEM: SCRIPT STARTING ---") # Debug 1

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
print("--- SYSTEM: LOADING INTENTS ---") # Debug 2
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

# --- MEMORY LIST (Soft Ban) ---
softbanned_users = set()

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
#      🛑 THE "SOFT BAN" TRAP
# ==========================================

@bot.tree.command(name="softban", description="🚪 Kick them immediately every time they rejoin.")
@app_commands.checks.has_permissions(kick_members=True)
async def softban(interaction: discord.Interaction, member: discord.Member):
    softbanned_users.add(member.id)
    await interaction.response.send_message(f"😈 **{member.name} is now Soft Banned.**\nIf they rejoin, I will kick them instantly.")
    try:
        await member.send("🚫 **Don't you try.** (You are soft-banned).")
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
            await interaction.response.send_message("❌ User not found in list.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ Invalid ID.", ephemeral=True)

@bot.event
async def on_member_join(member):
    if member.id in softbanned_users:
        try:
            await member.send("🛑 **Don't you try.**")
            await member.kick(reason="Soft Ban Auto-Kick")
            print(f"👢 Auto-kicked {member.name}")
        except Exception as e:
            print(f"Failed to auto-kick: {e}")

# ==========================================
#         👋 BASIC COMMANDS
# ==========================================

@bot.tree.command(name="hello", description="Says hello to Procraft!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! 👋 I am back online!")

@bot.tree.command(name="avatar", description="🖼️ Steal someone's profile picture!")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed = discord.Embed(title=f"🖼️ Stolen Avatar: {member.name}", color=member.color)
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

# ==========================================
#    🖱️ RIGHT-CLICK MENUS
# ==========================================

@bot.tree.command(name="avatar", description="🖼️ Steal someone's profile picture!")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    # 1. FREEZE TIME 🧊 (Tells Discord to wait)
    await interaction.response.defer()

    try:
        # 2. Get the avatar safely (Handles missing avatars automatically)
        avatar_url = member.display_avatar.url 
        
        # 3. Create the Embed
        embed = discord.Embed(title=f"🖼️ Stolen Avatar: {member.name}", color=member.color)
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Stolen by {interaction.user.name} 🕵️‍♂️")

        # 4. Send the message (We use 'followup' because we deferred earlier)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        # If it fails, print the error to the chat so we know why!
        await interaction.followup.send(f"❌ Error fetching avatar: {e}")
        print(f"❌ AVATAR ERROR: {e}")

@bot.tree.context_menu(name="ℹ️ User Info")
async def user_info_ctx(interaction: discord.Interaction, member: discord.Member):
    roles = [role.mention for role in member.roles if role != interaction.guild.default_role]
    embed = discord.Embed(title=f"User Info: {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="🗓️ Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🏷️ Roles", value=", ".join(roles) if roles else "None", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.context_menu(name="🦵 Kick User")
@app_commands.checks.has_permissions(kick_members=True) 
async def kick_ctx(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.kick(reason="Kicked via Right-Click Menu")
        await interaction.response.send_message(f"🦵 **{member.mention} was kicked!**", ephemeral=False)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't kick them!", ephemeral=True)

@bot.tree.context_menu(name="🔨 Ban User")
@app_commands.checks.has_permissions(ban_members=True) 
async def ban_ctx(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.ban(reason="Banned via Right-Click Menu")
        await interaction.response.send_message(f"🔨 **{member.mention} was BANNED!**", ephemeral=False)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't ban them!", ephemeral=True)

@bot.tree.context_menu(name="💣 Reaction Nuke")
async def reaction_nuke(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message("☢️ LAUNCHING WARHEADS...", ephemeral=True)
    emojis = ["🤡", "💩", "💀", "😹", "🍌", "🌭", "👻", "👀", "👺", "🍆", "🐔", "🦀", "🤖", "👽", "🧨"]
    selected_emojis = random.sample(emojis, 10) 
    for emoji in selected_emojis:
        try:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.4) 
        except discord.Forbidden:
            await interaction.followup.send("❌ Can't react here!", ephemeral=True)
            break

# ==========================================
#         ⌨️ OTHER COMMANDS
# ==========================================

@bot.tree.command(name="unban", description="🤝 Unban a user using their ID.")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"🤝 **{user.mention} has been unbanned.**")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed: {e}", ephemeral=True)

class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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
    await interaction.response.send_message("👇 Controls:", view=ChaosView(), ephemeral=True)

# --- RUN THE BOT ---
keep_alive()

# Check Token and Run
if my_secret:
    try:
        bot.run(my_secret)
    except discord.errors.LoginFailure:
        print("❌ ERROR: The Token is invalid! Reset it in Discord Developer Portal.")
    except Exception as e:
        print(f"❌ ERROR STARTING BOT: {e}")
else:
    print("❌ ERROR: Cannot start bot. Token is missing.")
