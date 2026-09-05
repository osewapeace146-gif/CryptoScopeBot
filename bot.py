import os
import logging
import sqlite3
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import TelegramError, Forbidden, RetryAfter

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Bot token from environment
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# Database setup
DB_PATH = os.environ.get("DB_PATH", "cryptoscope.db")

# Content database - educational and informational posts
CONTENT_POOL = [
    {
        "title": "What is a Blockchain?",
        "body": "A blockchain is a distributed digital ledger that records transactions across many computers. Each 'block' contains a set of transactions, and these blocks are linked together in a 'chain' using cryptography.",
        "why_matters": "Blockchain technology enables secure, transparent, and decentralized record-keeping without requiring a central authority. This forms the foundation of cryptocurrencies and many Web3 applications.",
        "category": "education",
    },
    {
        "title": "What is a Layer 1?",
        "body": "Layer 1 refers to the base or main network of a blockchain ecosystem. Examples include Bitcoin, Ethereum, and Solana. These networks process and validate transactions directly on their own infrastructure.",
        "why_matters": "Layer 1 blockchains are the foundation upon which other applications and scaling solutions are built. They provide the core security, consensus, and data availability for their ecosystem.",
        "category": "education",
    },
    {
        "title": "What is a Layer 2?",
        "body": "Layer 2 solutions are protocols built on top of a base blockchain (Layer 1) to improve speed, reduce costs, and enable more complex applications. They process transactions off the main chain and then settle the results on Layer 1.",
        "why_matters": "Layer 2 solutions help blockchain networks scale, making them faster and more affordable for everyday use, while still leveraging the security of the underlying Layer 1 blockchain.",
        "category": "education",
    },
    {
        "title": "What are Smart Contracts?",
        "body": "Smart contracts are self-executing programs stored on a blockchain that automatically execute when predetermined conditions are met. They enable trustless transactions and agreements without intermediaries.",
        "why_matters": "Smart contracts are the building blocks of DeFi, NFTs, and many other Web3 applications. They allow for programmable, transparent, and automated agreements between parties.",
        "category": "education",
    },
    {
        "title": "What is a Crypto Wallet?",
        "body": "A crypto wallet is a tool that allows users to manage their blockchain assets. It contains a public address for receiving funds and private keys for authorizing transactions. Wallets can be software-based (hot) or hardware-based (cold).",
        "why_matters": "Understanding crypto wallets is essential for safely managing digital assets. Different wallet types offer varying levels of security and convenience for different use cases.",
        "category": "education",
    },
    {
        "title": "What is a Token?",
        "body": "A token is a digital asset built on an existing blockchain network. Unlike coins that operate on their own blockchain, tokens are created and managed through smart contracts on platforms like Ethereum.",
        "why_matters": "Tokens represent a wide variety of digital assets, from currencies and utility tokens to governance rights and digital art. They enable many innovative Web3 applications and economic models.",
        "category": "education",
    },
    {
        "title": "What is a Stablecoin?",
        "body": "A stablecoin is a type of cryptocurrency designed to maintain a stable value relative to a reference asset, typically the US dollar. They achieve stability through various mechanisms including collateralization and algorithmic adjustments.",
        "why_matters": "Stablecoins bridge the volatility of cryptocurrencies with the stability of traditional currencies, making them useful for payments, trading, and as a store of value in the crypto ecosystem.",
        "category": "education",
    },
    {
        "title": "What is Decentralized Finance (DeFi)?",
        "body": "DeFi (Decentralized Finance) refers to a financial system built on blockchain networks that operates without traditional intermediaries like banks. It includes lending, borrowing, trading, and other financial services accessible to anyone with internet access.",
        "why_matters": "DeFi represents a paradigm shift in finance, offering open, transparent, and accessible financial services. It leverages smart contracts to automate and decentralize traditional financial functions.",
        "category": "education",
    },
    {
        "title": "What is Web3?",
        "body": "Web3 is the next evolution of the internet, built on blockchain and decentralized technologies. It envisions a web where users own their data, content, and digital identities, rather than relying on centralized platforms.",
        "why_matters": "Web3 represents a shift toward user ownership, privacy, and decentralization online. It aims to create a more equitable internet where individuals have greater control over their digital lives.",
        "category": "web3",
    },
    {
        "title": "What is Blockchain Consensus?",
        "body": "Consensus mechanisms are protocols used by blockchain networks to agree on the state of the ledger. They ensure all participants have a consistent view of transactions and prevent double-spending.",
        "why_matters": "Consensus mechanisms are the cornerstone of blockchain security and trust. They allow decentralized networks to operate without a central authority, maintaining integrity through collective agreement.",
        "category": "education",
    },
    {
        "title": "What are Transaction Fees?",
        "body": "Transaction fees are costs paid to network validators or miners for processing and including transactions on a blockchain. Fees vary based on network congestion, transaction complexity, and the specific blockchain's fee structure.",
        "why_matters": "Understanding transaction fees is important for using blockchains effectively. They incentivize network participants to maintain and secure the network while managing resource usage.",
        "category": "education",
    },
    {
        "title": "What is Token Utility?",
        "body": "Token utility refers to the specific functions and uses a token provides within its ecosystem. Utility can include access to services, governance voting rights, fee reductions, or representing ownership rights.",
        "why_matters": "Token utility drives the value and adoption of tokens within Web3 projects. Understanding different utility models helps in evaluating the purpose and potential of various tokens.",
        "category": "education",
    },
    {
        "title": "What is On-Chain Activity?",
        "body": "On-chain activity refers to all transactions and interactions that occur directly on a blockchain network. This includes sending and receiving tokens, interacting with smart contracts, and participating in governance.",
        "why_matters": "On-chain activity provides transparent and verifiable records of blockchain usage. Analyzing this activity offers insights into network adoption, user behavior, and overall ecosystem health.",
        "category": "education",
    },
    {
        "title": "What is a Decentralized Application (dApp)?",
        "body": "A dApp (decentralized application) is an application that runs on a blockchain network rather than centralized servers. It uses smart contracts for backend logic and typically offers transparent, user-controlled functionality.",
        "why_matters": "dApps are the building blocks of the Web3 ecosystem, enabling everything from gaming and social media to financial services and governance systems without central intermediaries.",
        "category": "web3",
    },
    {
        "title": "What is Proof of Stake (PoS)?",
        "body": "Proof of Stake is a consensus mechanism where validators are selected to create new blocks based on the number of tokens they have staked (locked up) as collateral. This reduces energy consumption compared to Proof of Work.",
        "why_matters": "PoS offers a more energy-efficient alternative to PoW while maintaining network security. Many modern blockchains have adopted or are transitioning to this consensus mechanism.",
        "category": "education",
    },
    {
        "title": "What is Proof of Work (PoW)?",
        "body": "Proof of Work is a consensus mechanism where miners compete to solve complex mathematical puzzles to add new blocks to the blockchain. This requires significant computational power and energy.",
        "why_matters": "PoW was the first consensus mechanism used in blockchain networks like Bitcoin. While energy-intensive, it has proven secure and resilient over more than a decade of operation.",
        "category": "education",
    },
]

