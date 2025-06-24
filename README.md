# CryptoAlertsWithDiscord

This project what does is it will create a dashboard table in discord (in reality is a comment that will be edited/updated every minute or whatever time you want by using cron) and showing the price of some cryptos (BTC, XRP and AVAX) The first row of dashboard will be always the most updated row. Also will be displaying the RSI, SMA VWAP and give you the signal to buy, sell, p buy (probably buy), p sell (probably sell), sell ob (overbought), buy os (oversell).

Not only that, will also send a new message if buy or sell time, except during hold signal.

This works by using python 3.9 and up

First, in the webserver, you will need to install the following (run it in terminal, Linux):

pip install pandas ta yfinance requests

Go to the Discord Developer Portal in order to create your discord bot.
https://discord.com/developers/applications

Create a new application.

Under the “Bot” tab:

Click "Add Bot".

Copy the Bot Token (you’ll use it in your code).

Under “OAuth2” → “URL Generator”:

Scopes: bot

Bot Permissions: Send Messages, Manage Messages, Read Message History

Copy and use the generated URL to invite the bot to your server.

in the terminal of webserver execute this:

pip install -U discord.py

You will need to execute only once this:

send_initial_message.py

take note of the id of the message that is displayed in terminal. you will copy that and paste it in DISCORD_MESSAGE_ID = "" under bot.py file

also, remember to modify DISCORD_BOT_TOKEN = "" and DISCORD_CHANNEL_ID = "" with your data on bot.py and in send_initial_message.py files

now you can execute it manually by doing in terminal:

python3 bot.py

now that is working, you can add it as cron job (Linux).
