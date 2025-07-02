import discord
from discord import app_commands
import aiohttp
import os
import time
import hashlib

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"✅ Bot is ready. Logged in as {self.user}")
        await self.tree.sync()
        print("✅ Slash commands synced.")

client = MyClient()

def generate_sign(fid, cdk, time_str, secret_key="YOUR_SECRET_KEY"):
    raw_str = f"fid={fid}&cdk={cdk}&time={time_str}&key={secret_key}"
    sign = hashlib.md5(raw_str.encode("utf-8")).hexdigest()
    return sign

@client.tree.command(name="redeem", description="Redeem a Kingshot gift code for a player ID")
@app_commands.describe(player_id="Your Kingshot Player ID", gift_code="The gift code to redeem")
async def redeem(interaction: discord.Interaction, player_id: str, gift_code: str):
    await interaction.response.defer(thinking=True)
    url = "https://kingshot-giftcode.centurygame.com/api/gift_code"
    
    current_time = str(int(time.time() * 1000))
    secret_key = "YOUR_SECRET_KEY"  # عدلها بالقيمة الحقيقية
    
    sign = generate_sign(player_id, gift_code, current_time, secret_key)
    
    payload = {
        "sign": sign,
        "fid": player_id,
        "cdk": gift_code,
        "captcha_code": "",
        "time": current_time
    }
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache, private",
        "User-Agent": "Mozilla/5.0",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                await interaction.followup.send(f"❌ API Error {resp.status}:\n```{text}```")
                return
            
            data = await resp.json()
            if data.get("code") == 0:
                await interaction.followup.send(f"✅ Success: {data.get('msg', 'Code redeemed!')}")
            else:
                await interaction.followup.send(f"❌ Failed: {data.get('msg', 'Unknown error')}")

if __name__ == "__main__":
    client.run(TOKEN)
