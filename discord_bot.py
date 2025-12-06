import os
import discord
import requests
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "blurnsy/amc-showtimes"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="showtimes", description="Fetch AMC NorthPark 15 showtimes")
async def showtimes(interaction: discord.Interaction):
    await interaction.response.send_message("🎬 Fetching showtimes... (takes ~30 seconds)")
    
    response = requests.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/dispatches",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={"event_type": "amc-showtimes"}
    )
    
    if response.status_code == 204:
        await interaction.followup.send("✅ Scraper triggered! Results incoming shortly.")
    else:
        await interaction.followup.send(f"❌ Failed to trigger: {response.status_code}")


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot ready as {client.user}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN not set")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not set")
    client.run(DISCORD_TOKEN)

