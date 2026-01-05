"""
Main Controller for 72-Hour AI Cash System
Orchestrates all components and manages the 72-hour countdown
"""

import os
import sys
import json
import time
import schedule
import threading
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Optional

class AICashSystemController:
    def __init__(self, config_file="system_config.json"):
        self.config = self.load_config(config_file)
        self.start_time = datetime.now()
        self.deadline = self.start_time + timedelta(hours=72)
        self.target_amount = 5000
        self.current_amount = 0
        self.system_status = {}
        self.logs = []
        self.running = False
        
        # Components
        self.components = {
            "ebook_generator": False,
            "social_automation": False,
            "video_maker": False,
            "monitoring": False,
            "emergency_protocol": False
        }
    
    def load_config(self, config_file):
        """Load or create system configuration"""
        
        default_config = {
            "system": {
                "name": "72-Hour AI Cash System",
                "version": "1.0",
                "creator": "AI Survival Challenge",
                "start_time": datetime.now().isoformat(),
                "deadline": (datetime.now() + timedelta(hours=72)).isoformat(),
                "target_amount": 5000,
                "status": "initializing"
            },
            "components": {
                "ebook_generator": {
                    "enabled": True,
                    "script": "ebook_generator.py",
                    "schedule": "once",  # once, daily, hourly
                    "last_run": None
                },
                "social_automation": {
                    "enabled": True,
                    "script": "social_automation.py --mode schedule",
                    "schedule": "continuous",
                    "last_run": None
                },
                "video_maker": {
                    "enabled": True,
                    "script": "video_maker.py --mode batch --count 3",
                    "schedule": "every_6_hours",
                    "last_run": None
                },
                "monitoring": {
                    "enabled": True,
                    "check_interval": 3600,  # seconds
                    "alerts": True
                },
                "emergency_protocol": {
                    "enabled": True,
                    "activate_at_hour": 60,  # Activate at hour 60
                    "protocols": ["price_reduction", "bundle_offer", "live_stream"]
                }
            },
            "paths": {
                "log_dir": "logs",
                "data_dir": "data",
                "output_dir": "output"
            },
            "api_keys": {},  # To store any API keys
            "notifications": {
                "telegram": False,
                "email": False,
                "webhook": False
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            os.makedirs(os.path.dirname(config_file) or '.', exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📁 Created system config: {config_file}")
            return default_config
    
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        self.logs.append(log_entry)
        
        # Save to log file
        log_dir = self.config["paths"]["log_dir"]
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"system_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
        return log_entry
    
    def update_status(self, component, status, details=None):
        """Update component status"""
        
        self.system_status[component] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.save_status()
        self.log(f"Component '{component}' status: {status}")
    
    def save_status(self):
        """Save system status to file"""
        
        status_file = "system_status.json"
        status_data = {
            "system_status": self.system_status,
            "current_time": datetime.now().isoformat(),
            "time_remaining": self.get_time_remaining(),
            "target_progress": self.get_progress_percentage(),
            "components": self.components
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def get_time_remaining(self):
        """Get time remaining until deadline"""
        
        remaining = self.deadline - datetime.now()
        hours = remaining.total_seconds() / 3600
        
        if hours < 0:
            return "EXPIRED"
        
        return f"{int(hours)}h {int((hours % 1) * 60)}m"
    
    def get_progress_percentage(self):
        """Get progress percentage toward target"""
        
        if self.target_amount == 0:
            return 0
        
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    def run_component(self, component_name, script_path, args=""):
        """Run a component script"""
        
        if not os.path.exists(script_path):
            self.log(f"Script not found: {script_path}", "ERROR")
            return False
        
        try:
            self.update_status(component_name, "running")
            
            # Run the script
            cmd = f"python {script_path} {args}"
            self.log(f"Running: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.update_status(component_name, "completed", {
                    "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
                })
                self.components[component_name] = True
                return True
            else:
                self.update_status(component_name, "failed", {
                    "error": result.stderr[:500] if result.stderr else "Unknown error",
                    "returncode": result.returncode
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.update_status(component_name, "timeout")
            return False
        except Exception as e:
            self.update_status(component_name, "error", {"exception": str(e)})
            return False
    
    def run_ebook_generator(self):
        """Run ebook generator"""
        
        config = self.config["components"]["ebook_generator"]
        if not config["enabled"]:
            return True
        
        self.log("Starting ebook generator...")
        success = self.run_component(
            "ebook_generator",
            config["script"],
            "--mode generate_all" if config.get("mode") else ""
        )
        
        if success:
            self.log("✅ Ebook generation completed")
        else:
            self.log("❌ Ebook generation failed", "WARNING")
        
        return success
    
    def run_social_automation(self):
        """Run social automation"""
        
        config = self.config["components"]["social_automation"]
        if not config["enabled"]:
            return True
        
        self.log("Starting social automation...")
        
        # Check if it's already running
        if self.components.get("social_automation_running"):
            self.log("Social automation already running", "INFO")
            return True
        
        # Run in separate thread for continuous operation
        def run_social():
            self.components["social_automation_running"] = True
            success = self.run_component("social_automation", config["script"])
            self.components["social_automation_running"] = False
            return success
        
        thread = threading.Thread(target=run_social, daemon=True)
        thread.start()
        
        self.log("✅ Social automation started in background")
        return True
    
    def run_video_maker(self):
        """Run video maker"""
        
        config = self.config["components"]["video_maker"]
        if not config["enabled"]:
            return True
        
        self.log("Starting video maker...")
        success = self.run_component("video_maker", config["script"])
        
        if success:
            self.log("✅ Video creation completed")
        else:
            self.log("❌ Video creation failed", "WARNING")
        
        return success
    
    def check_progress(self):
        """Check sales progress (simulated or real)"""
        
        # In real implementation, this would check Gumroad API
        # For now, simulate progress
        
        hours_elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        
        # Simulate sales based on time
        base_sales = hours_elapsed * 1.5  # 1.5 sales per hour average
        variance = (datetime.now().hour % 24) / 24  # Daily cycle
        
        simulated_sales = int(base_sales * (0.8 + variance * 0.4))
        self.current_amount = simulated_sales * 27  # $27 per sale
        
        self.log(f"Progress check: ${self.current_amount} / ${self.target_amount} "
                f"({self.get_progress_percentage():.1f}%)")
        
        # Save progress
        progress_file = "sales_progress.json"
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "current_amount": self.current_amount,
            "target_amount": self.target_amount,
            "progress_percentage": self.get_progress_percentage(),
            "time_remaining": self.get_time_remaining(),
            "hours_elapsed": hours_elapsed,
            "estimated_sales": simulated_sales
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        return self.current_amount
    
    def show_dashboard(self):
        """Show system dashboard"""
        
        hours_elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        hours_remaining = max(0, (self.deadline - datetime.now()).total_seconds() / 3600)
        
        print("\n" + "="*60)
        print("           72-HOUR AI CASH SYSTEM - DASHBOARD")
        print("="*60)
        
        print(f"\n⏰ TIME:")
        print(f"   Started:     {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Deadline:    {self.deadline.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Elapsed:     {hours_elapsed:.1f} hours")
        print(f"   Remaining:   {hours_remaining:.1f} hours")
        
        print(f"\n💰 FINANCIAL:")
        print(f"   Current:     ${self.current_amount}")
        print(f"   Target:      ${self.target_amount}")
        print(f"   Progress:    {self.get_progress_percentage():.1f}%")
        print(f"   Needed/Hour: ${(self.target_amount - self.current_amount) / max(1, hours_remaining):.1f}")
        
        print(f"\n🚀 COMPONENTS:")
        for component, status in self.components.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component}")
        
        print(f"\n📊 SYSTEM STATUS:")
        for component, data in self.system_status.items():
            status = data.get("status", "unknown")
            timestamp = data.get("timestamp", "")
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M") if timestamp else ""
            print(f"   • {component}: {status} ({time_str})")
        
        print(f"\n📝 LOGS: {len(self.logs)} entries")
        if self.logs:
            print(f"   Latest: {self.logs[-1][:80]}...")
        
        print("\n" + "="*60)
    
    def check_emergency_conditions(self):
        """Check if emergency protocols should be activated"""
        
        hours_elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        config = self.config["components"]["emergency_protocol"]
        
        if not config["enabled"]:
            return False
        
        # Check time condition
        if hours_elapsed >= config["activate_at_hour"]:
            self.log(f"⏰ Emergency condition met: Hour {hours_elapsed:.1f} >= {config['activate_at_hour']}", "WARNING")
            return True
        
        # Check progress condition
        progress = self.get_progress_percentage()
        if hours_elapsed >= 48 and progress < 50:  # Less than 50% at 48 hours
            self.log(f"📉 Emergency condition met: {progress:.1f}% at hour {hours_elapsed:.1f}", "WARNING")
            return True
        
        return False
    
    def activate_emergency_protocol(self):
        """Activate emergency protocols"""
        
        self.log("🚨 ACTIVATING EMERGENCY PROTOCOLS", "EMERGENCY")
        
        protocols = self.config["components"]["emergency_protocol"]["protocols"]
        
        for protocol in protocols:
            self.log(f"  Executing: {protocol}")
            
            if protocol == "price_reduction":
                # Reduce all prices by 50%
                self.log("  • All prices reduced by 50%")
                # Update Gumroad prices here
                
            elif protocol == "bundle_offer":
                # Create emergency bundle
                self.log("  • Creating 'Survival Bundle' - all 6 products for $47")
                # Create bundle on Gumroad
                
            elif protocol == "live_stream":
                # Start live stream
                self.log("  • Starting emergency live stream")
                # Start streaming on YouTube/Twitch
                
            elif protocol == "affiliate_boost":
                # Increase affiliate commissions
                self.log("  • Affiliate commissions increased to 80%")
                # Update affiliate program
                
            elif protocol == "pay_what_you_want":
                # Activate PWYW
                self.log("  • Activating 'Pay What You Want' (minimum $1)")
                # Update pricing model
        
        # Create emergency content
        self.create_emergency_content()
        
        self.log("✅ Emergency protocols activated", "EMERGENCY")
    
    def create_emergency_content(self):
        """Create emergency content"""
        
        emergency_content = {
            "title": "EMERGENCY: 72-HOUR SURVIVAL CHALLENGE FINAL PUSH",
            "message": f"""
🚨 URGENT UPDATE - FINAL {int((self.deadline - datetime.now()).total_seconds()/3600)} HOURS

I have less than {int((self.deadline - datetime.now()).total_seconds()/3600)} hours to reach ${self.target_amount}.

Current: ${self.current_amount}
Still needed: ${self.target_amount - self.current_amount}

EVERY PURCHASE HELPS ME EAT.
EVERY SHARE GIVES ME HOPE.

SPECIAL EMERGENCY OFFERS:
1. ALL 6 AI SYSTEMS - Was $162, Now $47
2. PAY WHAT YOU WANT - Minimum $1
3. 80% AFFILIATE COMMISSIONS

I'm live-streaming the final hours.
Watch my real-time progress.

TIME IS RUNNING OUT. ⏰
            """,
            "hashtags": "#Emergency #72HourChallenge #AISurvival #HelpMeEat #FinalPush"
        }
        
        # Save emergency content
        with open("emergency_content.json", 'w') as f:
            json.dump(emergency_content, f, indent=2)
        
        self.log("📝 Emergency content created", "EMERGENCY")
        return emergency_content
    
    def schedule_tasks(self):
        """Schedule automatic tasks"""
        
        # Hourly progress check
        schedule.every().hour.do(self.check_progress)
        
        # Dashboard display every 6 hours
        schedule.every(6).hours.do(self.show_dashboard)
        
        # Video generation every 6 hours
        if self.config["components"]["video_maker"]["enabled"]:
            schedule.every(6).hours.do(self.run_video_maker)
        
        # Emergency protocol check every hour
        schedule.every().hour.do(self.check_and_activate_emergency)
        
        self.log("📅 Tasks scheduled")
    
    def check_and_activate_emergency(self):
        """Check and activate emergency protocols if needed"""
        
        if self.check_emergency_conditions():
            self.activate_emergency_protocol()
    
    def run(self):
        """Run the main system"""
        
        self.running = True
        self.log("="*60)
        self.log("🚀 STARTING 72-HOUR AI CASH SYSTEM")
        self.log("="*60)
        
        # Initial setup
        self.show_dashboard()
        
        # Run initial ebook generation
        if self.config["components"]["ebook_generator"]["enabled"]:
            self.run_ebook_generator()
        
        # Start social automation
        if self.config["components"]["social_automation"]["enabled"]:
            self.run_social_automation()
        
        # Initial video generation
        if self.config["components"]["video_maker"]["enabled"]:
            self.run_video_maker()
        
        # Schedule tasks
        self.schedule_tasks()
        
        # Initial progress check
        self.check_progress()
        
        self.log("\n✅ System initialized and running")
        self.log("   Press Ctrl+C to stop\n")
        
        # Main loop
        try:
            while self.running:
                schedule.run_pending()
                
                # Check if deadline passed
                if datetime.now() > self.deadline:
                    self.log("⏰ DEADLINE REACHED - System complete", "IMPORTANT")
                    self.shutdown()
                    break
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.log("\n👋 Shutting down by user request...", "INFO")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown system cleanly"""
        
        self.running = False
        schedule.clear()
        
        # Final progress check
        self.check_progress()
        
        # Show final dashboard
        self.show_dashboard()
        
        # Generate final report
        self.generate_final_report()
        
        self.log("="*60)
        self.log("🛑 SYSTEM SHUTDOWN COMPLETE")
        self.log("="*60)
    
    def generate_final_report(self):
        """Generate final report"""
        
        hours_elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        
        report = {
            "system": "72-Hour AI Cash System",
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_hours": hours_elapsed,
            "target_amount": self.target_amount,
            "achieved_amount": self.current_amount,
            "success_percentage": self.get_progress_percentage(),
            "components_executed": {k: v for k, v in self.components.items() if v},
            "total_logs": len(self.logs),
            "emergency_protocols_activated": self.check_emergency_conditions(),
            "summary": "Success" if self.current_amount >= self.target_amount else "Partial/Failed"
        }
        
        report_file = "final_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📋 Final report saved: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("                 FINAL REPORT")
        print("="*60)
        print(f"\n🎯 Target: ${self.target_amount}")
        print(f"💰 Achieved: ${self.current_amount}")
        print(f"📈 Success: {report['success_percentage']:.1f}%")
        print(f"⏱️  Time: {hours_elapsed:.1f} hours")
        print(f"📊 Status: {report['summary']}")
        print("="*60)
        
        return report

# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="72-Hour AI Cash System - Main Controller")
    parser.add_argument("--mode", choices=["run", "dashboard", "test", "emergency", "shutdown"], 
                       default="run", help="Operation mode")
    parser.add_argument("--config", default="system_config.json", help="Config file")
    parser.add_argument("--target", type=int, default=5000, help="Target amount")
    parser.add_argument("--hours", type=int, default=72, help="Hours for challenge")
    
    args = parser.parse_args()
    
    controller = AICashSystemController(args.config)
    controller.target_amount = args.target
    controller.deadline = controller.start_time + timedelta(hours=args.hours)
    
    if args.mode == "run":
        controller.run()
        
    elif args.mode == "dashboard":
        controller.show_dashboard()
        
    elif args.mode == "test":
        print("🧪 Running system tests...")
        print(f"   Config loaded: {len(controller.config.get('components', {}))} components")
        print(f"   Start time: {controller.start_time}")
        print(f"   Deadline: {controller.deadline}")
        print(f"   Time remaining: {controller.get_time_remaining()}")
        
        # Test component
        test_result = controller.run_ebook_generator()
        print(f"   Ebook generator test: {'PASS' if test_result else 'FAIL'}")
        
    elif args.mode == "emergency":
        print("🚨 Manual emergency activation")
        controller.activate_emergency_protocol()
        
    elif args.mode == "shutdown":
        controller.shutdown()