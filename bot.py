import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from keep_alive import keep_alive


load_dotenv()  # Læs .env filen
token = os.getenv("DISCORD_TOKEN")

# Intents (skal også være slået til i Developer Portal → "Message Content Intent")
intents = discord.Intents.default()
intents.message_content = True

# Prefix = ! (så man kan skrive fx !tilkald)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Botten er logget ind som {bot.user}")

@bot.command()
async def tilkald(ctx):
    role = discord.utils.get(ctx.guild.roles, name="POLITI")
    if role:
        await ctx.send(f"🚨 En kollega har brug for din hjælp, {role.mention}!")
    else:
        await ctx.send("❌ Kan ikke finde rollen **Politi**! Tjek om den findes.")

@bot.command()
async def test(ctx):
    await ctx.send("Botten virker! 🚀")

keep_alive()

# Til sidst: start botten
bot.run(token)
