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

    role = discord.utils.get(ctx.guild.roles, name="POLITI")
    if role:
        await ctx.send(f"———————{role.mention}——————— 🚨 En person venter på dig!")
    else:
        await ctx.send("❌ Kan ikke finde rollen **Politi**!")

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
        name="!commands",
        value="Viser denne oversigt over kommandoer.",
        inline=False
    )

    embed.set_footer(text="Bot lavet af dig 😎")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/99/Discord_logo.svg")

    await ctx.send(embed=embed)

# Test-kommando
@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

keep_alive()
bot.run(token)
