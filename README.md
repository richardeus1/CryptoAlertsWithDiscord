# CryptoAlertsWithDiscord

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

take note of the id of the message that is displayed in terminal. you will copy that and paste it in:

now you can execute it manually by doing in terminal:

python3 bot.py

now that is working, you can add it as cron job (Linux).
