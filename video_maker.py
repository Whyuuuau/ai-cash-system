"""
AI Video Generator for 72-Hour Cash System
Creates short videos for TikTok/Instagram/YouTube Shorts
"""

import os
import random
import textwrap
import time
from datetime import datetime
from typing import List, Dict
import subprocess
import json

try:
    from moviepy.editor import *
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ moviepy not installed. Videos will be script-only.")

class VideoMaker:
    def __init__(self, config_file="video_config.json"):
        self.config = self.load_config(config_file)
        self.videos_created = []
        self.stats = {
            "total_videos": 0,
            "by_niche": {},
            "by_platform": {},
            "start_time": datetime.now().isoformat()
        }
        
        # Check dependencies
        self.check_dependencies()
    
    def load_config(self, config_file):
        """Load or create configuration"""
        
        default_config = {
            "output_dir": "videos",
            "formats": {
                "tiktok": {"width": 1080, "height": 1920, "duration": 60},
                "instagram": {"width": 1080, "height": 1350, "duration": 90},
                "youtube": {"width": 1920, "height": 1080, "duration": 60}
            },
            "platforms": ["tiktok", "instagram"],
            "niches": {
                "men_lust": "Alpha Male AI",
                "women_beauty": "AI Beauty System",
                "rich_time": "Time Billionaire",
                "parents_peace": "Peaceful Parenting AI",
                "kids_dreams": "DreamBuilder AI",
                "poor_hope": "Hope Economy"
            },
            "content": {
                "templates": [
                    "This AI tool changed everything for {niche}...",
                    "Stop doing {niche} manually. Use AI instead.",
                    "I automated my entire {niche} process. Here's how:",
                    "72 hours ago I had $0. Watch what happened with {niche}.",
                    "The secret AI trick for {niche} nobody talks about.",
                    "Why you're struggling with {niche} (and the AI solution).",
                    "From zero to hero in {niche} using only free AI tools.",
                    "The future of {niche} is automated. Get ready.",
                    "My {niche} system runs 24/7 without me. Here's the setup.",
                    "AI for {niche}: Beyond the basics."
                ],
                "hashtags": {
                    "men_lust": ["#DatingTips", "#SelfImprovement", "#AlphaMindset", "#AIDating"],
                    "women_beauty": ["#BeautyTips", "#AIBeauty", "#Skincare", "#MakeupAI"],
                    "rich_time": ["#Productivity", "#TimeManagement", "#AIProductivity", "#PassiveIncome"],
                    "parents_peace": ["#Parenting", "#AIParenting", "#FamilyLife", "#ParentingHacks"],
                    "kids_dreams": ["#Education", "#AIEducation", "#KidsLearning", "#EdTech"],
                    "poor_hope": ["#SideHustle", "#MakeMoneyOnline", "#AIIncome", "#FinancialFreedom"]
                }
            },
            "audio": {
                "use_background_music": True,
                "music_files": [],  # Add paths to royalty-free music
                "voiceover": {
                    "enabled": False,
                    "api_key": "",  # For ElevenLabs or similar
                    "voice_id": ""
                }
            },
            "automation": {
                "auto_upload": False,
                "schedule_posts": False,
                "videos_per_day": 5,
                "max_storage_gb": 10
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            os.makedirs(os.path.dirname(config_file) or '.', exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📁 Created config: {config_file}")
            return default_config
    
    def check_dependencies(self):
        """Check for required dependencies"""
        
        dependencies = {
            "ffmpeg": "ffmpeg -version",
            "imagemagick": "convert --version"
        }
        
        print("🔍 Checking dependencies...")
        
        for dep, check_cmd in dependencies.items():
            try:
                subprocess.run(check_cmd.split(), capture_output=True, check=True)
                print(f"  ✅ {dep}")
            except:
                print(f"  ⚠️ {dep} not found (some features may be limited)")
        
        if not MOVIEPY_AVAILABLE:
            print("  ⚠️ moviepy not installed - install with: pip install moviepy")
    
    def generate_script(self, niche, platform="tiktok"):
        """Generate video script"""
        
        niche_name = self.config["niches"].get(niche, niche.replace('_', ' '))
        template = random.choice(self.config["content"]["templates"])
        
        script = template.format(niche=niche_name)
        
        # Add details based on platform
        if platform == "tiktok":
            # Short, punchy scripts for TikTok
            scripts = [
                f"{script}\n\nStep 1: {self.get_step(1, niche)}\nStep 2: {self.get_step(2, niche)}\nStep 3: {self.get_step(3, niche)}\n\nResults: {self.get_result(niche)}",
                f"{script}\n\nThe AI Tool: {self.get_ai_tool(niche)}\nHow it works: {self.get_how_it_works(niche)}\nTime saved: {self.get_time_saved()}",
                f"{script}\n\nBefore AI: {self.get_before_state(niche)}\nAfter AI: {self.get_after_state(niche)}\nImplementation: {self.get_implementation_time()}",
                f"{script}\n\nCommon mistake: {self.get_common_mistake(niche)}\nAI solution: {self.get_ai_solution(niche)}\nYour action: {self.get_action_step()}"
            ]
            script = random.choice(scripts)
            
        elif platform == "youtube":
            # More detailed for YouTube
            scripts = [
                f"{script}\n\nIn this video, I'll show you exactly how I used AI to transform my {niche_name} process.\n\nWhat you'll learn:\n• {self.get_benefit(1, niche)}\n• {self.get_benefit(2, niche)}\n• {self.get_benefit(3, niche)}\n\nStay tuned to the end for a free resource!",
                f"{script}\n\nIf you're struggling with {niche_name}, this video is for you. I was in your shoes just {random.randint(1,4)} weeks ago.\n\nThe breakthrough came when I discovered these {random.randint(2,5)} AI tools...",
                f"{script}\n\nDocumenting my 72-hour challenge to automate {niche_name} completely.\n\nDay {random.randint(1,3)} progress:\n• Accomplished: {self.get_accomplishment(niche)}\n• Learned: {self.get_lesson_learned()}\n• Next: {self.get_next_step(niche)}"
            ]
            script = random.choice(scripts)
        
        # Add hashtags
        hashtag_list = self.config["content"]["hashtags"].get(niche, ["#AI", "#Automation", "#Tech"])
        hashtags = " ".join(hashtag_list[:5])
        
        script += f"\n\n{hashtags}"
        
        # Add CTA
        cta_options = [
            "\n\n👉 Full system in bio",
            "\n\n🔗 Link in description",
            "\n\n💬 Comment 'AI' for details",
            "\n\n📥 DM for free guide"
        ]
        
        if random.random() > 0.3:  # 70% chance of CTA
            script += random.choice(cta_options)
        
        return script
    
    def get_step(self, step_num, niche):
        """Get step description"""
        
        steps = {
            "men_lust": ["Analyze conversation patterns", "Generate personalized openers", "Automate follow-up messages"],
            "women_beauty": ["AI skin analysis", "Personalized routine generation", "Progress tracking"],
            "rich_time": ["Time audit with AI", "Automation identification", "System implementation"],
            "parents_peace": ["Behavior pattern recognition", "Activity suggestion generation", "Schedule optimization"],
            "kids_dreams": ["Interest assessment", "Content personalization", "Progress visualization"],
            "poor_hope": ["Skill gap analysis", "Micro-service identification", "Automated outreach"]
        }
        
        niche_steps = steps.get(niche, ["Research", "Implement", "Optimize"])
        return niche_steps[(step_num-1) % len(niche_steps)]
    
    def get_ai_tool(self, niche):
        """Get AI tool name"""
        
        tools = ["ChatGPT", "Bing AI", "Midjourney", "Canva AI", "Jasper", "Copy.ai", "Grammarly", "Otter.ai"]
        return random.choice(tools)
    
    def get_how_it_works(self, niche):
        """Get how it works description"""
        
        descriptions = [
            "analyzes patterns and generates optimized content",
            "learns from your preferences and adapts recommendations",
            "automates repetitive tasks 24/7",
            "provides data-driven insights and suggestions",
            "creates personalized solutions based on your goals"
        ]
        return random.choice(descriptions)
    
    def get_time_saved(self):
        """Get time saved"""
        
        return random.choice(["10+ hours/week", "5 hours daily", "20 hours monthly", "80% time reduction"])
    
    def get_before_state(self, niche):
        """Get before state"""
        
        states = ["manual work", "chaos", "inefficiency", "frustration", "overwhelm"]
        return random.choice(states)
    
    def get_after_state(self, niche):
        """Get after state"""
        
        states = ["automated", "streamlined", "profitable", "effortless", "scalable"]
        return random.choice(states)
    
    def get_implementation_time(self):
        """Get implementation time"""
        
        return random.choice(["24 hours", "3 days", "a weekend", "72 hours"])
    
    def get_common_mistake(self, niche):
        """Get common mistake"""
        
        mistakes = [
            "trying to do everything manually",
            "not leveraging available AI tools",
            "overcomplicating the process",
            "inconsistent implementation",
            "not measuring results"
        ]
        return random.choice(mistakes)
    
    def get_ai_solution(self, niche):
        """Get AI solution"""
        
        solutions = [
            "automates the heavy lifting",
            "provides consistent quality",
            "scales without additional effort",
            "learns and improves over time",
            "works 24/7 without breaks"
        ]
        return random.choice(solutions)
    
    def get_action_step(self):
        """Get action step"""
        
        actions = [
            "Pick one task to automate today",
            "Try one AI tool this week",
            "Document your current process",
            "Identify your biggest time waste",
            "Set up your first automation"
        ]
        return random.choice(actions)
    
    def get_benefit(self, benefit_num, niche):
        """Get benefit"""
        
        benefits = [
            "How to save 10+ hours per week",
            "The exact AI tools you need",
            "Step-by-step implementation guide",
            "Common pitfalls to avoid",
            "How to scale your results"
        ]
        return benefits[(benefit_num-1) % len(benefits)]
    
    def get_accomplishment(self, niche):
        """Get accomplishment"""
        
        accomplishments = [
            "built the automation framework",
            "created 50+ content pieces with AI",
            "set up the tracking system",
            "generated first $100",
            "automated customer onboarding"
        ]
        return random.choice(accomplishments)
    
    def get_lesson_learned(self):
        """Get lesson learned"""
        
        lessons = [
            "AI works best with human guidance",
            "Start simple, then expand",
            "Consistency beats perfection",
            "Automation requires upfront work",
            "Measure everything, optimize what matters"
        ]
        return random.choice(lessons)
    
    def get_next_step(self, niche):
        """Get next step"""
        
        steps = [
            "scale to 10x current volume",
            "add more automation layers",
            "create self-optimizing system",
            "document everything for others",
            "explore additional revenue streams"
        ]
        return random.choice(steps)
    
    def create_simple_video(self, script, platform="tiktok", niche="general"):
        """Create a simple video with text overlay"""
        
        if not MOVIEPY_AVAILABLE:
            print("⚠️ moviepy not available - creating script only")
            return self.save_script_only(script, platform, niche)
        
        try:
            # Get platform dimensions
            platform_config = self.config["formats"][platform]
            width = platform_config["width"]
            height = platform_config["height"]
            duration = platform_config["duration"]
            
            # Create output directory
            output_dir = self.config["output_dir"]
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/{niche}_{platform}_{timestamp}.mp4"
            
            # Create background (color or gradient)
            bg_color = random.choice([
                (25, 25, 40),    # Dark blue
                (40, 25, 40),    # Dark purple
                (25, 40, 40),    # Dark teal
                (40, 40, 25),    # Dark olive
                (30, 30, 30)     # Dark gray
            ])
            
            background = ColorClip(size=(width, height), color=bg_color, duration=duration)
            
            # Prepare text
            wrapped_text = textwrap.fill(script, width=40)
            text_lines = wrapped_text.split('\n')
            
            # Create text clips
            text_clips = []
            font_size = 36 if platform == "tiktok" else 48
            line_height = font_size * 1.2
            
            for i, line in enumerate(text_lines):
                txt_clip = TextClip(
                    line,
                    fontsize=font_size,
                    color='white',
                    font='Arial',
                    stroke_color='black',
                    stroke_width=1
                )
                
                # Position text (scroll effect)
                start_y = height + (i * line_height)
                end_y = -len(text_lines) * line_height
                
                txt_clip = txt_clip.set_position(('center', start_y))
                txt_clip = txt_clip.set_start(0)
                txt_clip = txt_clip.set_duration(duration)
                txt_clip = txt_clip.set_position(lambda t: ('center', start_y - (t/duration) * (start_y - end_y)))
                
                text_clips.append(txt_clip)
            
            # Composite video
            video = CompositeVideoClip([background] + text_clips)
            
            # Add simple animation or effects
            if random.random() > 0.5:
                # Fade in/out
                video = video.fadein(1).fadeout(1)
            
            # Add background music if available
            if self.config["audio"]["use_background_music"] and self.config["audio"]["music_files"]:
                try:
                    music_file = random.choice(self.config["audio"]["music_files"])
                    if os.path.exists(music_file):
                        audio = AudioFileClip(music_file).subclip(0, duration)
                        video = video.set_audio(audio)
                except:
                    pass
            
            # Write video file
            video.write_videofile(
                filename,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            print(f"✅ Video created: {filename}")
            
            # Update stats
            self.videos_created.append({
                "filename": filename,
                "niche": niche,
                "platform": platform,
                "script": script,
                "created": datetime.now().isoformat(),
                "size_mb": os.path.getsize(filename) / (1024*1024) if os.path.exists(filename) else 0
            })
            
            self.stats["total_videos"] += 1
            self.stats["by_niche"][niche] = self.stats["by_niche"].get(niche, 0) + 1
            self.stats["by_platform"][platform] = self.stats["by_platform"].get(platform, 0) + 1
            
            self.save_stats()
            return filename
            
        except Exception as e:
            print(f"❌ Video creation failed: {e}")
            return self.save_script_only(script, platform, niche)
    
    def save_script_only(self, script, platform, niche):
        """Save script as text file when video creation fails"""
        
        output_dir = self.config["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{niche}_{platform}_{timestamp}_script.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Platform: {platform}\n")
            f.write(f"Niche: {niche}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write("\n" + "="*50 + "\n")
            f.write(script)
        
        print(f"📝 Script saved: {filename}")
        return filename
    
    def save_stats(self):
        """Save statistics to file"""
        
        stats_file = "video_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        # Also save videos list
        videos_file = "videos_created.json"
        with open(videos_file, 'w') as f:
            json.dump(self.videos_created, f, indent=2)
    
    def generate_batch(self, count=5, platforms=None, niches=None):
        """Generate batch of videos"""
        
        if platforms is None:
            platforms = self.config["platforms"]
        
        if niches is None:
            niches = list(self.config["niches"].keys())
        
        print(f"🎬 Generating {count} videos...")
        print(f"   Platforms: {', '.join(platforms)}")
        print(f"   Niches: {', '.join(niches)}")
        
        created_files = []
        
        for i in range(count):
            platform = random.choice(platforms)
            niche = random.choice(niches)
            
            print(f"\n📹 Video {i+1}/{count}: {niche} for {platform}")
            
            script = self.generate_script(niche, platform)
            print(f"   Script: {script[:50]}...")
            
            video_file = self.create_simple_video(script, platform, niche)
            created_files.append(video_file)
            
            # Delay between videos
            if i < count - 1:
                delay = random.randint(5, 15)
                print(f"   ⏳ Waiting {delay} seconds...")
                time.sleep(delay)
        
        print(f"\n✅ Batch complete! Created {len(created_files)} videos.")
        self.show_stats()
        
        return created_files
    
    def show_stats(self):
        """Show current statistics"""
        
        print("\n📊 Video Creation Statistics:")
        print(f"   Total videos: {self.stats['total_videos']}")
        print(f"   By platform:")
        for platform, count in self.stats['by_platform'].items():
            print(f"     {platform}: {count}")
        print(f"   By niche:")
        for niche, count in self.stats['by_niche'].items():
            print(f"     {niche}: {count}")
        
        # Calculate total size
        total_size_mb = 0
        for video in self.videos_created:
            if "size_mb" in video:
                total_size_mb += video["size_mb"]
        
        print(f"   Total size: {total_size_mb:.1f} MB")
    
    def create_emergency_video(self):
        """Create emergency video for final push"""
        
        script = """🚨 EMERGENCY UPDATE: 72-HOUR CHALLENGE

I have less than 24 hours to reach $5000.

Current status: $[AMOUNT] raised
Still needed: $[NEEDED]

Every purchase helps me eat.
Every share gives me hope.

SPECIAL: All 6 AI systems for $47
(Originally $162)

Pay what you can afford.
Minimum $1.

Link in bio.
Time is running out. ⏰"""
        
        print("🎥 Creating emergency video...")
        return self.create_simple_video(script, "tiktok", "emergency")

# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Generator for 72-Hour Cash System")
    parser.add_argument("--mode", choices=["batch", "single", "stats", "emergency", "test"], 
                       default="batch", help="Run mode")
    parser.add_argument("--count", type=int, default=3, help="Number of videos to create")
    parser.add_argument("--platform", default="tiktok", help="Platform format")
    parser.add_argument("--niche", help="Specific niche")
    parser.add_argument("--config", default="video_config.json", help="Config file")
    
    args = parser.parse_args()
    
    maker = VideoMaker(args.config)
    
    if args.mode == "batch":
        niches = [args.niche] if args.niche else None
        platforms = [args.platform] if args.platform != "tiktok" else None
        
        maker.generate_batch(count=args.count, platforms=platforms, niches=niches)
        
    elif args.mode == "single":
        niche = args.niche or random.choice(list(maker.config["niches"].keys()))
        script = maker.generate_script(niche, args.platform)
        print(f"\n📝 Generated script for {niche} ({args.platform}):\n")
        print("-" * 50)
        print(script)
        print("-" * 50)
        
        create = input("\nCreate video? (y/n): ").lower().strip()
        if create == 'y':
            maker.create_simple_video(script, args.platform, niche)
        
    elif args.mode == "stats":
        maker.show_stats()
        
    elif args.mode == "emergency":
        maker.create_emergency_video()
        
    elif args.mode == "test":
        print("🧪 Test mode - Checking configuration:")
        print(f"   Output directory: {maker.config['output_dir']}")
        print(f"   Platforms configured: {', '.join(maker.config['platforms'])}")
        print(f"   Niches: {', '.join(maker.config['niches'].keys())}")
        print(f"   MoviePy available: {MOVIEPY_AVAILABLE}")
        
        # Test script generation
        test_niche = random.choice(list(maker.config["niches"].keys()))
        test_script = maker.generate_script(test_niche, "tiktok")
        print(f"\n📝 Sample script for {test_niche}:\n{test_script[:100]}...")