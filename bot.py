import discord
from discord.ext import commands
import os
import json
import requests
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

KANAL_FIL = "kanaler.json"

# Opret JSON fil hvis den ikke findes
if not os.path.exists(KANAL_FIL):
    with open(KANAL_FIL, "w") as f:
        json.dump({}, f)

# Indlæs kanal-data
def load_kanaler():
    with open(KANAL_FIL, "r") as f:
        return json.load(f)

# Gem kanal-data
def save_kanaler(data):
    with open(KANAL_FIL, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Botten er logget ind som {bot.user}")
    print(f"🔹 Prefix: {bot.command_prefix}")

# Kommando: tilkald
@bot.command()
async def tilkald(ctx):
    kanaler = load_kanaler()
    kanal_id = kanaler.get(str(ctx.guild.id))

    if kanal_id != str(ctx.channel.id):
        await ctx.send("❌ Denne kommando kan kun bruges i den kanal, der er sat med !setkanal.")
        return

    role_name = kanaler.get(f"{ctx.guild.id}_rolle", "POLITI")
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role:
        await ctx.send(f"———————{role.mention}——————— 🚨 En person venter på dig!")
    else:
        await ctx.send(f"❌ Kan ikke finde rollen **{role_name}**!")

# Kommando: setkanal (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setkanal(ctx):
    kanaler = load_kanaler()
    kanaler[str(ctx.guild.id)] = str(ctx.channel.id)
    save_kanaler(kanaler)
    await ctx.send("✅ Denne kanal er nu sat som tilkald-kanal.")

@setkanal.error
async def setkanal_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")

# Kommando: setrolle (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setrolle(ctx, rolle_navn):
    kanaler = load_kanaler()
    kanaler[f"{ctx.guild.id}_rolle"] = rolle_navn
    save_kanaler(kanaler)
    await ctx.send(f"✅ Rollen er nu sat til **{rolle_navn}** for denne server.")

@setrolle.error
async def setrolle_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")

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
        name="!setrolle <rolenavn>",
        value="Sætter rollen der tilkaldes i den kanal.\nKun admin-brugere kan bruge denne.\nEksempel: `!setrolle Rigspolitiet`",
        inline=False
    )
    embed.add_field(
        name="!minip",
        value="Sender botens VPS’ offentlige IP privat til ejeren.\nKun ejeren kan bruge denne.",
        inline=False
    )
    embed.add_field(
        name="!commands",
        value="Viser denne oversigt over kommandoer.",
        inline=False
    )

    embed.set_footer(text="Bot lavet af dig 😎")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/99/Discord_logo.svg")

    await ctx.send(embed=embed)

# Kommando: minip (kun ejer)
@bot.command()
async def minip(ctx):
    ejer_id = 820010231400103956  # <-- SKIFT dette til dit Discord-bruger-ID
    if ctx.author.id != ejer_id:
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")
        return
    try:
        offentlig_ip = requests.get("https://api.ipify.org").text
        await ctx.author.send(f"Min VPS’ offentlige IP er: `{offentlig_ip}`")
        await ctx.send("✅ IP’en er sendt til dig i en privat besked 📩")
    except Exception as e:
        await ctx.send(f"❌ Fejl ved hentning af IP: {e}")

# Test-kommando
@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

keep_alive()
bot.run(token)
