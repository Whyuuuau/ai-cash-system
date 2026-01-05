"""
Sales Tracking and Monitoring System
Real-time tracking of sales progress toward $5000 goal
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
from utils.logger import get_logger
from utils.helpers import load_config, get_time_remaining, format_currency, calculate_progress

logger = get_logger("sales_tracker")

class SalesTracker:
    def __init__(self, start_time=None, target=5000, duration_hours=72):
        self.start_time = start_time or datetime.now()
        self.target = target
        self.duration_hours = duration_hours
        self.deadline = self.start_time + timedelta(hours=duration_hours)
        
        self.sales = []
        self.analytics = {
            'total_revenue': 0,
            'total_sales': 0,
            'by_product': {},
            'hourly_breakdown': {},
            'conversion_events': []
        }
        
        self.load_data()
        logger.info(f"Sales tracker initialized - Target: {format_currency(target)}")
    
    def load_data(self):
        """Load existing sales data"""
        data_file = Path("data/analytics/sales_data.json")
        
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
                self.sales = data.get('sales', [])
                self.analytics = data.get('analytics', self.analytics)
            logger.info(f"Loaded {len(self.sales)} existing sales")
    
    def save_data(self):
        """Save sales data"""
        data_file = Path("data/analytics/sales_data.json")
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'sales': self.sales,
            'analytics': self.analytics,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_sale(self, product, amount, source='manual'):
        """Record a new sale"""
        sale = {
            'timestamp': datetime.now().isoformat(),
            'product': product,
            'amount': amount,
            'source': source,
            'hours_elapsed': (datetime.now() - self.start_time).total_seconds() / 3600
        }
        
        self.sales.append(sale)
        
        # Update analytics
        self.analytics['total_revenue'] += amount
        self.analytics['total_sales'] += 1
        
        if product not in self.analytics['by_product']:
            self.analytics['by_product'][product] = {'count': 0, 'revenue': 0}
        
        self.analytics['by_product'][product]['count'] += 1
        self.analytics['by_product'][product]['revenue'] += amount
        
        self.save_data()
        
        logger.success(f"Sale recorded: {product} - {format_currency(amount)}")
        return sale
    
    def get_current_status(self):
        """Get current challenge status"""
        time_info = get_time_remaining(self.start_time, self.duration_hours)
        
        revenue = self.analytics['total_revenue']
        progress = calculate_progress(revenue, self.target)
        remaining = self.target - revenue
        
        status = {
            'current_revenue': revenue,
            'target': self.target,
            'remaining': remaining,
            'progress_percent': progress,
            'total_sales': self.analytics['total_sales'],
            'hours_elapsed': (datetime.now() - self.start_time).total_seconds() / 3600,
            'hours_remaining': time_info['remaining_hours'],
            'deadline': time_info['deadline'].isoformat(),
            'is_expired': time_info['is_expired']
        }
        
        # Calculate required rate
        if time_info['remaining_hours'] > 0 and remaining > 0:
            status['required_per_hour'] = remaining / time_info['remaining_hours']
        else:
            status['required_per_hour'] = 0
        
        # Calculate current rate
        if status['hours_elapsed'] > 0:
            status['current_per_hour'] = revenue / status['hours_elapsed']
        else:
            status['current_per_hour'] = 0
        
        return status
    
    def print_dashboard(self):
        """Print formatted dashboard"""
        status = self.get_current_status()
        
        print("\n" + "="*60)
        print("🎯 72-HOUR SURVIVAL DASHBOARD")
        print("="*60)
        print(f"⏰ Time Elapsed: {status['hours_elapsed']:.1f} / {self.duration_hours} hours")
        print(f"⏳ Time Remaining: {status['hours_remaining']:.1f} hours")
        print(f"")
        print(f"💰 Revenue: {format_currency(status['current_revenue'])}")
        print(f"🎯 Target: {format_currency(status['target'])}")
        print(f"📊 Progress: {status['progress_percent']:.1f}%")
        print(f"📉 Remaining: {format_currency(status['remaining'])}")
        print(f"")
        print(f"🛒 Total Sales: {status['total_sales']}")
        print(f"📈 Current Rate: {format_currency(status['current_per_hour'])}/hour")
        
        if status['remaining'] > 0 and not status['is_expired']:
            print(f"⚡ Required Rate: {format_currency(status['required_per_hour'])}/hour")
            
            # Performance indicator
            if status['current_per_hour'] >= status['required_per_hour']:
                print(f"✅ ON TRACK")
            else:
                print(f"⚠️  BEHIND TARGET")
        elif status['is_expired']:
            print(f"⏰ CHALLENGE ENDED")
            if status['current_revenue'] >= status['target']:
                print(f"🎉 TARGET ACHIEVED!")
            else:
                print(f"📊 Final Result: {status['progress_percent']:.1f}% of target")
        else:
            print(f"🎉 TARGET ACHIEVED!")
        
        print("\n" + "="*60)
        
        # Top products
        if self.analytics['by_product']:
            print("\n📦 SALES BY PRODUCT:")
            sorted_products = sorted(
                self.analytics['by_product'].items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )
            for product, data in sorted_products[:5]:
                print(f"  • {product}: {data['count']} sales - {format_currency(data['revenue'])}")
        
        print("\n")
        
        return status
    
    def simulate_sale(self):
        """Simulate a sale for testing"""
        import random
        
        products = [
            ('men_lust', 27),
            ('women_beauty', 27),
            ('rich_time', 27),
            ('parents_peace', 27),
            ('kids_dreams', 27),
            ('poor_hope', 27),
            ('bundle', 97)
        ]
        
        product, price = random.choice(products)
        return self.add_sale(product, price, source='simulated')
    
    def run_monitoring_loop(self, check_interval_hours=1):
        """Run continuous monitoring"""
        logger.info("Starting monitoring loop...")
        
        try:
            while datetime.now() < self.deadline:
                self.print_dashboard()
                
                # Check if we need emergency measures
                status = self.get_current_status()
                if status['hours_remaining'] < 24 and status['progress_percent'] < 50:
                    logger.warning("⚠️ EMERGENCY: Less than 24 hours and below 50% of target!")
                
                # Wait for next check
                time.sleep(check_interval_hours * 3600)
            
            # Final status
            print("\n\n🏁 CHALLENGE COMPLETE!")
            self.print_dashboard()
            
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
            self.print_dashboard()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sales Tracker for 72-Hour Challenge')
    parser.add_argument('--mode', choices=['dashboard', 'monitor', 'add-sale', 'simulate'], 
                       default='dashboard', help='Run mode')
    parser.add_argument('--product', help='Product name for add-sale mode')
    parser.add_argument('--amount', type=float, help='Sale amount for add-sale mode')
    parser.add_argument('--interval', type=float, default=1.0, help='Check interval in hours')
    
    args = parser.parse_args()
    
    tracker = SalesTracker()
    
    if args.mode == 'dashboard':
        tracker.print_dashboard()
    
    elif args.mode == 'monitor':
        tracker.run_monitoring_loop(check_interval_hours=args.interval)
    
    elif args.mode == 'add-sale':
        if not args.product or not args.amount:
            print("❌ Please provide --product and --amount")
            return
        tracker.add_sale(args.product, args.amount, source='manual')
        tracker.print_dashboard()
    
    elif args.mode == 'simulate':
        print("🎲 Simulating sale...")
        tracker.simulate_sale()
        tracker.print_dashboard()

if __name__ == "__main__":
    main()
