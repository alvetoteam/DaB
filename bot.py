import discord
from discord.ext import commands
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

API_URL = "https://ks-giftcode.centurygame.com/api/redeem"  # Adjust if needed

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {{bot.user}}")

@bot.command()
async def redeem(ctx, player_id: str, gift_code: str):
    """Redeem a Kingshot gift code for a player ID."""
    await ctx.send(f"🔄 Redeeming code `{{gift_code}}` for player `{{player_id}}`...")

    payload = {
        "playerId": player_id,
        "giftCode": gift_code
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=headers) as response:
            if response.status != 200:
                await ctx.send(f"❌ API error: {{response.status}}")
                return

            data = await response.json()
            if data.get("code") == 0:
                await ctx.send(f"✅ Success: {{data.get('message', 'Code redeemed.')}}")
            else:
                await ctx.send(f"⚠️ Failed: {{data.get('message', 'Unknown error')}}")

bot.run(TOKEN)