# Extended content with more topics
WEB3_CONTENT = [
    {
        "title": "Layer 2 Scaling Solutions",
        "body": "Layer 2 solutions like Rollups (Optimistic and ZK) and State Channels process transactions off-chain before settling them on the main network. This significantly reduces costs and increases transaction throughput.",
        "why_matters": "These technologies are essential for blockchain scalability, enabling mainstream adoption of decentralized applications with lower fees and better user experiences.",
        "category": "web3",
    },
    {
        "title": "Decentralized Autonomous Organizations (DAOs)",
        "body": "DAOs are organizations managed by smart contracts and governed by token holders who vote on proposals. They operate transparently and democratically, distributing decision-making power among members.",
        "why_matters": "DAOs represent a new model of collaborative governance, enabling communities to manage shared resources and make decisions without traditional hierarchical structures.",
        "category": "web3",
    },
    {
        "title": "Non-Fungible Tokens (NFTs)",
        "body": "NFTs are unique digital assets that represent ownership of specific items, artwork, collectibles, or other digital content. Each NFT is distinct and cannot be replaced by another token.",
        "why_matters": "NFTs have revolutionized digital ownership, enabling creators to monetize digital works and allowing consumers to own verifiable digital assets in the Web3 ecosystem.",
        "category": "web3",
    },
    {
        "title": "Interoperability in Blockchain",
        "body": "Interoperability protocols allow different blockchain networks to communicate and share data. This includes cross-chain bridges and messaging protocols that enable assets and information to move between networks.",
        "why_matters": "Interoperability is crucial for building a connected Web3 ecosystem, enabling assets and data to flow freely between different blockchain networks and applications.",
        "category": "web3",
    },
    {
        "title": "Privacy in Web3",
        "body": "Privacy-focused technologies in Web3 include zero-knowledge proofs and privacy-preserving protocols. These enable transactions and computations to be verified without revealing underlying data.",
        "why_matters": "Privacy is a fundamental concern in digital interactions. Web3 privacy solutions offer new ways to protect user data while maintaining transparency and trust in decentralized systems.",
        "category": "web3",
    },
    {
        "title": "Blockchain Bridges",
        "body": "Blockchain bridges connect different blockchain networks, allowing assets and data to move between them. They facilitate interoperability and enable users to access diverse DeFi and Web3 applications.",
        "why_matters": "Bridges are essential infrastructure for a multi-chain world, allowing users to take advantage of opportunities across different blockchain ecosystems.",
        "category": "web3",
    },
    {
        "title": "Gas Fees and Network Optimization",
        "body": "Gas fees are transaction costs paid to network validators for processing transactions. Users can optimize gas costs by timing transactions during periods of lower network activity or using priority fee mechanisms.",
        "why_matters": "Understanding gas economics helps users navigate blockchain networks efficiently, reducing costs and improving transaction timing for better user experiences.",
        "category": "education",
    },
]

