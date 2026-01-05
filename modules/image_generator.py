"""
Professional eBook Cover Image Generator
Generates attractive covers using PIL or AI services
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from utils.logger import get_logger
from utils.helpers import load_niches, sanitize_filename, get_env_variable

logger = get_logger("image_generator")

class ImageGenerator:
    def __init__(self, output_dir="data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ImageGenerator initialized")
    
    def generate_gradient_background(self, width, height, color1, color2):
        """Generate gradient background"""
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    def create_local_cover(self, title, niche, width=1600, height=2400):
        """Create cover using PIL (fallback method)"""
        logger.info(f"Creating local cover for: {niche}")
        
        # Color schemes for different niches
        color_schemes = {
            "men_lust": ((47, 54, 64), (87, 101, 116)),
            "women_beauty": ((255, 118, 117), (253, 203, 110)),
            "rich_time": ((18, 137, 167), (0, 210, 211)),
            "parents_peace": ((162, 155, 254), (205, 180, 219)),
            "kids_dreams": ((255, 195, 18), (255, 107, 107)),
            "poor_hope": ((34, 166, 179), (83, 211, 156))
        }
        
        colors = color_schemes.get(niche, ((102, 126, 234), (118, 75, 162)))
        
        # Create gradient background
        img = self.generate_gradient_background(width, height, colors[0], colors[1])
        
        # Add subtle texture
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font, fallback to default
        try:
            # Try to use Arial or another common font
            title_font = ImageFont.truetype("arial.ttf", 120)
            subtitle_font = ImageFont.truetype("arial.ttf", 60)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title with word wrapping
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] > width - 200:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text centered
        y_offset = height // 3
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw shadow
            draw.text((x + 5, y_offset + 5), line, font=title_font, fill=(0, 0, 0, 100))
            # Draw text
            draw.text((x, y_offset), line, font=title_font, fill='white')
            y_offset += 150
        
        # Add subtitle
        subtitle = "AI-Powered System"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = bbox[2] - bbox[0]
        x = (width - subtitle_width) // 2
        draw.text((x, height - 300), subtitle, font=subtitle_font, fill='white')
        
        # Add decorative line
        draw.rectangle([width // 4, height - 400, width * 3 // 4, height - 395], fill='white')
        
        return img
    
    def generate_with_api(self, title, niche):
        """Generate cover using Stability AI or other API"""
        api_key = get_env_variable('STABILITY_AI_KEY')
        
        if not api_key:
            logger.warning("No Stability AI key found, using local generation")
            return None
        
        prompt = f"Professional ebook cover for '{title}', minimalist, modern design, attractive, trending on Amazon, high quality, digital art"
        
        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                img_data = data['artifacts'][0]['base64']
                import base64
                img = Image.open(BytesIO(base64.b64decode(img_data)))
                # Resize to ebook cover dimensions
                img = img.resize((1600, 2400), Image.LANCZOS)
                logger.success(f"Generated cover with AI for: {niche}")
                return img
            else:
                logger.error(f"API failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            return None
    
    def generate_cover(self, niche, title, use_api=False):
        """Generate cover image for a niche"""
        logger.info(f"Generating cover for: {niche}")
        
        # Try API first if enabled
        img = None
        if use_api:
            img = self.generate_with_api(title, niche)
        
        # Fallback to local generation
        if img is None:
            img = self.create_local_cover(title, niche)
        
        # Save image
        filename = f"{sanitize_filename(niche)}_cover.png"
        filepath = self.output_dir / filename
        img.save(filepath, 'PNG', quality=95)
        
        logger.success(f"Saved cover: {filename}")
        return str(filepath)
    
    def generate_all(self, niches=None, use_api=False):
        """Generate all covers"""
        if niches is None:
            niches = load_niches()
        
        logger.info(f"Generating {len(niches)} covers...")
        
        generated_files = []
        for niche, details in niches.items():
            try:
                filepath = self.generate_cover(niche, details['title'], use_api)
                generated_files.append(filepath)
            except Exception as e:
                logger.error(f"Failed to generate cover for {niche}: {e}")
        
        logger.success(f"Generated {len(generated_files)} covers")
        return generated_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate ebook covers')
    parser.add_argument('--api', action='store_true', help='Use API for generation')
    parser.add_argument('--test-mode', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    generator = ImageGenerator()
    generator.generate_all(use_api=args.api)

if __name__ == "__main__":
    main()
