"""
Social Media Automation for 72-Hour Cash System
Automates posting to Twitter, Reddit, Telegram
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import tweepy
import praw
import telebot
import schedule
import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict
import threading

from utils.logger import get_logger
from utils.helpers import load_niches, load_config

logger = get_logger("social_automation")

class SocialAutomation:
    def __init__(self, config_file="social_config.json"):
        self.config = self.load_config(config_file)
        self.setup_clients()
        self.content_queue = []
        self.post_log = []
        self.running = False
        
    def load_config(self, config_file):
        """Load or create configuration"""
        
        default_config = {
            "twitter": {
                "enabled": False,
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_secret": "",
                "post_interval": 30,  # minutes
                "max_posts_per_day": 20
            },
            "reddit": {
                "enabled": False,
                "client_id": "",
                "client_secret": "",
                "user_agent": "72HourAICashSystem/1.0",
                "subreddits": [
                    "sidehustle", "beermoney", "Entrepreneur",
                    "digitalnomad", "passive_income", "startups"
                ],
                "post_interval": 240,  # minutes
                "max_posts_per_day": 5
            },
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "channel_id": "",
                "post_interval": 120,  # minutes
                "auto_reply": True
            },
            "content": {
                "ebooks": {
                    "men_lust": "Alpha Male AI System",
                    "women_beauty": "AI Beauty OS",
                    "rich_time": "Time Billionaire System",
                    "parents_peace": "Peaceful Parenting AI",
                    "kids_dreams": "DreamBuilder AI",
                    "poor_hope": "Hope Economy Blueprint"
                },
                "landing_pages": {},
                "emergency_mode": False
            },
            "settings": {
                "timezone": "UTC",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(hours=72)).isoformat(),
                "target_amount": 5000
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"⚠️ Created default config: {config_file}")
            return default_config
    
    def setup_clients(self):
        """Setup API clients"""
        
        # Twitter/X client
        if self.config['twitter']['enabled'] and all(self.config['twitter'].get(k) for k in ['api_key', 'api_secret', 'access_token', 'access_secret']):
            auth = tweepy.OAuthHandler(
                self.config['twitter']['api_key'],
                self.config['twitter']['api_secret']
            )
            auth.set_access_token(
                self.config['twitter']['access_token'],
                self.config['twitter']['access_secret']
            )
            self.twitter_api = tweepy.API(auth)
            print("✅ Twitter client initialized")
        else:
            self.twitter_api = None
            print("⚠️ Twitter not configured")
        
        # Reddit client
        if self.config['reddit']['enabled'] and all(self.config['reddit'].get(k) for k in ['client_id', 'client_secret']):
            self.reddit_client = praw.Reddit(
                client_id=self.config['reddit']['client_id'],
                client_secret=self.config['reddit']['client_secret'],
                user_agent=self.config['reddit']['user_agent']
            )
            print("✅ Reddit client initialized")
        else:
            self.reddit_client = None
            print("⚠️ Reddit not configured")
        
        # Telegram bot
        if self.config['telegram']['enabled'] and self.config['telegram'].get('bot_token'):
            self.telegram_bot = telebot.TeleBot(self.config['telegram']['bot_token'])
            print("✅ Telegram bot initialized")
        else:
            self.telegram_bot = None
            print("⚠️ Telegram not configured")
    
    def generate_tweet(self, niche=None):
        """Generate a tweet"""
        
        templates = [
            "Just automated my entire {niche} process using AI. Went from {before} to {after} in {time}. The future is here. 🚀",
            "Most people struggle with {niche}. Here's how AI solves it in 3 steps: 1) {step1} 2) {step2} 3) {step3}",
            "I'm documenting my 72-hour challenge to go from $0 to $5000 using only AI. Day {day}: Working on {niche} system...",
            "The {niche} industry doesn't want you to know about these AI tools: • {tool1} • {tool2} • {tool3}",
            "Just found an AI trick for {niche} that saved me {hours} hours this week. Game changer.",
            "From overwhelmed to automated: How AI transformed my {niche} approach.",
            "Why you're struggling with {niche} (and the AI solution nobody talks about).",
            "AI for {niche}: The good, the bad, and the incredibly profitable.",
            "My {niche} system now runs on autopilot thanks to these 3 AI tools.",
            "The secret to mastering {niche} isn't working harder. It's working smarter with AI."
        ]
        
        if not niche:
            niche = random.choice(list(self.config['content']['ebooks'].keys()))
        
        niche_name = self.config['content']['ebooks'].get(niche, niche.replace('_', ' '))
        
        # Fill template variables
        variables = {
            'niche': niche_name,
            'before': random.choice(['manual work', 'chaos', 'inefficiency', 'frustration']),
            'after': random.choice(['automated', 'streamlined', 'profitable', 'effortless']),
            'time': random.choice(['24 hours', '3 days', 'a week', '72 hours']),
            'step1': random.choice(['Identify patterns', 'Automate repetitive tasks', 'Use AI analysis']),
            'step2': random.choice(['Implement automation', 'Train the AI', 'Set up systems']),
            'step3': random.choice(['Scale results', 'Monitor and optimize', 'Automate marketing']),
            'day': random.randint(1, 3),
            'tool1': random.choice(['ChatGPT', 'Bing AI', 'Midjourney', 'Canva AI']),
            'tool2': random.choice(['Jasper', 'Copy.ai', 'Grammarly', 'Otter.ai']),
            'tool3': random.choice(['Notion AI', 'Gamma', 'Beautiful.ai', 'Tome']),
            'hours': random.randint(5, 20)
        }
        
        template = random.choice(templates)
        tweet = template.format(**variables)
        
        # Add hashtags
        hashtags = [
            f"#{niche.replace('_', '')}",
            "#AI",
            "#Automation",
            "#SideHustle",
            "#72HourChallenge",
            "#Tech",
            random.choice(["#Entrepreneur", "#Startup", "#DigitalNomad"]),
            random.choice(["#Productivity", "#Efficiency", "#Innovation"])
        ]
        
        tweet += "\n\n" + " ".join(hashtags[:5])
        
        # Add call to action (sometimes)
        if random.random() > 0.5:
            cta_options = [
                "\n\nFull system available → [LINK IN BIO]",
                "\n\nDocumenting the whole process → [PROFILE LINK]",
                "\n\nFree guide in replies 👇",
                "\n\nDM me for the free checklist"
            ]
            tweet += random.choice(cta_options)
        
        # Ensure tweet length
        if len(tweet) > 280:
            tweet = tweet[:275] + "..."
        
        return tweet
    
    def generate_reddit_post(self, subreddit, niche=None):
        """Generate Reddit post"""
        
        if not niche:
            niche = random.choice(list(self.config['content']['ebooks'].keys()))
        
        niche_name = self.config['content']['ebooks'].get(niche, niche.replace('_', ' '))
        
        title_templates = [
            "AI for {niche}: What actually works in 2024",
            "Just automated my {niche} with AI - results after 30 days",
            "The {niche} industry is changing because of AI",
            "How I used AI to solve my biggest {niche} problem",
            "AMA about using AI for {niche} (72-hour challenge participant)",
            "Most people are doing {niche} wrong. Here's the AI way.",
            "From zero to profitable in {niche} using only free AI tools",
            "The future of {niche} is automated. Here's how to prepare."
        ]
        
        content_templates = [
            """I've been experimenting with AI tools for {niche} as part of a 72-hour challenge to go from $0 to $5000.

