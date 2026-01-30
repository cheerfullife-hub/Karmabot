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
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Procraft 👀"))
    except Exception as e:
        print(e)

# ==========================================
#         👋 BASIC COMMANDS
# ==========================================

@bot.tree.command(name="hello", description="Says hello to Procraft!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! 👋 I am back online!")

# --- NEW: AVATAR STEALER (Slash Command) ---
@bot.tree.command(name="avatar", description="🖼️ Steal someone's profile picture in HD!")
@app_commands.describe(member="The victim to steal from")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    # Get the avatar URL (or default if they don't have one)
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    
    embed = discord.Embed(title=f"🖼️ Stolen Avatar: {member.name}", color=member.color)
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Stolen by {interaction.user.name} 🕵️‍♂️")
    
    await interaction.response.send_message(embed=embed)

# ==========================================
#    🖱️ RIGHT-CLICK MENUS (THE "APPS" LIST)
# ==========================================

# --- NEW: AVATAR STEALER (Right-Click Version) ---
@bot.tree.context_menu(name="🖼️ Steal Avatar")
async def avatar_ctx(interaction: discord.Interaction, member: discord.Member):
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    
    embed = discord.Embed(title=f"🖼️ Stolen Avatar: {member.name}", color=member.color)
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Stolen by {interaction.user.name} 🕵️‍♂️")
    
    await interaction.response.send_message(embed=embed)

# --- USER INFO ---
@bot.tree.context_menu(name="ℹ️ User Info")
async def user_info_ctx(interaction: discord.Interaction, member: discord.Member):
    roles = [role.mention for role in member.roles if role != interaction.guild.default_role]
    embed = discord.Embed(title=f"User Info: {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="🗓️ Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🏷️ Roles", value=", ".join(roles) if roles else "None", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KICK USER ---
@bot.tree.context_menu(name="🦵 Kick User")
@app_commands.checks.has_permissions(kick_members=True) 
async def kick_ctx(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.kick(reason="Kicked via Right-Click Menu")
        await interaction.response.send_message(f"🦵 **{member.mention} was kicked!**", ephemeral=False)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't kick them! (They might be the Boss/Admin)", ephemeral=True)

# --- BAN USER ---
@bot.tree.context_menu(name="🔨 Ban User")
@app_commands.checks.has_permissions(ban_members=True) 
async def ban_ctx(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.ban(reason="Banned via Right-Click Menu")
        await interaction.response.send_message(f"🔨 **{member.mention} was BANNED!**", ephemeral=False)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't ban them! (They might be the Boss/Admin)", ephemeral=True)

# --- REACTION NUKE ---
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
#         ⌨️ SLASH COMMANDS (TYPING)
# ==========================================

# --- UNBAN ---
@bot.tree.command(name="unban", description="🤝 Unban a user using their ID.")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"🤝 **{user.mention} has been unbanned.**")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed: {e}", ephemeral=True)

# --- CHAOS PANEL ---
class ChaosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spam Hello (x5)", style=discord.ButtonStyle.green)
    async def hello_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🚀 Launching Spam...", ephemeral=True)
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
            await interaction.followup.send("❌ I am not allowed to ping everyone here!", ephemeral=True)

@bot.tree.command(name="chaos", description="Open the Secret Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    await interaction.response.send_message("👇 Controls:", view=ChaosView(), ephemeral=True)

# --- ERROR HANDLER ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("⛔ You need Admin/Mod powers to do that!", ephemeral=True)
    else:
        print(f"Error: {error}")

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
