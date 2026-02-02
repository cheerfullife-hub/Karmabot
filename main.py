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

# --- MEMORY LISTS (The Brains) ---
softbanned_users = set()
mocking_list = set()   # <--- THIS IS CRITICAL FOR MOCKING TO WORK!

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
#      🦜 SPONGEBOB MOCK MODE
# ==========================================

@bot.tree.command(name="mock", description="🦜 Mock everything this user says for 5 minutes!")
async def mock(interaction: discord.Interaction, member: discord.Member):
    # Toggle: On/Off
    if member.id in mocking_list:
        mocking_list.remove(member.id)
        await interaction.response.send_message(f"✋ **Mercy!** Stopped mocking {member.name}.")
    else:
        mocking_list.add(member.id)
        await interaction.response.send_message(f"🦜 **ACTIVATED!** repeating everything {member.name} says.")
        
        # Auto-stop after 5 minutes
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
            # Random Caps Logic
            mocked_text = "".join(random.choice((str.upper, str.lower))(c) for c in original)
            await message.delete() # Delete original
            await message.channel.send(f"{message.author.mention} sAyS: \"**{mocked_text}**\" 🤡")
        except:
            pass # If we can't delete, just ignore it

    # CRITICAL: This allows other commands to run!
    await bot.process_commands(message)

# ==========================================
#      🛑 THE "SOFT BAN" TRAP
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

# ==========================================
#      🔫 RUSSIAN ROULETTE (LOBBY SYSTEM)
# ==========================================

class RouletteLobby(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=300)
        self.host = host
        self.players = [host]
        self.npcs = []

    def update_embed(self):
        player_names = [p.name for p in self.players] + [f"🤖 {name}" for name in self.npcs]
        embed = discord.Embed(title="🔫 Russian Roulette Lobby", color=discord.Color.red())
        embed.description = "The gun has **1 Bullet**.\nLast one standing wins. Loser gets KICKED."
        embed.add_field(name=f"👥 Players ({len(player_names)})", value="\n".join(player_names), inline=False)
        embed.set_footer(text=f"Host: {self.host.name} | Click 'Start' when ready!")
        return embed

    @discord.ui.button(label="✋ Join Game", style=discord.ButtonStyle.blurple)
    async def join_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("You are already in!", ephemeral=True)
            return
        self.players.append(interaction.user)
        await interaction.response.edit_message(embed=self.update_embed(), view=self)

    @discord.ui.button(label="🤖 Add NPC", style=discord.ButtonStyle.gray)
    async def add_npc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Only Host can add bots!", ephemeral=True)
            return
        new_bot = random.choice(["Terminator", "Wall-E", "R2-D2", "Siri", "Alexa", "Steve"])
        self.npcs.append(new_bot)
        await interaction.response.edit_message(embed=self.update_embed(), view=self)

    @discord.ui.button(label="🔥 START", style=discord.ButtonStyle.red)
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host: return
        all_participants = self.players + [{"name": f"🤖 {name}", "is_npc": True} for name in self.npcs]
        
        if len(all_participants) < 2:
            await interaction.response.send_message("❌ Need at least 2 players!", ephemeral=True)
            return

        for child in self.children: child.disabled = True
        await interaction.response.edit_message(content="**🎲 LOADING REVOLVER...**", view=self)
        
        chamber = [0, 0, 0, 0, 0, 1]
        random.shuffle(chamber)
        bullet_index = 0
        while True:
            for person in all_participants:
                is_npc = isinstance(person, dict)
                name = person['name'] if is_npc else person.mention
                
                await interaction.channel.send(f"😰 {name} picks up the gun...")
                await asyncio.sleep(2)
                
                if chamber[bullet_index] == 1:
                    await interaction.channel.send(f"💥 **BANG!** {name} dropped dead!")
                    if not is_npc:
                        try:
                            await person.kick(reason="Lost Roulette")
                            await interaction.channel.send("👢 **KICKED!**")
                        except:
                            await interaction.channel.send("❌ (Too powerful to kick!)")
                    return 
                else:
                    await interaction.channel.send("😅 **CLICK.** Safe.")
                    await asyncio.sleep(1)
                
                bullet_index += 1
                if bullet_index >= 6: bullet_index = 0

@bot.tree.command(name="roulette", description="🔫 Start a game of Russian Roulette")
async def roulette(interaction: discord.Interaction):
    view = RouletteLobby(host=interaction.user)
    await interaction.response.send_message(embed=view.update_embed(), view=view)

# ==========================================
#         👋 BASIC COMMANDS
# ==========================================

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

@bot.tree.command(name="chaos", description="Open the Secret Panel 👮‍♂️")
async def chaos(interaction: discord.Interaction):
    await interaction.response.send_message("👇 Controls:", ephemeral=True)

# --- RUN THE BOT ---
keep_alive()

if my_secret:
    try:
        bot.run(my_secret)
    except Exception as e:
        print(f"❌ ERROR STARTING BOT: {e}")
else:
    print("❌ ERROR: Cannot start bot. Token is missing.")
