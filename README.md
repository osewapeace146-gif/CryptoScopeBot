# CryptoScope Telegram Bot

CryptoScope is an informational and educational Telegram bot focused on crypto news, blockchain developments, Web3 ecosystem updates, and educational insights.

**Username:** @CryptoScopeBot

## Features

- 📰 Latest Updates - Get current informational content
- 📚 Learn Crypto - Educational content about blockchain concepts
- 🌐 Web3 Updates - Explore Web3 ecosystem developments
- 🔔 Automated Updates - Optional 10-minute informational updates
- 🛑 Easy Opt-Out - Turn updates on/off with one click

## Important Notes

This bot is designed to be compliant with Telegram's advertising policies. It provides:

- ✅ Educational and informational content
- ✅ Neutral market information
- ✅ Blockchain and Web3 education

**No investment advice, trading signals, or profit promises.**

## Deployment Instructions

### 1. Create the Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to create a new bot
3. Choose a name: `CryptoScope`
4. Choose a username: `CryptoScopeBot` (must end with "bot")
5. Copy the bot token provided by BotFather

### 2. Set Up Environment Variables

1. Rename `.env.example` to `.env`
2. Replace `your_bot_token_here` with your actual bot token
3. **Never commit your .env file**

### 3. Deploy to Railway

1. Create a GitHub repository
2. Upload all files to the repository:
   - bot.py
   - requirements.txt
   - runtime.txt
   - mise.toml
   - .env.example
   - .gitignore
   - README.md
3. Go to [Railway.app](https://railway.app/)
4. Click "New Project" → "Deploy from GitHub repo"
5. Connect your GitHub account and select the repository
6. Add the environment variable:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token
7. Railway will automatically deploy your bot

### 4. Start Command

The bot will run automatically when deployed. No additional start commands are needed.

### 5. Check Logs

To view logs on Railway:

1. Go to your Railway dashboard
2. Select your project
3. Click on the "Logs" tab
4. View real-time logs

### 6. How the 10-Minute Update System Works

The bot automatically sends educational/informational updates every 10 minutes to users who:

- Have started the bot
- Have updates enabled (default after /start)

**Features:**
- Sends diverse content to avoid repetition
- Respects user preferences (can be toggled on/off)
- Handles rate limiting and errors gracefully
- Automatically stops sending to users who block the bot

### 7. Changing the Update Interval

To change the update interval, edit the `interval` parameter in `bot.py`:

```python
# Change 600 (seconds) to your desired interval
self.app.job_queue.run_repeating(self.send_auto_updates, interval=600, first=30)