# News-style informational updates
NEWS_STYLE_CONTENT = [
    {
        "title": "Blockchain Adoption Trends",
        "body": "Enterprise blockchain adoption continues to accelerate across banking, healthcare, and supply chain management. Major institutions are exploring distributed ledger technology for efficiency and transparency.",
        "why_matters": "Mainstream blockchain adoption signals growing trust in this technology beyond cryptocurrency, suggesting it will become increasingly integrated into existing digital infrastructure.",
        "category": "news",
    },
    {
        "title": "Web3 Ecosystem Growth",
        "body": "The Web3 ecosystem has seen substantial growth in development activity and user engagement. New applications are expanding beyond finance into social media, identity, and content creation.",
        "why_matters": "Web3's expansion into diverse sectors indicates a maturing ecosystem that may reshape how we interact with digital services and manage our online presence.",
        "category": "web3",
    },
    {
        "title": "Stablecoin Usage Trends",
        "body": "Stablecoins continue to grow in popularity, with billions of dollars in transactions processed daily. They serve as a bridge between traditional finance and the cryptocurrency ecosystem.",
        "why_matters": "Stablecoin adoption represents the convergence of traditional and digital finance, potentially reshaping payment systems and cross-border transactions.",
        "category": "news",
    },
    {
        "title": "Layer 2 Activity Rises",
        "body": "Layer 2 networks are processing more transactions as users seek lower fees and faster settlement. Optimistic and ZK rollups are seeing increased adoption across DeFi applications.",
        "why_matters": "Growing Layer 2 usage suggests scalability solutions are working, making blockchain applications more accessible and cost-effective for everyday users.",
        "category": "news",
    },
    {
        "title": "Blockchain for Good Initiatives",
        "body": "Blockchain technology is being applied to social good initiatives including humanitarian aid distribution, supply chain transparency, and environmental monitoring. Several pilot projects are showing positive results.",
        "why_matters": "These applications demonstrate blockchain's potential for positive social impact, extending beyond financial services to address real-world challenges.",
        "category": "web3",
    },
    {
        "title": "Smart Contract Audits Importance",
        "body": "Smart contract security audits are increasingly recognized as essential for protecting user assets and maintaining trust in DeFi protocols. Auditors review code for vulnerabilities before deployment.",
        "why_matters": "Smart contract security is critical for the long-term health of the Web3 ecosystem, protecting billions in assets and maintaining user confidence in decentralized applications.",
        "category": "education",
    },
]

