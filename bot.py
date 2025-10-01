import discord
from discord.ext import commands
import os
import json
import requests
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

print (OWNER_ID)

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
    guild_id = str(ctx.guild.id)
    kanal_data = kanaler.get(guild_id, {})

    if kanal_data.get("kanal_id") != str(ctx.channel.id):
        await ctx.send("❌ Denne kommando kan kun bruges i den kanal, der er sat med !setkanal.")
        return

    role_id = kanal_data.get("rolle_id")
    if not role_id:
        await ctx.send("❌ Ingen rolle er sat for denne kanal. Brug !setrolle først.")
        return

    role = ctx.guild.get_role(int(role_id))
    if role:
        await ctx.send(f"———————{role.mention}——————— 🚨 En person venter på dig!")
    else:
        await ctx.send("❌ Kunne ikke finde rollen, der er sat for denne kanal.")

# Kommando: setkanal (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setkanal(ctx):
    kanaler = load_kanaler()
    guild_id = str(ctx.guild.id)

    if guild_id not in kanaler:
        kanaler[guild_id] = {}

    kanaler[guild_id]["kanal_id"] = str(ctx.channel.id)
    save_kanaler(kanaler)
    await ctx.send("✅ Denne kanal er nu sat som tilkald-kanal.")

@setkanal.error
async def setkanal_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")

# Kommando: setrolle (kun admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def setrolle(ctx, *, rolle_navn: str):
    role = discord.utils.get(ctx.guild.roles, name=rolle_navn)
    if not role:
        await ctx.send(f"❌ Kunne ikke finde rollen med navnet: **{rolle_navn}**")
        return

    kanaler = load_kanaler()
    guild_id = str(ctx.guild.id)

    if guild_id not in kanaler:
        kanaler[guild_id] = {}

    kanaler[guild_id]["rolle_id"] = str(role.id)
    save_kanaler(kanaler)
    await ctx.send(f"✅ Rollen **{rolle_navn}** er nu sat som tilkald-rolle for denne server.")

@setrolle.error
async def setrolle_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")

# Kommando: commands (pæn embed)
@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title="📜 Bot Kommandoer",
        description="Her er en oversigt over kommandoer og hvordan du bruger dem:",
        color=discord.Color.green()
    )

    embed.add_field(
        name="!tilkald",
        value="Tilkalder den rolle, der er sat for kanalen.\nEksempel: `!tilkald`",
        inline=False
    )
    embed.add_field(
        name="!setkanal",
        value="Sætter den kanal, hvor `!tilkald` kan bruges.\nKun admin kan bruge denne.\nEksempel: `!setkanal` i den ønskede kanal.",
        inline=False
    )
    embed.add_field(
        name="!setrolle <rollenavn>",
        value="Sætter den rolle, som nævnes ved `!tilkald`.\nKun admin kan bruge denne.\nEksempel: `!setrolle Politi`",
        inline=False
    )
    embed.add_field(
        name="!commands",
        value="Viser denne oversigt.",
        inline=False
    )
    embed.add_field(
        name="!minip",
        value="Sender VPS'ens offentlige IP til dig i en privat besked.\nKun ejeren kan bruge denne.",
        inline=False
    )
    embed.add_field(
        name="!test",
        value="Tjekker at botten svarer korrekt.",
        inline=False
    )

    embed.set_footer(text="Bot lavet af dig 😎")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/99/Discord_logo.svg")

    await ctx.send(embed=embed)

# Kommando: test
@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

# Kommando: minip (kun ejer)
@bot.command()
async def minip(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Du har ikke tilladelse til at bruge denne kommando.")
        return

    try:
        ip = requests.get("https://ifconfig.me").text
        await ctx.author.send(f"🌍 VPS Public IP: `{ip}`")
        await ctx.send("✅ IP'en er sendt til dig i en privat besked.")
    except Exception as e:
        await ctx.send(f"❌ Kunne ikke hente IP: {e}")

keep_alive()
bot.run(token)
