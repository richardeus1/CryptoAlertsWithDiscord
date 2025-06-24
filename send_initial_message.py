import requests

DISCORD_BOT_TOKEN = ""
DISCORD_CHANNEL_ID = ""

url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json"
}

initial_content = "```md\nTime   | Coin  | Price     | RSI    | SMA      | Signal\n" + "-"*56 + "\n```"

data = {
    "content": initial_content
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)  # Will contain the message ID