class DatabaseManager:
    """Manage SQLite database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                updates_enabled INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update_sent_at TIMESTAMP,
                last_content_index INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def register_user(self, user_id: int, username: str = None, first_name: str = None):
        """Register a new user or update existing user's info"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, updates_enabled, joined_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(?, username),
                first_name = COALESCE(?, first_name)
        """, (user_id, username, first_name, username, first_name))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def update_subscription(self, user_id: int, enabled: bool):
        """Update user's subscription status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET updates_enabled = ? WHERE user_id = ?
        """, (1 if enabled else 0, user_id))
        
        conn.commit()
        conn.close()
    
    def get_subscribed_users(self) -> List[Dict]:
        """Get all users with updates enabled"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE updates_enabled = 1
        """)
        users = cursor.fetchall()
        conn.close()
        
        return [dict(user) for user in users]
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def update_user_content_index(self, user_id: int, index: int):
        """Update the last content index sent to a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_content_index = ? WHERE user_id = ?
        """, (index, user_id))
        
        conn.commit()
        conn.close()
    
    def update_last_sent_time(self, user_id: int):
        """Update the time when the last update was sent to a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET last_update_sent_at = CURRENT_TIMESTAMP WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()

class ContentManager:
    """Manage content rotation and selection"""
    
    def __init__(self):
        self.all_content = CONTENT_POOL + NEWS_STYLE_CONTENT + WEB3_CONTENT
        random.seed(time.time())
    
    def get_random_content(self, category: str = None, exclude_index: int = None) -> Dict:
        """Get random content, optionally by category and excluding a specific index"""
        if category:
            available = [c for c in self.all_content if c.get('category') == category]
        else:
            available = self.all_content.copy()
        
        if exclude_index is not None and 0 <= exclude_index < len(self.all_content):
            available = [c for c in available if c != self.all_content[exclude_index]]
        
        if not available:
            return random.choice(self.all_content)
        
        return random.choice(available)
    
    def format_update_message(self, content: Dict) -> str:
        """Format content into a Telegram message"""
        return f"""📰 CryptoScope Update

{content['title']}

{content['body']}

🔎 Why it matters:
{content['why_matters']}

#CryptoScope #CryptoNews"""

class BotManager:
    """Main bot application manager"""
    
    def __init__(self, token: str):
        self.token = token
        self.db = DatabaseManager(DB_PATH)
        self.content_manager = ContentManager()
        self.app = None
    
    def build_app(self):
        """Build the Telegram application with handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("updates", self.updates_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("latest", self.latest_command))
        self.app.add_handler(CommandHandler("learn", self.learn_command))
        self.app.add_handler(CommandHandler("web3", self.web3_command))
        
        # Add callback query handler for inline buttons
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Add job queue for scheduled updates
        self.app.job_queue.run_repeating(self.send_auto_updates, interval=600, first=30)
        
        return self.app
    
    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create the main menu inline keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📰 Latest Update", callback_data="latest"),
                InlineKeyboardButton("📚 Learn Crypto", callback_data="learn"),
            ],
            [
                InlineKeyboardButton("🌐 Web3 Update", callback_data="web3"),
                InlineKeyboardButton("🔔 Updates ON/OFF", callback_data="toggle_updates"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        user = update.effective_user
        
        # Register user
        self.db.register_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        welcome_message = """👋 Welcome to CryptoScope!

Your simple hub for crypto news, blockchain developments, Web3 updates, and educational insights.

Explore the latest information or learn the basics of blockchain technology.

Use the buttons below to get started."""

        await update.message.reply_text(
            welcome_message,
            reply_markup=self.get_main_menu_keyboard()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_message = """CryptoScope provides informational and educational content about crypto, blockchain, and Web3.

Available commands:

📰 /latest — Latest available update
📚 /learn — Learn a crypto concept
🌐 /web3 — Explore Web3 topics
🔔 /updates — Manage automated updates
🛑 /stop — Turn off automated updates

