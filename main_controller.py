"""
Main Controller for 72-Hour AI Cash System
Orchestrates all modules and manages the complete workflow
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import time

# Setup path
sys.path.append(str(Path(__file__).parent))

from utils.logger import get_logger
from utils.helpers import load_config, load_niches
from modules.ebook_generator import EbookGenerator
from modules.image_generator import ImageGenerator
from modules.pdf_converter import PDFConverter
from modules.landing_generator import LandingPageGenerator
from modules.video_maker import VideoMaker
from automation.social_automation import SocialAutomation
from automation.telegram_bot import TelegramBot
from monitoring.sales_tracker import SalesTracker
from monitoring.emergency import EmergencyProtocol

logger = get_logger("main_controller")

class MainController:
    def __init__(self, config_path="config/config.yaml", simulate=False):
        self.config = load_config(config_path)
        self.niches = load_niches()
        self.simulate = simulate
        
        # Initialize modules
        self.ebook_gen = EbookGenerator()
        self.image_gen = ImageGenerator()
        self.pdf_conv = PDFConverter()
        self.landing_gen = LandingPageGenerator()
        self.video_maker = None  # Initialize when needed
        self.social_auto = None  # Initialize when needed
        self.telegram_bot = None  # Initialize when needed
        
        # Initialize monitoring
        self.sales_tracker = SalesTracker(
            target=self.config['system']['target_revenue'],
            duration_hours=self.config['system']['deadline_hours']
        )
        self.emergency = EmergencyProtocol(self.sales_tracker, self.config)
        
        logger.info("Main Controller initialized")
    
    def phase_1_production(self):
        """Phase 1 (Hours 0-12): Content Production"""
        logger.info("=" * 60)
        logger.info("PHASE 1: CONTENT PRODUCTION (Hours 0-12)")
        logger.info("=" * 60)
        
        print("\n🏭 PHASE 1: CONTENT PRODUCTION")
        print("="*60)
        print("Goal: Generate all 6 ebooks, covers, PDFs, and landing pages")
        print("="*60 + "\n")
        
        # Step 1: Generate ebooks
        print("\n📚 Step 1: Generating eBooks...")
        ebook_files = self.ebook_gen.generate_all()
        logger.success(f"Generated {len(ebook_files)} ebooks")
        
        # Step 2: Generate covers
        print("\n🎨 Step 2: Generating cover images...")
        cover_files = self.image_gen.generate_all(use_api=False)
        logger.success(f"Generated {len(cover_files)} covers")
        
        # Step 3: Convert to PDF
        print("\n📄 Step 3: Converting to PDFs...")
        pdf_files = self.pdf_conv.convert_all()
        logger.success(f"Generated {len(pdf_files)} PDFs")
        
        # Step 4: Generate landing pages
        print("\n🌐 Step 4: Generating landing pages...")
        landing_files = self.landing_gen.generate_all()
        logger.success(f"Generated {len(landing_files)} landing pages")
        
        print("\n✅ PHASE 1 COMPLETE!")
        print(f"   • Ebooks: {len(ebook_files)}")
        print(f"   • Covers: {len(cover_files)}")
        print(f"   • PDFs: {len(pdf_files)}")
        print(f"   • Landing Pages: {len(landing_files)}")
        print("\n⏭️  Next: Upload PDFs to Gumroad manually")
        print("   Then proceed to Phase 2\n")
        
        input("Press Enter when ready to continue...")
    
    def phase_2_platform_setup(self):
        """Phase 2 (Hours 12-24): Platform Setup"""
        logger.info("=" * 60)
        logger.info("PHASE 2: PLATFORM SETUP (Hours 12-24)")
        logger.info("=" * 60)
        
        print("\n🚀 PHASE 2: PLATFORM SETUP")
        print("="*60)
        print("Goal: Set up sales platforms and automation systems")
        print("="*60 + "\n")
        
        # Manual steps
        print("📋 MANUAL STEPS REQUIRED:\n")
        print("1. GUMROAD SETUP:")
        print("   • Go to gumroad.com")
        print("   • Create account if needed")
        print("   • Upload all 6 PDFs as products")
        print("   • Set price: $27 each")
        print("   • Add descriptions from landing pages")
        print("   • Get product URLs\n")
        
        print("2. LANDING PAGE DEPLOYMENT:")
        print("   • Go to netlify.com/drop")
        print("   • Drag & drop each landing page HTML")
        print("   • Get deployment URLs")
        print("   • Update Gumroad product links\n")
        
        print("3. TELEGRAM BOT:")
        print("   • Message @BotFather on Telegram")
        print("   • Create new bot: /newbot")
        print("   • Save bot token to .env file")
        print("   • Start bot: python automation/telegram_bot.py\n")
        
        print("4. SOCIAL MEDIA ACCOUNTS:")
        print("   • Create Twitter account (if needed)")
        print("   • Create Reddit account (if needed)")
        print("   • Get API credentials")
        print("   • Save to .env file\n")
        
        proceed = input("Have you completed these steps? (y/n): ").lower().strip()
        
        if proceed == 'y':
            print("\n✅ PHASE 2 COMPLETE!")
            print("⏭️  Proceeding to Phase 3: Automation\n")
        else:
            print("\n⏸️  Complete setup steps before continuing.")
            print("Run 'python main_controller.py --phase 3' when ready.\n")
            sys.exit(0)
    
    def phase_3_automation(self):
        """Phase 3 (Hours 24-72): Automation & Monitoring"""
        logger.info("=" * 60)
        logger.info("PHASE 3: AUTOMATION & MONITORING (Hours 24-72)")
        logger.info("=" * 60)
        
        print("\n🤖 PHASE 3: AUTOMATION & MONITORING")
        print("="*60)
        print("Goal: Run automation, monitor sales, achieve $5000 target")
        print("="*60 + "\n")
        
        # Check configuration
        print("🔍 Checking configuration...\n")
        
        config_ok = True
        
        # Check social media config
        try:
            self.social_auto = SocialAutomation()
            print("✅ Social automation configured")
        except Exception as e:
            print(f"⚠️  Social automation: {e}")
            config_ok = False
        
        # Check Telegram bot
        try:
            self.telegram_bot = TelegramBot()
            if self.telegram_bot.bot:
                print("✅ Telegram bot configured")
            else:
                print("⚠️  Telegram bot not configured")
        except Exception as e:
            print(f"⚠️  Telegram bot: {e}")
        
        print()
        
        if not config_ok and not self.simulate:
            print("⚠️  Some integrations are not configured.")
            proceed = input("Continue anyway? (y/n): ").lower().strip()
            if proceed != 'y':
                sys.exit(0)
        
        # Start monitoring
        print("🎯 Starting monitoring system...\n")
        self.sales_tracker.print_dashboard()
        
        print("\n🤖 Starting automation threads...\n")
        
        # Start Telegram bot in background
        if self.telegram_bot and self.telegram_bot.bot:
            bot_thread = self.telegram_bot.run_threaded()
            print("✅ Telegram bot running")
        
        # Start social media automation
        if self.social_auto and not self.simulate:
            import threading
            social_thread = threading.Thread(
                target=self.social_auto.run_scheduled,
                daemon=True
            )
            social_thread.start()
            print("✅ Social automation running")
        
        print("\n" + "="*60)
        print("🔥 SYSTEM FULLY OPERATIONAL")
        print("="*60)
        print("\nMonitoring will run automatically.")
        print("Emergency protocol will activate if needed.")
        print("\nPress Ctrl+C to stop.\n")
        
        try:
            # Monitoring loop
            check_interval = 3600  # 1 hour
            
            while True:
                # Check sales
                status = self.sales_tracker.get_current_status()
                
                if status['is_expired']:
                    print("\n⏰ 72-HOUR DEADLINE REACHED!")
                    self.sales_tracker.print_dashboard()
                    break
                
                # Check emergency protocol
                should_activate, reason = self.emergency.should_activate()
                if should_activate:
                    self.emergency.activate(reason)
                    self.emergency.print_final_instructions()
                
                # Print status
                self.sales_tracker.print_dashboard()
                
                # Wait for next check
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 System stopped by user")
            self.sales_tracker.print_dashboard()
    
    def run_full_workflow(self):
        """Run complete 72-hour workflow"""
        print("\n" + "="*70)
        print("🚀 72-HOUR AI CASH SYSTEM - FULL WORKFLOW")
        print("="*70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: ${self.config['system']['target_revenue']}")
        print(f"Deadline: {self.sales_tracker.deadline.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Phase 1
        self.phase_1_production()
        
        # Phase 2
        self.phase_2_platform_setup()
        
        # Phase 3
        self.phase_3_automation()
        
        # Final report
        print("\n" + "="*70)
        print("🏁 72-HOUR CHALLENGE COMPLETE!")
        print("="*70)
        self.sales_tracker.print_dashboard()
    
    def quick_start(self):
        """Quick start guide"""
        print("\n" + "="*70)
        print("📖 72-HOUR AI CASH SYSTEM - QUICK START GUIDE")
        print("="*70 + "\n")
        
        print("STEP-BY-STEP INSTRUCTIONS:\n")
        
        print("✅ HOUR 0-1: Setup")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Copy .env.example to .env")
        print("   3. Add your API keys to .env (optional for Phase 1)\n")
        
        print("✅ HOUR 1-12: Content Creation")
        print("   Run: python main_controller.py --phase 1")
        print("   This generates all ebooks, covers, PDFs, and landing pages\n")
        
        print("✅ HOUR 12-24: Platform Setup")
        print("   1. Upload PDFs to Gumroad")
        print("   2. Deploy landing pages to Netlify")
        print("   3. Set up Telegram bot")
        print("   4. Configure social media")
        print("   Run: python main_controller.py --phase 2\n")
        
        print("✅ HOUR 24-72: Automation & Sales")
        print("   Run: python main_controller.py --phase 3")
        print("   System will automatically:")
        print("   • Post to social media")
        print("   • Monitor sales")
        print("   • Activate emergency protocol if needed\n")
        
        print("💡 OR run everything at once:")
        print("   python main_controller.py --full\n")
        
        print("📊 Check status anytime:")
        print("   python monitoring/sales_tracker.py --mode dashboard\n")
        
        print("🚨 Emergency protocol:")
        print("   python monitoring/emergency.py --check\n")
        
        print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='72-Hour AI Cash System - Main Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--phase', type=int, choices=[1, 2, 3],
                       help='Run specific phase (1=Production, 2=Setup, 3=Automation)')
    parser.add_argument('--full', action='store_true',
                       help='Run complete workflow')
    parser.add_argument('--guide', action='store_true',
                       help='Show quick start guide')
    parser.add_argument('--simulate', action='store_true',
                       help='Simulation mode (faster, for testing)')
    
    args = parser.parse_args()
    
    controller = MainController(simulate=args.simulate)
    
    if args.guide:
        controller.quick_start()
    elif args.phase == 1:
        controller.phase_1_production()
    elif args.phase == 2:
        controller.phase_2_platform_setup()
    elif args.phase == 3:
        controller.phase_3_automation()
    elif args.full:
        controller.run_full_workflow()
    else:
        # Default: show guide
        controller.quick_start()

if __name__ == "__main__":
    main()