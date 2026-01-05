"""
Telegram Bot for Product Delivery and Customer Interaction
Part of the 72-Hour AI Cash System
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import telebot
from telebot import types
import threading
import time
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import load_niches, get_env_variable

logger = get_logger("telegram_bot")

class TelegramBot:
    def __init__(self, token=None):
        self.token = token or get_env_variable('TELEGRAM_BOT_TOKEN')
        
        if not self.token:
            logger.warning("No Telegram bot token provided")
            self.bot = None
            return
        
        self.bot = telebot.TeleBot(self.token)
        self.niches = load_niches()
        self.users = {}
        self.purchases = {}
        
        self.setup_handlers()
        logger.info("Telegram bot initialized")
    
    def setup_handlers(self):
        """Setup message handlers"""
        
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            user_id = message.from_user.id
            username = message.from_user.username or "friend"
            
            # Log user
            self.users[user_id] = {
                'username': username,
                'first_seen': datetime.now().isoformat(),
                'interaction_count': self.users.get(user_id, {}).get('interaction_count', 0) + 1
            }
            
            welcome_text = f"""👋 Welcome to the 72-Hour AI Cash System, {username}!

I'm documenting my journey to go from $0 to $5000 in 72 hours using only AI.

**Available Commands:**
/products - See all AI systems
/status - Check the 72-hour challenge progress
/help - Get help
/about - Learn more about this project

**Quick Links:**
• Full story: [Link in description]
• Free resources: Use /resources

Every purchase directly supports this challenge. Thank you! 🙏"""
            
            self.bot.reply_to(message, welcome_text)
            logger.info(f"New user: {username} ({user_id})")
        
        @self.bot.message_handler(commands=['products'])
        def show_products(message):
            products_text = "**🚀 AI Systems Available:**\n\n"
            
            for niche, details in self.niches.items():
                price = details.get('price', 27 )
                products_text += f"**{details['title']}**\n"
                products_text += f"💰 ${price}\n"
                products_text += f"📱 /buy\\_{niche}\n\n"
            
            products_text += "\n**📦 SPECIAL BUNDLE:**\n"
            products_text += "Get all 6 systems for $97 (Save $65!)\n"
            products_text += "/buy\\_bundle\n\n"
            products_text += "⏰ *Special pricing valid for 72 hours only!*"
            
            self.bot.reply_to(message, products_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['status'])
        def show_status(message):
            # This would connect to the monitoring system
            status_text = """📊 **72-HOUR CHALLENGE STATUS**

⏰ Time Remaining: [X] hours
💰 Revenue: $[X] / $5,000
📈 Progress: [X]%
🎯 Sales: [X] products sold

**What I'm Working On:**
Currently implementing [system name]

**Recent Updates:**
• Hour [X]: [accomplishment]
• Hour [X]: [accomplishment]

Follow along as I build in real-time! 🚀"""
            
            self.bot.reply_to(message, status_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            help_text = """❓ **How Can I Help?**

**To Purchase:**
1. Use /products to see all systems
2. Click on /buy\\_[product] for the one you want
3. Complete payment via secure link
4. Receive instant access

**Support:**
• Questions about products: Just ask!
• Technical issues: Describe your problem
• Refund requests: Contact within 30 days

**Free Resources:**
Use /resources for free tools and guides

💬 **Just message me** - I'm here to help!"""
            
            self.bot.reply_to(message, help_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['resources'])
        def send_resources(message):
            resources_text = """🎁 **FREE RESOURCES**

**AI Tools List:**
• ChatGPT prompts library
• Free automation templates
• Tool comparison guide

**Guides:**
• "Getting Started with AI Automation"
• "7 Free AI Tools You Need"
• "Productivity Framework"

**Community:**
• Free Discord server (link below)
• Weekly Q&A sessions
• Success stories

Download all resources: [LINK]

*These are permanently free - no strings attached! 🎉*"""
            
            self.bot.reply_to(message, resources_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['about'])
        def send_about(message):
            about_text = """📖 **About This Project**

I started with $0, no audience, just a laptop and determination.

**The Challenge:**
Create 6 complete AI systems, build landing pages, automate marketing, and generate $5,000 in sales - all in 72 hours.

**Why AI?**
To prove that anyone can build profitable digital products using free AI tools.

**The Result?**
You're experiencing it right now. Every system, every piece of content, every automation - built from scratch in 72 hours.

**What You Get:**
Real, battle-tested systems that actually work.

**The Mission:**
Democratize access to AI-powered business systems.

Ready to join the revolution? /products"""
            
            self.bot.reply_to(message, about_text, parse_mode='Markdown')
        
        @self.bot.message_handler(func=lambda message: message.text.startswith('/buy_'))
        def handle_purchase(message):
            product = message.text.replace('/buy_', '')
            
            if product == 'bundle':
                title = "Complete AI Systems Bundle (All 6)"
                price = 97
                gumroad_link = "https://gumroad.com/l/ai-bundle-72h"
            elif product in self.niches:
                details = self.niches[product]
                title = details['title']
                price = details.get('price', 27)
                gumroad_link = f"https://gumroad.com/l/{product}-72h"
            else:
                self.bot.reply_to(message, "❌ Product not found. Use /products to see available items.")
                return
            
            purchase_text = f"""🛒 **Ready to Purchase:**

**{title}**
💰 Price: ${price}

**What happens next:**
1. Click the link below to complete payment
2. You'll receive instant access via email
3. Download all materials immediately
4. 30-day money-back guarantee

🔗 **Secure Payment Link:**
{gumroad_link}

Questions? Just reply to this message!

✅ After purchase, forward your receipt here for bonus resources."""
            
            # Add inline keyboard
            markup = types.InlineKeyboardMarkup()
            buy_button = types.InlineKeyboardButton(f"Buy Now - ${price}", url=gumroad_link)
            markup.add(buy_button)
            
            self.bot.reply_to(message, purchase_text, parse_mode='Markdown', reply_markup=markup)
            
            # Log potential purchase
            logger.info(f"Purchase intent: {product} by {message.from_user.username}")
        
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            # Handle general messages
            text = message.text.lower()
            
            if any(word in text for word in ['price', 'cost', 'how much']):
                self.bot.reply_to(message, "Prices start at $27 per system. Use /products to see all options!")
            
            elif any(word in text for word in ['help', 'support']):
                self.bot.reply_to(message, "I'm here to help! Use /help to see all available commands.")
            
            elif any(word in text for word in ['free', 'trial']):
                self.bot.reply_to(message, "Check out our free resources with /resources - no payment needed!")
            
            else:
                self.bot.reply_to(message, 
                    "Thanks for your message! I'm a bot, but I've recorded your message. "
                    "Use /help to see what I can do, or just ask your question!")
    
    def run(self):
        """Run the bot"""
        if not self.bot:
            logger.error("Bot not initialized - missing token")
            return
        
        logger.info("Starting Telegram bot...")
        try:
            self.bot.infinity_polling()
        except Exception as e:
            logger.error(f"Bot error: {e}")
    
    def run_threaded(self):
        """Run bot in separate thread"""
        if not self.bot:
            logger.error("Bot not initialized")
            return None
        
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        logger.info("Bot running in background thread")
        return thread

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Telegram Bot for 72-Hour Cash System')
    parser.add_argument('--token', help='Bot token (or set TELEGRAM_BOT_TOKEN env var)')
    
    args = parser.parse_args()
    
    bot = TelegramBot(token=args.token)
    if bot.bot:
        bot.run()
    else:
        print("❌ Failed to initialize bot. Please provide a valid token.")

if __name__ == "__main__":
    main()