CryptoScope provides general informational and educational content. Nothing provided by the bot is financial, investment, or trading advice."""

        await update.message.reply_text(
            help_message,
            reply_markup=self.get_main_menu_keyboard()
        )
    
    async def updates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /updates command"""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if user_data:
            status = "ON" if user_data.get('updates_enabled', 1) else "OFF"
            message = f"""🔔 Automated updates are currently {status}.

When enabled, you'll receive informational updates approximately every 10 minutes.

Use the button below to toggle updates on or off, or use /stop to disable them."""
        else:
            message = "You haven't registered with the bot yet. Please use /start to begin."
        
        # Create toggle button
        keyboard = [[InlineKeyboardButton("Toggle Updates", callback_data="toggle_updates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stop command - disable automated updates"""
        user_id = update.effective_user.id
        self.db.update_subscription(user_id, False)
        
        await update.message.reply_text(
            "✅ Automated updates have been turned off.\n\nYou can re-enable updates anytime using /updates or the 'Updates ON/OFF' button.",
            reply_markup=self.get_main_menu_keyboard()
        )
    
    async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /latest command - send the latest update"""
        content = self.content_manager.get_random_content()
        await update.message.reply_text(self.content_manager.format_update_message(content))
    
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /learn command - send educational content"""
        content = self.content_manager.get_random_content(category="education")
        await update.message.reply_text(self.content_manager.format_update_message(content))
    
    async def web3_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /web3 command - send Web3 content"""
        content = self.content_manager.get_random_content(category="web3")
        await update.message.reply_text(self.content_manager.format_update_message(content))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "latest":
            content = self.content_manager.get_random_content()
            await query.message.reply_text(self.content_manager.format_update_message(content))
        elif query.data == "learn":
            content = self.content_manager.get_random_content(category="education")
            await query.message.reply_text(self.content_manager.format_update_message(content))
        elif query.data == "web3":
            content = self.content_manager.get_random_content(category="web3")
            await query.message.reply_text(self.content_manager.format_update_message(content))
        elif query.data == "toggle_updates":
            user_data = self.db.get_user(user_id)
            current_status = user_data.get('updates_enabled', 1) if user_data else 1
            new_status = not bool(current_status)
            
            self.db.update_subscription(user_id, new_status)
            
            status_text = "ON" if new_status else "OFF"
            await query.message.reply_text(
                f"✅ Automated updates are now {status_text}.\n\nUse /updates anytime to check your status."
            )
    
    async def send_auto_updates(self, context: ContextTypes.DEFAULT_TYPE):
        """Send automatic updates to subscribed users"""
        logger.info("Running automated update cycle...")
        
        users = self.db.get_subscribed_users()
        if not users:
            logger.info("No subscribed users found")
            return
        
        logger.info(f"Sending updates to {len(users)} users")
        
        for user in users:
            user_id = user['user_id']
            try:
                # Get last content index to avoid repeating the same content
                last_index = user.get('last_content_index', -1)
                content = self.content_manager.get_random_content(exclude_index=last_index)
                
                # Find the index of the selected content
                try:
                    content_index = self.content_manager.all_content.index(content)
                except ValueError:
                    content_index = -1
                
                # Send the message
                await context.bot.send_message(
                    chat_id=user_id,
                    text=self.content_manager.format_update_message(content)
                )
                
                # Update user's last content index and send time
                if content_index != -1:
                    self.db.update_user_content_index(user_id, content_index)
                self.db.update_last_sent_time(user_id)
                
                logger.info(f"✅ Sent update to user {user_id}")
                
                # Small delay to respect rate limits
                await context.bot.sleep(0.5)
                
            except Forbidden:
                logger.warning(f"Bot was blocked by user {user_id}")
                self.db.update_subscription(user_id, False)
                
            except RetryAfter as e:
                logger.warning(f"Rate limit hit for user {user_id}: {e.retry_after} seconds")
                await context.bot.sleep(e.retry_after)
                
            except TelegramError as e:
                logger.error(f"Telegram error for user {user_id}: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error for user {user_id}: {e}")
        
        logger.info("Automated update cycle completed")

def main():
    """Main entry point"""
    logger.info("Starting CryptoScope bot...")
    
    try:
        bot_manager = BotManager(TOKEN)
        app = bot_manager.build_app()
        
        # Log startup info
        total_users = bot_manager.db.get_total_users()
        logger.info(f"Total users: {total_users}")
        
        # Start the bot with polling
        logger.info("Starting polling...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
