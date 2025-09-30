import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

from keep_alive import keep_alive

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

KANAL_FILE = "kanal_data.json"

# Load kanal-data fra fil
try:
    with open(KANAL_FILE, "r") as f:
        kanal_data = json.load(f)
except FileNotFoundError:
    kanal_data = {}

@bot.event
async def on_ready():
    print(f"✅ Botten er logget ind som {bot.user}")
    print(f"🔹 Prefix: {bot.command_prefix}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setkanal(ctx, kanal_type: str):
    kanal_type = kanal_type.lower()
    if kanal_type not in ["politi", "borger", "rigspolitiet"]:
        return await ctx.send("❌ Ugyldig type. Brug `politi`, `borger` eller `rigspolitiet`.")

    guild_id = str(ctx.guild.id)
    if guild_id not in kanal_data:
        kanal_data[guild_id] = {}

    kanal_data[guild_id][str(ctx.channel.id)] = {
        "rolle_id": None,
        "type": kanal_type
    }

    with open(KANAL_FILE, "w") as f:
        json.dump(kanal_data, f, indent=4)

    await ctx.send(f"✅ Denne kanal er nu sat op som `{kanal_type}` kanal. Brug !setrolle @rolle for at tilføje en rolle.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setrolle(ctx, rolle: discord.Role):
    guild_id = str(ctx.guild.id)
    kanal_id = str(ctx.channel.id)

    if guild_id not in kanal_data or kanal_id not in kanal_data[guild_id]:
        return await ctx.send("❌ Denne kanal er ikke sat op. Brug !setkanal først.")

    kanal_data[guild_id][kanal_id]["rolle_id"] = rolle.id

    with open(KANAL_FILE, "w") as f:
        json.dump(kanal_data, f, indent=4)

    await ctx.send(f"✅ Rollen {rolle.mention} er nu sat til denne kanal.")

@bot.command()
async def tilkald(ctx):
    guild_id = str(ctx.guild.id)
    kanal_id = str(ctx.channel.id)

    if guild_id not in kanal_data or kanal_id not in kanal_data[guild_id]:
        return await ctx.send("❌ Denne kanal er ikke sat op til !tilkald. Brug !setkanal først.")

    rolle_id = kanal_data[guild_id][kanal_id].get("rolle_id")
    kanal_type = kanal_data[guild_id][kanal_id].get("type")

    if not rolle_id:
        return await ctx.send("❌ Rollen er ikke sat op. Brug !setrolle @rolle.")

    role = ctx.guild.get_role(rolle_id)
    if not role:
        return await ctx.send("❌ Rollen findes ikke længere.")

    if kanal_type == "politi":
        await ctx.send(f"———————{role.mention}——————— 🚨 En kollega har brug for din hjælp!")
    elif kanal_type == "rigspolitiet":
        await ctx.send(f"———————{role.mention}——————— 🚨 En person venter på dig!")
    else:
        return await ctx.send("❌ Kanalen har ikke en gyldig type. Brug !setkanal for at konfigurere den korrekt.")

@bot.command()
async def command(ctx):
    embed = discord.Embed(title="📜 Kommandoer", description="Her er en liste over tilgængelige kommandoer", color=0x00ff00)
    embed.add_field(name="!setkanal <type>", value="Sætter kanalen som `politi`, `borger` eller `rigspolitiet`. Kun admins.", inline=False)
    embed.add_field(name="!setrolle @rolle", value="Sætter rollen til kanalen. Kun admins.", inline=False)
    embed.add_field(name="!tilkald", value="Tilkalder den opsatte rolle i kanalen.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

keep_alive()
bot.run(token)
