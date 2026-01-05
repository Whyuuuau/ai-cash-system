"""
Emergency Protocol System
Activates aggressive sales tactics when challenge is at risk
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from utils.logger import get_logger
from utils.helpers import get_time_remaining, format_currency

logger = get_logger("emergency")

class EmergencyProtocol:
    def __init__(self, sales_tracker, config=None):
        self.sales_tracker = sales_tracker
        self.config = config or {}
        self.activated = False
        self.activation_time = None
        self.measures_taken = []
        
        logger.info("Emergency protocol initialized")
    
    def should_activate(self):
        """Determine if emergency protocol should be activated"""
        status = self.sales_tracker.get_current_status()
        
        # Activate if less than 24 hours remaining
        if status['hours_remaining'] < 24 and not self.activated:
            if status['progress_percent'] < 80:
                return True, "Less than 24 hours and below 80% of target"
        
        # Activate if less than 12 hours and below 90%
        if status['hours_remaining'] < 12 and not self.activated:
            if status['progress_percent'] < 90:
                return True, "Critical: Less than 12 hours and below 90%"
        
        # Activate if less than 6 hours remaining
        if status['hours_remaining'] < 6 and not self.activated:
            return True, "Final push: Less than 6 hours remaining"
        
        return False, None
    
    def activate(self, reason="Manual activation"):
        """Activate emergency protocol"""
        if self.activated:
            logger.warning("Emergency protocol already activated")
            return
        
        self.activated = True
        self.activation_time = datetime.now()
        
        logger.critical(f"🚨 EMERGENCY PROTOCOL ACTIVATED: {reason}")
        
        print("\n" + "="*60)
        print("⚠️⚠️⚠️ EMERGENCY PROTOCOL ACTIVATED ⚠️⚠️⚠️")
        print("="*60)
        print(f"Reason: {reason}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nExecuting emergency measures...")
        print("="*60 + "\n")
        
        # Execute all emergency measures
        self.launch_sos_bundle()
        self.activate_pwyw_pricing()
        self.activate_affiliate_commissions()
        self.create_emergency_content()
        self.multi_platform_blast()
        
        logger.critical("All emergency measures executed")
    
    def launch_sos_bundle(self):
        """Launch SOS bundle at emergency pricing"""
        measure = {
            'name': 'SOS BUNDLE',
            'timestamp': datetime.now().isoformat(),
            'details': 'All 6 products for $47 (70% off)',
            'action': 'Update Gumroad product pricing'
        }
        
        print("📦 LAUNCHING 'SOS BUNDLE'")
        print("   • All 6 AI systems for $47 (normally $162)")
        print("   • 70% discount")
        print("   • Action Required: Update Gumroad pricing manually")
        print("   • URL: https://gumroad.com/products")
        print()
        
        self.measures_taken.append(measure)
        logger.info("SOS Bundle launched")
    
    def activate_pwyw_pricing(self):
        """Activate Pay What You Want pricing"""
        measure = {
            'name': 'PWYW PRICING',
            'timestamp': datetime.now().isoformat(),
            'details': 'Minimum $1, suggested $27',
            'action': 'Enable flexible pricing on all products'
        }
        
        print("💰 ACTIVATING PAY-WHAT-YOU-WANT PRICING")
        print("   • Minimum: $1")
        print("   • Suggested: $27")
        print("   • Message: 'Pay what you can afford'")
        print("   • Action Required: Update Gumroad to allow flexible pricing")
        print()
        
        self.measures_taken.append(measure)
        logger.info("PWYW pricing activated")
    
    def activate_affiliate_commissions(self):
        """Activate 100% affiliate commissions"""
        measure = {
            'name': 'AFFILIATE PROGRAM',
            'timestamp': datetime.now().isoformat(),
            'details': '100% commission on all sales',
            'action': 'Enable affiliate program with maximum commission'
        }
        
        print("🤝 ACTIVATING 100% AFFILIATE COMMISSIONS")
        print("   • Commission: 100% of sale price")
        print("   • Payment: Instant via PayPal")
        print("   • Message to share:")
        print("     'Help me survive! Get 100% commission on every sale.'")
        print("     'You make the sale, you keep all the money.'")
        print("   • Action Required: Set up Gumroad affiliate program")
        print()
        
        self.measures_taken.append(measure)
        logger.info("Affiliate program activated")
    
    def create_emergency_content(self):
        """Generate emergency content for all platforms"""
        status = self.sales_tracker.get_current_status()
        hours_left = int(status['hours_remaining'])
        current = format_currency(status['current_revenue'])
        needed = format_currency(status['remaining'])
        
        content = {
            'twitter': f"""🚨 EMERGENCY UPDATE: {hours_left} HOURS LEFT