After testing dozens of tools, here are the ones that actually delivered results:

**Free Tools That Work:**
1. {tool1} - For {use1}
2. {tool2} - For {use2}
3. {tool3} - For {use3}

**The Process:**
- Step 1: {step1}
- Step 2: {step2}
- Step 3: {step3}

**Results so far:** {result}

What AI tools are you using for {niche}? Any recommendations?""",
            
            """I'm currently on hour {hour} of a 72-hour challenge to build a complete {niche} system using only AI.

**Progress Update:**
- Built: {built}
- Learned: {learned}
- Earned: ${earned}

**Biggest Insight:** {insight}

**Next Steps:** {next_steps}

AMA about the process or using AI for {niche}!""",
            
            """Most people overcomplicate {niche}. After working with AI on this, I've simplified it to a 3-step framework:

**The Simple {niche} Framework:**
1. {frame1}
2. {frame2}
3. {frame3}

**Why This Works with AI:**
- {reason1}
- {reason2}
- {reason3}

**Free Resources to Get Started:**
- Resource 1: {res1}
- Resource 2: {res2}

The key is starting simple and letting AI handle the complexity. What would you automate first in your {niche} process?"""
        ]
        
        # Fill variables
        variables = {
            'niche': niche_name,
            'tool1': random.choice(['ChatGPT', 'Bing AI', 'Google Bard', 'Claude']),
            'tool2': random.choice(['Canva', 'Midjourney', 'DALL-E', 'Stable Diffusion']),
            'tool3': random.choice(['Notion AI', 'Grammarly', 'Otter.ai', 'Descript']),
            'use1': random.choice(['content creation', 'idea generation', 'problem solving']),
            'use2': random.choice(['visual design', 'image creation', 'branding']),
            'use3': random.choice(['organization', 'writing', 'transcription']),
            'step1': random.choice(['Identify the bottleneck', 'Find the repetitive task', 'Define the desired outcome']),
            'step2': random.choice(['Research AI solutions', 'Test different prompts', 'Build the workflow']),
            'step3': random.choice(['Implement and iterate', 'Automate completely', 'Scale the system']),
            'result': random.choice(['Saved 10+ hours/week', 'Increased efficiency by 40%', 'Generated $500 in first week']),
            'hour': random.randint(1, 72),
            'built': random.choice(['automated content system', 'lead generation bot', 'customer service AI']),
            'learned': random.choice(['AI has limitations but incredible potential', 'Prompt engineering is a real skill', 'Automation requires upfront work']),
            'earned': random.randint(100, 2000),
            'insight': random.choice(['The bottleneck is usually human, not technical', 'AI works best with human oversight', 'Simple systems scale better']),
            'next_steps': random.choice(['Add more automation layers', 'Scale to other niches', 'Document everything for others']),
            'frame1': random.choice(['Define the outcome clearly', 'Identify what can be automated', 'Gather necessary data']),
            'frame2': random.choice(['Build the AI workflow', 'Test with small samples', 'Iterate based on results']),
            'frame3': random.choice(['Scale the automation', 'Monitor performance', 'Optimize continuously']),
            'reason1': random.choice(['AI handles repetitive tasks perfectly', 'Computers don\'t get tired or bored', 'Scale becomes almost free']),
            'reason2': random.choice(['Pattern recognition at scale', '24/7 operation', 'Consistent quality']),
            'reason3': random.choice(['Continuous improvement', 'Data-driven optimization', 'Rapid iteration']),
            'res1': random.choice(['Free AI tool list on my profile', 'YouTube tutorial series', 'GitHub repository']),
            'res2': random.choice(['Community Discord server', 'Free email course', 'Template library'])
        }
        
        title = random.choice(title_templates).format(**variables)
        content = random.choice(content_templates).format(**variables)
        
        # Soft CTA (only 30% of posts)
        if random.random() > 0.7:
            cta = "\n\n*(Documenting my entire 72-hour challenge journey. Full system available if anyone's interested in the complete blueprint.)*"
            content += cta
        
        return title, content
    
    def post_to_twitter(self):
        """Post to Twitter/X"""
        
        if not self.twitter_api:
            print("⚠️ Twitter not configured")
            return False
        
        try:
            tweet = self.generate_tweet()
            self.twitter_api.update_status(tweet)
            
            log_entry = {
                "platform": "twitter",
                "content": tweet[:50] + "...",
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.post_log.append(log_entry)
            
            print(f"✅ Tweeted: {tweet[:50]}...")
            self.save_log()
            return True
            
        except Exception as e:
            print(f"❌ Twitter error: {e}")
            return False
    
    def post_to_reddit(self):
        """Post to Reddit"""
        
        if not self.reddit_client or not self.config['reddit']['subreddits']:
            print("⚠️ Reddit not configured")
            return False
        
        subreddit_name = random.choice(self.config['reddit']['subreddits'])
        niche = random.choice(list(self.config['content']['ebooks'].keys()))
        
        try:
            title, content = self.generate_reddit_post(subreddit_name, niche)
            subreddit = self.reddit_client.subreddit(subreddit_name)
            
            submission = subreddit.submit(
                title=title,
                selftext=content
            )
            
            log_entry = {
                "platform": "reddit",
                "subreddit": subreddit_name,
                "title": title,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "post_id": submission.id
            }
            self.post_log.append(log_entry)
            
            print(f"✅ Posted to r/{subreddit_name}: {title[:50]}...")
            self.save_log()
            return True
            
        except Exception as e:
            print(f"❌ Reddit error ({subreddit_name}): {e}")
            return False
    
    def post_to_telegram(self):
        """Post to Telegram channel"""
        
        if not self.telegram_bot or not self.config['telegram']['channel_id']:
            print("⚠️ Telegram not configured")
            return False
        
        try:
            niche = random.choice(list(self.config['content']['ebooks'].keys()))
            niche_name = self.config['content']['ebooks'][niche]
            
            messages = [
                f"🚀 Update from 72-Hour AI Challenge:\n\nWorking on {niche_name} system...",
                f"💡 AI Tip for {niche_name.replace('AI', '').strip()}:\n\n{self.generate_ai_tip(niche)}",
                f"⏰ Progress Check: Hour {random.randint(1, 72)} of 72\n\nCurrent focus: {niche_name}",
                f"🆓 Free Resource: {self.generate_free_resource(niche)}"
            ]
            
            message = random.choice(messages)
            
            self.telegram_bot.send_message(
                chat_id=self.config['telegram']['channel_id'],
                text=message,
                parse_mode="Markdown"
            )
            
            log_entry = {
                "platform": "telegram",
                "content": message[:50] + "...",
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.post_log.append(log_entry)
            
            print(f"✅ Telegram update sent")
            self.save_log()
            return True
            
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def generate_ai_tip(self, niche):
        """Generate AI tip for Telegram"""
        
        tips = [
            "Use ChatGPT to analyze your target audience's pain points before creating content.",
            "Create a 'prompt library' for repetitive tasks to save time.",
            "Combine multiple AI tools for better results (e.g., ChatGPT for text + Midjourney for images).",
            "Train AI on your own writing style for more consistent output.",
            "Use AI to A/B test different marketing messages automatically.",
            "Automate customer service with AI while maintaining human oversight.",
            "Create content pillars and let AI generate variations for each.",
            "Use AI for market research - it can analyze trends faster than humans.",
            "Automate social media scheduling with AI-generated content calendars.",
            "Use AI to personalize outreach at scale without sounding robotic."
        ]
        
        return random.choice(tips)
    
    def generate_free_resource(self, niche):
        """Generate free resource mention"""
        
        resources = [
            "Free ChatGPT prompt template for this niche available on our GitHub.",
            "Check our free Notion template for organizing AI workflows.",
            "Free video tutorial series on YouTube (link in profile).",
            "Join our free Discord for daily AI tips and community support.",
            "Free checklist: '7 Steps to Automate [Niche] with AI'.",
            "Free workshop this Friday on AI automation for beginners.",
            "Free ebook chapter available for email subscribers.",
            "Free tool comparison spreadsheet in our Google Drive.",
            "Free consultation call for the first 10 people to message.",
            "Free AI tool stack recommendation based on your needs."
        ]
        
        return random.choice(resources).replace("[Niche]", niche.replace('_', ' '))
    
    def save_log(self):
        """Save post log to file"""
        
        with open("social_log.json", "w") as f:
            json.dump(self.post_log, f, indent=2)
    
    def load_log(self):
        """Load post log from file"""
        
        if os.path.exists("social_log.json"):
            with open("social_log.json", "r") as f:
                self.post_log = json.load(f)
            return True
        return False
    
    def get_stats(self):
        """Get posting statistics"""
        
        stats = {
            "total_posts": len(self.post_log),
            "by_platform": {},
            "success_rate": 0,
            "last_24_hours": 0
        }
        
        success_count = 0
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        for post in self.post_log:
            platform = post.get("platform", "unknown")
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            
            if post.get("success", False):
                success_count += 1
            
            post_time = datetime.fromisoformat(post["timestamp"])
            if post_time > twenty_four_hours_ago:
                stats["last_24_hours"] += 1
        
        if self.post_log:
            stats["success_rate"] = (success_count / len(self.post_log)) * 100
        
        return stats
    
    def schedule_posts(self):
        """Schedule automated posts"""
        
        # Twitter schedule
        if self.config['twitter']['enabled']:
            interval = self.config['twitter']['post_interval']
            schedule.every(interval).minutes.do(self.post_to_twitter)
            print(f"📅 Twitter: Every {interval} minutes")
        
        # Reddit schedule
        if self.config['reddit']['enabled']:
            interval = self.config['reddit']['post_interval']
            schedule.every(interval).minutes.do(self.post_to_reddit)
            print(f"📅 Reddit: Every {interval} minutes")
        
        # Telegram schedule
        if self.config['telegram']['enabled']:
            interval = self.config['telegram']['post_interval']
            schedule.every(interval).minutes.do(self.post_to_telegram)
            print(f"📅 Telegram: Every {interval} minutes")
        
        print(f"\n⏰ Scheduling started at {datetime.now().strftime('%H:%M:%S')}")
        print("Press Ctrl+C to stop\n")
    
    def run_scheduled(self):
        """Run the scheduling loop"""
        
        self.running = True
        self.load_log()
        self.schedule_posts()
        
        try:
            while self.running:
                schedule.run_pending()
                
                # Every hour, show stats
                if datetime.now().minute == 0:
                    stats = self.get_stats()
                    print(f"\n📊 Hourly Stats: {stats['total_posts']} total posts, "
                          f"{stats['last_24_hours']} in last 24h, "
                          f"{stats['success_rate']:.1f}% success rate")
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\n👋 Stopping scheduler...")
            self.stop()
    
    def run_once(self):
        """Run one posting cycle"""
        
        print("🔄 Running one posting cycle...")
        
        results = {
            "twitter": self.post_to_twitter() if self.config['twitter']['enabled'] else "disabled",
            "reddit": self.post_to_reddit() if self.config['reddit']['enabled'] else "disabled",
            "telegram": self.post_to_telegram() if self.config['telegram']['enabled'] else "disabled"
        }
        
        stats = self.get_stats()
        print(f"\n📊 Current stats: {stats['total_posts']} posts total")
        
        return results
    
    def stop(self):
        """Stop the automation"""
        
        self.running = False
        schedule.clear()
        print("🛑 Automation stopped")

# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Social Media Automation for 72-Hour Cash System")
    parser.add_argument("--mode", choices=["schedule", "once", "stats", "test"], 
                       default="schedule", help="Run mode")
    parser.add_argument("--config", default="social_config.json", help="Config file")
    
    args = parser.parse_args()
    
    automator = SocialAutomation(args.config)
    
    if args.mode == "schedule":
        print("🚀 Starting scheduled automation...")
        automator.run_scheduled()
        
    elif args.mode == "once":
        results = automator.run_once()
        print("\n📋 Results:")
        for platform, result in results.items():
            print(f"  {platform}: {result}")
        
    elif args.mode == "stats":
        stats = automator.get_stats()
        print("\n📊 Statistics:")
        print(f"  Total posts: {stats['total_posts']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Last 24 hours: {stats['last_24_hours']}")
        print("\n  By platform:")
        for platform, count in stats['by_platform'].items():
            print(f"    {platform}: {count}")
        
    elif args.mode == "test":
        print("🧪 Test mode - Generating sample content:")
        print("\nSample Tweet:")
        print("-" * 40)
        print(automator.generate_tweet())
        print("-" * 40)
        
        print("\nSample Reddit Post:")
        print("-" * 40)
        title, content = automator.generate_reddit_post("test")
        print(f"Title: {title}")
        print(f"\nContent preview: {content[:100]}...")
        print("-" * 40)