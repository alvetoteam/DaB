import discord
from discord import app_commands
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")

# Configure intents
intents = discord.Intents.default()
intents.message_content = True  # needed only if you want to support reading message content too

# Create bot client
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"✅ Bot is ready. Logged in as {self.user}")
        await self.tree.sync()
        print("✅ Slash commands synced.")

client = MyClient()

# Define slash command
@client.tree.command(name="redeem", description="Redeem a Kingshot gift code for a player ID")
@app_commands.describe(player_id="Your Kingshot Player ID", gift_code="The gift code to redeem")
async def redeem(interaction: discord.Interaction, player_id: str, gift_code: str):
    await interaction.response.defer(thinking=True)
    API_URL = "https://ks-giftcode.centurygame.com/api/redeem"

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
                await interaction.followup.send(f"❌ API error: {response.status}")
                return

            data = await response.json()
            if data.get("code") == 0:
                await interaction.followup.send(f"✅ Success: {data.get('message', 'Code redeemed!')}")
            else:
                await interaction.followup.send(f"⚠️ Failed: {data.get('message', 'Unknown error')}")

client.run(TOKEN)
