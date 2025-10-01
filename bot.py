import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "kanal_rolle_data.json"

# Opret JSON-fil hvis den ikke findes
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f, indent=4)

# Funktion: Load data
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Funktion: Save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Botten er logget ind som {bot.user}")
    print(f"🔹 Prefix: {bot.command_prefix}")

# Kommando: tilkald
@bot.command()
async def tilkald(ctx):
    data = load_data()
    guild_id = str(ctx.guild.id)
    kanal_id = str(ctx.channel.id)

    if guild_id not in data or kanal_id not in data[guild_id]:
        await ctx.send("❌ Denne kanal er ikke sat op til tilkald.")
        return

    role_name = data[guild_id][kanal_id]
    if role_name is None:
        await ctx.send("❌ Der er ikke sat en rolle for denne kanal. Brug `!setrolle @rolle`.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.send(f"———————{role.mention}——————— 🚨 Der er brug for assistance!")
    else:
        await ctx.send(f"❌ Kan ikke finde rollen **{role_name}**!")

# Kommando: setkanal (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setkanal(ctx):
    data = load_data()
    guild_id = str(ctx.guild.id)
    kanal_id = str(ctx.channel.id)

    if guild_id not in data:
        data[guild_id] = {}

    data[guild_id][kanal_id] = None
    save_data(data)
    await ctx.send(f"✅ Denne kanal er nu sat som tilkald-kanal. Brug `!setrolle @rolle` for at vælge rolle.")

@setkanal.error
async def setkanal_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")

# Kommando: setrolle (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setrolle(ctx, role: discord.Role):
    data = load_data()
    guild_id = str(ctx.guild.id)
    kanal_id = str(ctx.channel.id)

    if guild_id not in data or kanal_id not in data[guild_id]:
        await ctx.send("❌ Denne kanal er ikke sat som tilkald-kanal. Brug først `!setkanal`.")
        return

    data[guild_id][kanal_id] = role.name
    save_data(data)
    await ctx.send(f"✅ Rollen **{role.name}** er nu sat for denne kanal.")

@setrolle.error
async def setrolle_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Kunne ikke finde rollen. Brug format: `!setrolle @rolle`.")

# Kommando: commands (pæn embed)
@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title="📜 Bot Kommandoer",
        description="Her er en oversigt over bot kommandoer og hvordan du bruger dem:",
        color=discord.Color.green()
    )

    embed.add_field(
        name="!tilkald",
        value="Tilkalder den rolle, der er sat op for kanalen.\nEksempel: `!tilkald`",
        inline=False
    )
    embed.add_field(
        name="!setkanal",
        value="Sætter den kanal, hvor !tilkald kan bruges.\nKun admin-brugere kan bruge denne.\nEksempel: `!setkanal` i ønsket kanal",
        inline=False
    )
    embed.add_field(
        name="!setrolle @rolle",
        value="Vælger hvilken rolle, der skal kaldes i den kanal.\nKun admin-brugere kan bruge denne.\nEksempel: `!setrolle @Politi`",
        inline=False
    )
    embed.add_field(
        name="!commands",
        value="Viser denne oversigt over kommandoer.",
        inline=False
    )

    embed.set_footer(text="Ligma")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/99/Discord_logo.svg")

    await ctx.send(embed=embed)

# Test-kommando
@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

keep_alive()
bot.run(token)