Started with $0. Built 6 AI systems from scratch.

Current: {current}
Still need: {needed}

Every purchase helps me eat tonight.
Every share gives me hope.

All 6 systems: $47 (or pay what you can)
Minimum $1.

Link in bio. Time is running out. ⏰

#72HourChallenge #Emergency #HelpASideHustler""",
            
            'reddit': f"""Final {hours_left} hours of my 72-hour survival challenge - need your support

I started this challenge 72 hours ago with $0, no audience, just determination and AI tools.

The goal: Create 6 complete AI systems and make $5,000 in sales to prove anyone can do this.

**Current Status:**
- Revenue: {current} / $5,000
- Time left: {hours_left} hours
- What I built: 6 complete AI automation systems

**Why I'm posting this:**
I'm falling short. Every purchase directly helps me make rent this month.

**The Offer:**
- All 6 systems for $47 (normally $162)
- Or pay what you can afford (minimum $1)
- 30-day money-back guarantee
- You get real, working systems

**What you get:**
1. Alpha Male AI (attraction/dating)
2. AI Beauty System (skincare/style)
3. Time Billionaire (productivity)
4. Peaceful Parenting AI
5. DreamBuilder AI (kids education)
6. Hope Economy (income generation)

I'm not asking for donations. You get valuable products. But I'm being transparent - I need your help to cross the finish line.

[Product Link]

Thank you for reading.""",
            
            'telegram': f"""🆘 URGENT: {hours_left} HOURS REMAINING

This is it. The final push of my 72-hour challenge.

Current: {current}
Goal: $5,000
Time: {hours_left} hours

EMERGENCY OFFER:
✅ All 6 AI Systems: $47
✅ Pay What You Can: Minimum $1
✅ 100% Money-Back Guarantee

Every purchase helps me survive.
Every share gives me hope.

/products to see what's available

Thank you for being here. 🙏"""
        }
        
        measure = {
            'name': 'EMERGENCY CONTENT',
            'timestamp': datetime.now().isoformat(),
            'content': content,
             'action': 'Post to all platforms immediately'
        }
        
        print("📢 EMERGENCY CONTENT CREATED")
        print("\n--- TWITTER ---")
        print(content['twitter'])
        print("\n--- REDDIT ---")
        print(content['reddit'][:200] + "...")
        print("\n--- TELEGRAM ---")
        print(content['telegram'])
        print()
        
        # Save to file
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "emergency_content.txt", 'w', encoding='utf-8') as f:
            for platform, text in content.items():
                f.write(f"=== {platform.upper()} ===\n")
                f.write(text)
                f.write("\n\n")
        
        print(f"   • Content saved to: {output_dir / 'emergency_content.txt'}")
        print()
        
        self.measures_taken.append(measure)
        logger.info("Emergency content generated")
    
    def multi_platform_blast(self):
        """Coordinate multi-platform posting"""
        measure = {
            'name': 'MULTI-PLATFORM BLAST',
            'timestamp': datetime.now().isoformat(),
            'platforms': ['Twitter', 'Reddit', 'Telegram', 'Discord', 'Facebook'],
            'action': 'Post emergency content across all platforms'
        }
        
        print("🌐 MULTI-PLATFORM EMERGENCY BLAST")
        print("\n   Platforms to hit immediately:")
        print("   • Twitter/X: Post every 30 minutes")
        print("   • Reddit: Post to 10+ relevant subreddits")
        print("   • Telegram: Blast to channel + DM active users")
        print("   • Discord: Join relevant servers, share story")
        print("   • Facebook: Post in entrepreneurship groups")
        print("   • TikTok: Go LIVE if possible")
        print("   • YouTube: Community post update")
        print()
        print("   🎥 Consider:")
        print("   • Live stream the countdown")
        print("   • Record emotional video plea")
        print("   • Show the dashboard in real-time")
        print()
        
        self.measures_taken.append(measure)
        logger.info("Multi-platform blast coordinated")
    
    def get_status(self):
        """Get emergency protocol status"""
        return {
            'activated': self.activated,
            'activation_time': self.activation_time.isoformat() if self.activation_time else None,
            'measures_count': len(self.measures_taken),
            'measures': self.measures_taken
        }
    
    def print_final_instructions(self):
        """Print final manual steps"""
        print("\n" + "="*60)
        print("📋 MANUAL ACTIONS REQUIRED")
        print("="*60)
        print("\n1. GUMROAD PRICING:")
        print("   - Go to gumroad.com/products")
        print("   - Enable 'Pay What You Want' on all products")
        print("   - Set minimum: $1, suggested: $27")
        print("   - Create SOS Bundle at $47")
        print()
        print("2. AFFILIATE PROGRAM:")
        print("   - Enable Gumroad affiliate program")
        print("   - Set commission to 100%")
        print("   - Share affiliate link on all platforms")
        print()
        print("3. CONTENT POSTING:")
        print("   - Post emergency content (saved in data/output/)")
        print("   - Increase posting frequency")
        print("   - Engage with every comment/DM")
        print()
        print("4. LIVE UPDATES:")
        print("   - Consider going live on TikTok/YouTube")
        print("   - Show real-time dashboard")
        print("   - Be authentic and transparent")
        print()
        print("5. OUTREACH:")
        print("   - DM influencers in your niche")
        print("   - Ask for retweets/shares")
        print("   - Offer review copies")
        print()
        print("="*60 + "\n")

