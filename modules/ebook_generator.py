"""
AI Ebook Generator - 72 Hour Cash System
Generates 6 ebooks automatically using free AI
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.open_router import OpenRouter
from modules.open_router import OpenRouter
from modules.pdf_converter import PDFConverter
from modules.image_generator import ImageGenerator
import argparse
import json
import random
import time
from datetime import datetime

from utils.logger import get_logger
from utils.helpers import load_niches, sanitize_filename

logger = get_logger("ebook_generator")

class EbookGenerator:
    def __init__(self, niches_config=None, output_dir="data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_files = []
        logger.info("EbookGenerator initialized with utils integration")

        # Load prompt configs as the primary source of truth
        self.niches = {}
        try:
            prompts_path = Path("config/prompts.json")
            if prompts_path.exists():
                with open(prompts_path, "r", encoding="utf-8") as f:
                    self.niches = json.load(f)
                    logger.info(f"Loaded {len(self.niches)} prompts from prompts.json")
            else:
                logger.error("prompts.json not found in config directory")
        except Exception as e:
            logger.error(f"Failed to load prompts.json: {e}")

        # Initialize OpenRouter
        try:
            self.ai_client = OpenRouter()
        except:
            logger.warning("OpenRouter client failed to initialize (check API key)")
            self.ai_client = None

    
    def generate_chapter_content(self, niche, chapter_title, word_count=1500):
        """Generate chapter content using OpenRouter API"""
        
        prompt_config = self.prompt_configs.get(niche, {})
        system_role = prompt_config.get("role", "You are an expert ghostwriter.")
        base_content = prompt_config.get("content", "")
        
        prompt = f"""
        {base_content}
        
        Write a detailed chapter about "{chapter_title}" for an ebook titled "{self.niches[niche]['title']}".
        
        Requirements:
        1. Make it practical and actionable
        2. Include step-by-step instructions
        3. Mention specific FREE AI tools (ChatGPT, Bing AI, Canva, etc.)
        4. Include real examples and case studies
        5. Write in engaging, conversational tone
        6. Target audience: {self.niches[niche].get('target', self.niches[niche].get('target_audience', 'General Audience'))}
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
            if not self.ai_client:
                 raise Exception("OpenRouter client not initialized")

            # Using OpenRouter
            logger.info(f"Calling OpenRouter for chapter: {chapter_title}")
            response = self.ai_client.create_chat_completion(
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenRouter returned invalid response: {response}")
                raise Exception("Empty response from OpenRouter")
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Fallback content
            return f"# {chapter_title}\n\nThis chapter covers {chapter_title} in detail. Due to API limits, content generation is simplified. In the full version, this would include step-by-step instructions, AI tools, and practical examples."
    
    def generate_outline(self, topic_prompt):
        """Generate a chapter outline for the book"""
        logger.info(f"Generating outline for: {topic_prompt}")
        
        prompt = f"""
        {topic_prompt}
        
        Based on the request above, create a comprehensive outline for a 25,000 word book.
        Return strictly a JSON list of strings, where each string is a chapter title.
        The list should have at least 15 chapters to ensure enough length.
        Example: ["Introduction to...", "The Psychology of...", "Advanced Techniques...", ...]
        Do not include any explanation, just the JSON array.
        """
        
        try:
            response = self.ai_client.create_chat_completion(
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {"role": "system", "content": "You are a professional book outliner. Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                if "<think>" in content:
                    content = content.split("</think>")[-1]
                content = content.strip()
                
                # Extract JSON list
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    content = content[start:end+1]
                    return json.loads(content)
            
            # Fallback outline if parsing fails
            return [f"Chapter {i}: Detailed Analysis" for i in range(1, 16)]
            
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return [f"Section {i}" for i in range(1, 11)]

    def generate_book_directly(self, niche, filepath=None):
        """Generate entire book using recursive generation (Outline -> Chapters)"""
        details = self.niches[niche]
        prompt_content = details.get("content", "")
        title = details.get("title", niche)
        
        logger.info(f"Generating book '{title}' via recursive outline method...")
        
        # 1. Generate Outline
        chapters = self.generate_outline(prompt_content)
        logger.info(f"Generated outline with {len(chapters)} chapters")
        
        full_content = ""
        
        # 2. Generate content for each chapter
        for i, chapter_title in enumerate(chapters, 1):
            logger.info(f"Writing chapter {i}/{len(chapters)}: {chapter_title}")
            
            chapter_prompt = f"""
            Write a comprehensive, detailed chapter titled "{chapter_title}".
            This is part of a book about: {details.get('title', 'this topic')}.
            
            Requirements:
            - Write at least 2000 words.
            - Go extremely deep into details.
            - Provide actionable steps, examples, and psychological insights.
            - Do not include "Chapter X" in headings, just use the title.
            - Write in a flowing, engaging style.
            """
            
            retry_count = 0
            chapter_text = ""
            
            while retry_count < 3:
                try:
                    response = self.ai_client.create_chat_completion(
                        model="deepseek/deepseek-r1-0528:free",
                        messages=[
                            {"role": "system", "content": details.get("role", "You are an expert author.")},
                            {"role": "user", "content": chapter_prompt}
                        ]
                    )
                    
                    if response and "choices" in response:
                        chunk = response["choices"][0]["message"]["content"]
                        if "<think>" in chunk:
                            chunk = chunk.split("</think>")[-1].strip()
                        
                        if len(chunk) > 100:
                            chapter_text = chunk
                            break
                    
                    retry_count += 1
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Error generating chapter {chapter_title}: {e}")
                    retry_count += 1
                    time.sleep(2)
            
            if chapter_text:
                chapter_markdown = f"## {chapter_title}\n\n{chapter_text}\n\n"
            else:
                chapter_markdown = f"## {chapter_title}\n\n[Content missing for this section]\n\n"
            
            full_content += chapter_markdown
            
            # Incremental save to file
            if filepath:
                try:
                    with open(filepath, "a", encoding="utf-8") as f:
                        f.write(chapter_markdown)
                    logger.info(f"Incrementally saved chapter {i} to {filepath}")
                except Exception as e:
                    logger.error(f"Failed to save chapter {i} to file: {e}")
            
        return full_content

    def generate_conclusion(self, book_content):
        """Generate a conclusion based on the book content"""
        logger.info("Generating dynamic conclusion...")
        
        prompt = f"""
        Here is the content of a book I just wrote:
        
        {book_content[:15000]} ... [truncated] ... {book_content[-5000:]}
        
        Please write a powerful, inspiring conclusion for this book.
        summarize the key points and give the reader a final call to action.
        Do not look like an AI. Write like a human author.
        Match the tone of the book.
        """
        
        try:
            if not self.ai_client:
                 raise Exception("OpenRouter client not initialized")

            response = self.ai_client.create_chat_completion(
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {"role": "system", "content": "You are a professional book editor and closer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response and "choices" in response:
                conclusion = response["choices"][0]["message"]["content"]
                # Clean think tags
                if "<think>" in conclusion:
                    conclusion = conclusion.split("</think>")[-1].strip()
                return conclusion
            return "Conclusion could not be generated."
            
        except Exception as e:
            logger.error(f"Error generating conclusion: {e}")
            return "Failed to generate conclusion."

    def create_ebook_markdown(self, niche):
        """Create complete ebook in markdown format"""
        
        details = self.niches[niche]
        
        # Check if we have chapters (legacy/niches.json mode)
        if "chapters" in details:
             return self._create_ebook_from_chapters(niche, details)
        
        # Determine filepath
        filename = f"{sanitize_filename(niche)}_ebook.md"
        filepath = self.output_dir / filename
        
        # New mode: Prompt only
        content = f"# {details['title']}\n\n"
        
        # Write header initially
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Generate the whole thing with incremental saving
        generated_body = self.generate_book_directly(niche, filepath=filepath)
        
        # Return full content (legacy support)
        return content + generated_body

    def _create_ebook_from_chapters(self, niche, details):
        content = f"# {details['title']}\n\n"
        # Removed timestamp
        
        # Add table of contents
        content += "## Table of Contents\n\n"
        for i, chapter in enumerate(details['chapters'], 1):
            content += f"{i}. {chapter}\n"
        
        content += "\n---\n\n"
        
        # Generate each chapter
        for i, chapter in enumerate(details['chapters'], 1):
            logger.info(f"Generating chapter {i}/{len(details['chapters'])}: {chapter}")
            
            chapter_content = self.generate_chapter_content(niche, chapter)
            # Removed "Chapter X:" header, just content
            content += f"## {chapter}\n\n{chapter_content}\n\n"
            
            # Add page break
            content += "\\newpage\n\n" if i < len(details['chapters']) else ""
            
            # Delay to avoid rate limiting
            time.sleep(2)
        
        # Generate dynamic conclusion
        conclusion = self.generate_conclusion(content)
        content += f"\n\n# Conclusion\n\n{conclusion}"
        
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
            target_audience = self.niches[niche].get('target', self.niches[niche].get('target_audience', 'General Audience'))
            # Safe access for chapters
            num_chapters = len(self.niches[niche].get('chapters', []))
            logger.info(f"Chapters: {num_chapters} (or direct prompt)")
            logger.info(f"Target: {target_audience}")
            
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
            target_audience = details.get('target', details.get('target_audience', 'General Audience'))
            summary += f"**Target:** {target_audience}\n"
            num_chapters = len(details.get('chapters', []))
            summary += f"**Chapters:** {num_chapters} (or direct prompt)\n"
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
        
        total_chapters = sum(len(details.get('chapters', [])) for details in self.niches.values())
        total_words_estimate = total_chapters * 1500  # Approximate
        
        return {
            "total_ebooks": len(self.niches),
            "total_chapters": total_chapters,
            "estimated_words": total_words_estimate,
            "generated_files": self.generated_files
        }

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Ebook Generator')
    parser.add_argument('--phase', type=int, help='Phase number (1: Generate all + PDF)')
    args = parser.parse_args()

    print("=" * 60)
    print("AI EBOOK GENERATOR - 72 HOUR CASH SYSTEM")
    print("=" * 60)
    
    generator = EbookGenerator()

    if args.phase == 1:
        print("\n🚀 EXECUTING PHASE 1: Generate All Ebooks + PDFs")
        # 1. Generate Ebooks
        generator.generate_all()

        # 1.5 Generate Covers
        print("\n🖼️ Starting Cover Generation...")
        image_gen = ImageGenerator(output_dir=generator.output_dir)
        try:
            # We pass generator.niches because that now holds the loaded prompts/titles
            image_gen.generate_all(niches=generator.niches, use_api=False) 
        except Exception as e:
            logger.error(f"Cover generation failed: {e}")
        
        # 2. Convert to PDF
        print("\n📄 Starting PDF Conversion...")
        pdf_converter = PDFConverter(output_dir=generator.output_dir)
        pdf_converter.convert_all()
        
        print("\n✅ PHASE 1 COMPLETE")
        sys.exit(0)
    
    # Interactive mode (fallback)
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