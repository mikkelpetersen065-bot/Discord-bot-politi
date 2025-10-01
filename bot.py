import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Hent token fra .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Opsæt intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Her definerer du hvilke roller der pings i hvilke kanaler
KANALER = {
    123456789012345678: {   # Kanal 1 ID
        "rolle_id": 111111111111111111,  # ID på Politi-rolle
        "besked": "🚨 en kolega har brug for hjælp!"
    },
    987654321098765432: {   # Kanal 2 ID
        "rolle_id": 222222222222222222,  # ID på Rigspoliti-rolle
        "besked": "en person afventer dig"
    }
}

@bot.event
async def on_ready():
    print(f"✅ Botten er logget ind som {bot.user}")

@bot.command()
async def tilkald(ctx):
    kanal_id = ctx.channel.id

    if kanal_id not in KANALER:
        await ctx.send("❌ Denne kanal har ikke et tilkald-svar sat.")
        return

    data = KANALER[kanal_id]
    rolle = ctx.guild.get_role(data["rolle_id"])

    if rolle:
        await ctx.send(f"{rolle.mention} — {data['besked']}")
    else:
        await ctx.send("❌ Kunne ikke finde rollen. Tjek at rolle-ID'et er korrekt.")

# Start bot med keep_alive
keep_alive()
bot.run(TOKEN)
