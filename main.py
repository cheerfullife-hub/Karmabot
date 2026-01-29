import discord
import os
import asyncio
import random
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
intents.members = True # Needed to find members for unbanning
bot = commands.Bot(command_prefix="!", intents=intents)

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over the server 🛡️"))
    except Exception as e:
        print(e)

# ==========================================
#    🛡️ SECURITY & MODERATION COMMANDS 🛡️
# ==========================================

# --- 1. KICK COMMAND ---
@bot.tree.command(name="kick", description="🦵 Kick a member from the server.")
@app_commands.describe(member="The user to kick", reason="Why are you kicking them?")
@app_commands.checks.has_permissions(administrator=True) # Only Admins can use this
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"🦵 **{member.mention} has been kicked.**\n📝 Reason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick that user! (Is their role higher than mine?)", ephemeral=True)
    except Exception as e:
         await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# --- 2. BAN COMMAND ---
@bot.tree.command(name="ban", description="🔨 Ban a member from the server.")
@app_commands.describe(member="The user to ban", reason="Why are you banning them?")
@app_commands.checks.has_permissions(administrator=True) # Only Admins can use this
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        # Send them a DM before banning so they know why
        try:
            await member.send(f"🚫 You have been banned from **{interaction.guild.name}**.\n📝 Reason: {reason}")
        except:
            pass # If their DMs are closed, just continue

        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 **{member.mention} has been BANNED.**\n📝 Reason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban that user! (Is their role higher than mine?)", ephemeral=True)
    except Exception as e:
         await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# --- 3. UNBAN COMMAND ---
@bot.tree.command(name="unban", description="🤝 Unban a user using their ID.")
@app_commands.describe(user_id="The ID of the user to unban")
@app_commands.checks.has_permissions(administrator=True) # Only Admins can use this
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"🤝 **{user.mention} has been unbanned.**")
    except discord.NotFound:
        await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ Invalid User ID. Please provide a number.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# --- 4. USERINFO COMMAND ---
@bot.tree.command(name="userinfo", description="ℹ️ Get information about a user.")
@app_commands.describe(member="The user to get info on")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    roles = [role.mention for role in member.roles if role != interaction.guild.default_role] # Get their roles
    embed = discord.Embed(title=f"User Info: {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="🗓️ Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🎂 Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="🏷️ Roles", value=", ".join(roles) if roles else "None", inline=False)
    await interaction.response.send_message(embed=embed)


# ==========================================
#         🤡 FUN & CHAOS COMMANDS 🤡
# ==========================================

# --- FEATURE 1: THE MEGA REACTION NUKE ☢️ ---
@bot.tree.context_menu(name="💣 Reaction Nuke")
async def reaction_nuke(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message("☢️ LAUNCHING 15 WARHEADS...", ephemeral=True)
    emojis = [
        "🤡", "💩", "💀", "😹", "🍌", "🌭", "👻", "👀", "👺", "🍆",
        "🐔", "🦀", "🐛", "🌵", "🌚", "🧊", "🍅", "🍩", "🗿", "🧨",
        "🤢", "🤬", "🤖", "👽", "🙉", "🍄", "🧀", "🌭", "🦍", "🧦"
    ]
    selected_emojis = random.sample(emojis, 15)
    for emoji in selected_emojis:
        try:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.4) 
        except discord.Forbidden:
            await interaction.followup.send("❌ I hit a wall! (No permissions)", ephemeral=True)
            break
        except Exception as e:
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

# --- ERROR HANDLER (For Permission Checks) ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("⛔ **You don't have permission to use this command!** (You need Administrator)", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ An error occurred: {error}", ephemeral=True)

# --- RUN THE BOT ---
keep_alive()
bot.run(os.getenv('TOKEN'))