def main():
    import argparse
    from monitoring.sales_tracker import SalesTracker
    
    parser = argparse.ArgumentParser(description='Emergency Protocol System')
    parser.add_argument('--check', action='store_true', help='Check if activation needed')
    parser.add_argument('--activate', action='store_true', help='Force activation')
    parser.add_argument('--status', action='store_true', help='Show status')
    
    args = parser.parse_args()
    
    tracker = SalesTracker()
    protocol = EmergencyProtocol(tracker)
    
    if args.status:
        status = protocol.get_status()
        print(f"\nEmergency Protocol Status:")
        print(f"  Activated: {status['activated']}")
        if status['activated']:
            print(f"  Activation Time: {status['activation_time']}")
            print(f"  Measures Taken: {status['measures_count']}")
    
    elif args.check:
        should_activate, reason = protocol.should_activate()
        if should_activate:
            print(f"\n⚠️ EMERGENCY ACTIVATION RECOMMENDED")
            print(f"Reason: {reason}")
            print(f"\nRun with --activate to execute emergency protocol")
        else:
            print(f"\n✅ Emergency protocol not needed yet")
            tracker.print_dashboard()
    
    elif args.activate:
        protocol.activate("Manual activation via CLI")
        protocol.print_final_instructions()
    
    else:
        # Auto-check
        should_activate, reason = protocol.should_activate()
        if should_activate:
            print(f"\n⚠️ Auto-activating emergency protocol...")
            protocol.activate(reason)
            protocol.print_final_instructions()
        else:
            print("Emergency protocol not needed at this time")

if __name__ == "__main__":
    main()
