"""
AI Ebook Generator - 72 Hour Cash System
Generates 6 ebooks automatically using free AI
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import g4f  # Free GPT API
import json
import random
import time
from datetime import datetime

from utils.logger import get_logger
from utils.helpers import load_niches, sanitize_filename

logger = get_logger("ebook_generator")

class EbookGenerator:
    def __init__(self, niches_config=None, output_dir="data/output"):
        self.niches = niches_config or load_niches()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_files = []
        logger.info("EbookGenerator initialized with utils integration")
        
        # Keep original niches as fallback if load_niches fails
        if not self.niches:
            self.niches = {
            "men_lust": {
                "title": "Alpha Male AI: Psychology of Attraction Mastery",
                "chapters": [
                    "The Neuroscience of Attraction - Rewiring Your Brain",
                    "AI-Powered Dating Scripts That Actually Work", 
                    "Confidence Algorithms for Social Success",
                    "Social Proof Engineering in Digital Age",
                    "Body Language Decoded by Computer Vision",
                    "Voice Modulation AI for Magnetic Presence",
                    "Text Game Automation with ChatGPT",
                    "Lifestyle Design Through Data Analytics",
                    "Wealth Signaling in Social Media Era",
                    "The 72-Hour Charisma Transformation"
                ],
                "price": 27,
                "target": "Men aged 20-45 seeking dating success"
            },
            "women_beauty": {
                "title": "AI Beauty OS: Automated Glamour System",
                "chapters": [
                    "Skin Analysis AI - Beyond Human Eye",
                    "Automated Makeup Routine Generator",
                    "Fashion Algorithm for Your Body Type",
                    "Hair Style AI Recommender System",
                    "Nutrition Plan via Image Recognition",
                    "Workout Optimization with Motion AI",
                    "Confidence Protocol Through Self-Talk AI",
                    "Social Media Presence Enhancer",
                    "Beauty Product Recommender Engine",
                    "The 7-Day Digital Glow Up"
                ],
                "price": 27,
                "target": "Women seeking beauty enhancement through tech"
            },
            "rich_time": {
                "title": "Time Billionaire: AI-Powered Productivity System",
                "chapters": [
                    "Time Auditing AI - Find Your Hidden Hours",
                    "Automation Stack for Passive Income",
                    "Delegation Matrix to Virtual Assistants",
                    "Focus Optimization with Brainwave Tech",
                    "Email Management Through GPT",
                    "Meeting Efficiency Algorithm",
                    "Decision Fatigue Reduction System",
                    "Energy Management via Wearable Data",
                    "Wealth Acceleration Time Blocks",
                    "The 4-Hour AI Workweek Blueprint"
                ],
                "price": 47,
                "target": "Entrepreneurs and professionals"
            },
            "parents_peace": {
                "title": "Peaceful Parenting: AI Nanny System",
                "chapters": [
                    "Tantrum Predictor - AI Early Warning System",
                    "Educational Game Generator Based on Child's Interest",
                    "Routine Optimizer for Harmonious Home",
                    "Stress Management Through Biofeedback",
                    "Screen Time Balance Algorithm",
                    "Nutrition Planner for Picky Eaters",
                    "Sleep Pattern Analyzer and Optimizer",
                    "Educational Content Curator AI",
                    "Parent-Child Bonding Activity Generator",
                    "The Calm Home Operating System"
                ],
                "price": 27,
                "target": "Parents overwhelmed with daily chaos"
            },
            "kids_dreams": {
                "title": "DreamBuilder AI: Custom Adventure Creator",
                "chapters": [
                    "Personalized Story Generator Engine",
                    "Educational Game Maker for Any Subject",
                    "Creativity Engine - Infinite Art Ideas",
                    "Goal Visualizer with Progress Tracking",
                    "Career Explorer Through Role-Play AI",
                    "Social Skills Simulator for Shy Kids",
                    "Homework Helper with Step-by-Step AI",
                    "Hobby Recommender Based on Personality",
                    "Dream Journal with AI Interpretation",
                    "The Imagination Amplifier System"
                ],
                "price": 27,
                "target": "Children and parents seeking educational fun"
            },
            "poor_hope": {
                "title": "Hope Economy: $0 to $5000 in 72 Hours",
                "chapters": [
                    "Mindset Reset - From Scarcity to Abundance",
                    "Skill Stacking for Maximum Market Value",
                    "Micro-Service AI - Small Tasks, Big Money",
                    "Profit Multiplication Through Automation",
                    "Digital Product Creation in 24 Hours",
                    "Social Proof Generation Algorithm",
                    "Client Acquisition Funnel AI",
                    "Pricing Psychology for Maximum Yield",
                    "Scaling Systems Without Investment",
                    "The Escape Velocity Financial Plan"
                ],
                "price": 27,
                "target": "People in financial distress seeking hope"
            }
        }
    
    def generate_chapter_content(self, niche, chapter_title, word_count=1500):
        """Generate chapter content using free GPT API"""
        
        prompt = f"""Write a detailed chapter about "{chapter_title}" for an ebook titled "{self.niches[niche]['title']}".
        
        Requirements:
        1. Make it practical and actionable
        2. Include step-by-step instructions
        3. Mention specific FREE AI tools (ChatGPT, Bing AI, Canva, etc.)
        4. Include real examples and case studies
        5. Write in engaging, conversational tone
        6. Target audience: {self.niches[niche]['target']}
        7. Word count: Approximately {word_count} words
        8. Include actionable takeaways at the end
        
        Structure:
        - Problem identification
        - Solution overview  
        - Step-by-step implementation
        - Tools and resources (free only)
        - Common pitfalls to avoid
        - Success metrics
        - Action plan
        
        Make it valuable enough that someone would pay $27 for this information."""
        
        try:
            # Using g4f for free GPT access
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Fallback content
            return f"# {chapter_title}\n\nThis chapter covers {chapter_title} in detail. Due to API limits, content generation is simplified. In the full version, this would include step-by-step instructions, AI tools, and practical examples."
    
    def create_ebook_markdown(self, niche):
        """Create complete ebook in markdown format"""
        
        details = self.niches[niche]
        content = f"# {details['title']}\n\n"
        content += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        content += "## Table of Contents\n\n"
        
        # Add table of contents
        for i, chapter in enumerate(details['chapters'], 1):
            content += f"{i}. {chapter}\n"
        
        content += "\n---\n\n"
        
        # Generate each chapter
        for i, chapter in enumerate(details['chapters'], 1):
            logger.info(f"Generating chapter {i}/{len(details['chapters'])}: {chapter}")
            
            chapter_content = self.generate_chapter_content(niche, chapter)
            content += f"# Chapter {i}: {chapter}\n\n{chapter_content}\n\n"
            
            # Add page break
            content += "\\newpage\n\n" if i < len(details['chapters']) else ""
            
            # Delay to avoid rate limiting
            time.sleep(2)
        
        # Add conclusion
        content += "# Conclusion\n\n"
        content += "This ebook was created using AI as part of a 72-hour survival challenge. "
        content += "Every purchase supports this experimental project to prove that with just a laptop and AI, "
        content += "anyone can create value from nothing.\n\n"
        content += "**Next Steps:**\n"
        content += "1. Implement one chapter immediately\n"
        content += "2. Join our free Telegram group for updates\n"
        content += "3. Share your results for community support\n"
        
        return content
    
    def save_ebook(self, niche, content):
        """Save ebook to file"""
        
        filename = f"{sanitize_filename(niche)}_ebook.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_files.append(str(filepath))
        logger.success(f"Saved: {filepath}")
        return str(filepath)
    
    def generate_all(self):
        """Generate all 6 ebooks"""
        
        logger.info("Starting Ebook Generation...")
        logger.info(f"Total niches: {len(self.niches)}")
        print("=" * 50)
        
        for niche in self.niches.keys():
            logger.info(f"Generating: {self.niches[niche]['title']}")
            logger.info(f"Chapters: {len(self.niches[niche]['chapters'])}")
            logger.info(f"Target: {self.niches[niche]['target']}")
            
            content = self.create_ebook_markdown(niche)
            self.save_ebook(niche, content)
            
            logger.success(f"Completed: {self.niches[niche]['title']}")
            logger.info("Waiting before next ebook...")
            time.sleep(5)
        
        print("\n" + "=" * 50)
        logger.success("ALL EBOOKS GENERATED SUCCESSFULLY!")
        logger.info(f"Total files: {len(self.generated_files)}")
        
        # Create summary file
        self.create_summary()
        
        return self.generated_files
    
    def create_summary(self):
        """Create summary of all generated ebooks"""
        
        summary = "# 72-Hour AI Cash System - Ebook Summary\n\n"
        summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for niche, details in self.niches.items():
            summary += f"## {details['title']}\n"
            summary += f"**Price:** ${details['price']}\n"
            summary += f"**Target:** {details['target']}\n"
            summary += f"**Chapters:** {len(details['chapters'])}\n"
            summary += f"**File:** {niche}_ebook.md\n\n"
        
        summary += "## Usage Instructions\n"
        summary += "1. Convert markdown to PDF using pandoc or online converter\n"
        summary += "2. Upload to Gumroad/Carrd\n"
        summary += "3. Use social_automation.py to promote\n"
        summary += "4. Monitor sales with main_controller.py\n"
        
        summary_file = self.output_dir / "ebook_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Summary created: {summary_file}")
    
    def get_stats(self):
        """Get statistics about generated content"""
        
        total_chapters = sum(len(details['chapters']) for details in self.niches.values())
        total_words_estimate = total_chapters * 1500  # Approximate
        
        return {
            "total_ebooks": len(self.niches),
            "total_chapters": total_chapters,
            "estimated_words": total_words_estimate,
            "generated_files": self.generated_files
        }

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("AI EBOOK GENERATOR - 72 HOUR CASH SYSTEM")
    print("=" * 60)
    
    generator = EbookGenerator()
    
    # Ask which niches to generate
    print("\nAvailable niches:")
    for i, niche in enumerate(generator.niches.keys(), 1):
        print(f"{i}. {generator.niches[niche]['title']}")
    
    print("\nOptions:")
    print("1. Generate ALL ebooks")
    print("2. Generate specific niches")
    print("3. Test mode (generate 1 chapter each)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        files = generator.generate_all()
        stats = generator.get_stats()
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total ebooks: {stats['total_ebooks']}")
        print(f"   Total chapters: {stats['total_chapters']}")
        print(f"   Estimated words: {stats['estimated_words']:,}")
        
    elif choice == "2":
        print("\nEnter niche numbers (comma-separated):")
        for i, niche in enumerate(generator.niches.keys(), 1):
            print(f"{i}. {niche}")
        
        selected = input("> ").strip().split(',')
        niches_to_generate = []
        
        for num in selected:
            try:
                idx = int(num.strip()) - 1
                niche = list(generator.niches.keys())[idx]
                niches_to_generate.append(niche)
            except:
                pass
        
        print(f"\nGenerating: {', '.join(niches_to_generate)}")
        
        for niche in niches_to_generate:
            content = generator.create_ebook_markdown(niche)
            generator.save_ebook(niche, content)
        
    elif choice == "3":
        print("\n🧪 TEST MODE: Generating 1 chapter per ebook")
        
        for niche in generator.niches.keys():
            logger.info(f"Testing: {generator.niches[niche]['title']}")
            test_content = generator.generate_chapter_content(
                niche, 
                generator.niches[niche]['chapters'][0],
                word_count=300
            )
            logger.info(f"Generated: {len(test_content)} characters")
            time.sleep(1)
    
    print("\n✨ Process completed! Check the generated .md files.")