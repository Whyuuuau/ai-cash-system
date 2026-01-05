"""
Standalone Gumroad Setup Helper
Semi-automated Gumroad product creation using Selenium
"""
import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from utils.helpers import load_niches

logger = get_logger("gumroad_setup")

class GumroadSetup:
    def __init__(self):
        self.niches = load_niches()
        self.product_urls = {}
        logger.info("Gumroad setup initialized")
    
    def setup_driver(self):
        """Setup Chrome driver"""
        try:
            options = webdriver.ChromeOptions()
            # Add options for better compatibility
            options.add_argument('--start-maximized')
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            print("\n⚠️ Selenium ChromeDriver not found.")
            print("Download from: https://chromedriver.chromium.org/")
            return None
    
    def manual_setup_guide(self):
        """Print manual setup guide"""
        print("\n" + "="*70)
        print("📋 GUMROAD MANUAL SETUP GUIDE")
        print("="*70 + "\n")
        
        print("1. Go to: https://gumroad.com/products")
        print("2. Click 'New Product'")
        print("3. For each product:\n")
        
        for niche, details in self.niches.items():
            pdf_file = f"data/output/{niche}_ebook.pdf"
            
            print(f"\n--- {details['title']} ---")
            print(f"   Name: {details['title']}")
            print(f"   Price: ${details.get('price', 27)}")
            print(f"   File: {pdf_file}")
            print(f"   Description:")
            print(f"   'Instant access to {details['title']}.")
            print(f"    Includes AI tools, templates, and step-by-step system.'")
            print(f"   URL: Save as: {niche}-ai-system")
        
        print("\n" + "="*70)
        print("After setup, save URLs to: data/output/product_urls.txt")
        print("Format: niche:URL")
        print("="*70 + "\n")
    
    def automated_setup(self):
        """Semi-automated setup with Selenium"""
        print("\n🤖 Starting semi-automated Gumroad setup...")
        print("You will need to login manually, then the script will help fill forms.\n")
        
        driver = self.setup_driver()
        if not driver:
            print("❌ Cannot start automation without ChromeDriver")
            return self.manual_setup_guide()
        
        try:
            # Navigate to Gumroad
            driver.get("https://gumroad.com/login")
            print("✅ Opened Gumroad")
            print("\n⏸️  Please login to your Gumroad account...")
            input("Press Enter after you've logged in...")
            
            # Create products
            urls_file = Path("data/output/product_urls.txt")
            urls_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(urls_file, 'w') as f:
                for niche, details in self.niches.items():
                    print(f"\n📦 Creating product: {details['title']}")
                    
                    # Navigate to new product page
                    driver.get("https://gumroad.com/products/new")
                    time.sleep(2)
                    
                    try:
                        # Fill product name
                        name_field = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "product[name]"))
                        )
                        name_field.send_keys(details['title'])
                        
                        # Fill price
                        price_field = driver.find_element(By.NAME, "product[price]")
                        price_field.clear()
                        price_field.send_keys(str(details.get('price', 27)))
                        
                        # Upload file
                        pdf_path = Path(f"data/output/{niche}_ebook.pdf").absolute()
                        if pdf_path.exists():
                            upload_field = driver.find_element(By.NAME, "product[file]")
                            upload_field.send_keys(str(pdf_path))
                            print(f"   ✅ Uploaded: {pdf_path.name}")
                        else:
                            print(f"   ⚠️ PDF not found: {pdf_path}")
                        
                        # Fill description
                        desc_field = driver.find_element(By.NAME, "product[description]")
                        description = f"Instant access to {details['title']}. Includes AI tools, templates, and step-by-step system."
                        desc_field.send_keys(description)
                        
                        # Wait for user to review and publish
                        print("   ⏸️  Review the product details and click 'Publish'")
                        input("   Press Enter after publishing...")
                        
                        # Get product URL
                        product_url = driver.current_url
                        print(f"   ✅ Product created: {product_url}")
                        
                        # Save URL
                        f.write(f"{niche}:{product_url}\n")
                        self.product_urls[niche] = product_url
                        
                    except Exception as e:
                        logger.error(f"Error creating {niche}: {e}")
                        print(f"   ❌ Error: {e}")
                        print("   Continuing with manual entry...")
                        manual_url = input(f"   Enter product URL for {niche} (or press Enter to skip): ")
                        if manual_url:
                            f.write(f"{niche}:{manual_url}\n")
                            self.product_urls[niche] = manual_url
            
            print(f"\n✅ Setup complete! URLs saved to: {urls_file}")
            
        except Exception as e:
            logger.error(f"Automation error: {e}")
            print(f"\n❌ Automation failed: {e}")
            print("Falling back to manual guide...")
            self.manual_setup_guide()
        
        finally:
            if driver:
                print("\nClosing browser in 5 seconds...")
                time.sleep(5)
                driver.quit()
    
    def load_existing_urls(self):
        """Load existing product URLs"""
        urls_file = Path("data/output/product_urls.txt")
        
        if urls_file.exists():
            with open(urls_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        niche, url = line.strip().split(':', 1)
                        self.product_urls[niche] = url
            
            print(f"✅ Loaded {len(self.product_urls)} product URLs")
            for niche, url in self.product_urls.items():
                print(f"   • {niche}: {url}")
        else:
            print("⚠️ No existing URLs found")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gumroad Setup Helper')
    parser.add_argument('--auto', action='store_true', help='Try automated setup')
    parser.add_argument('--manual', action='store_true', help='Show manual guide')
    parser.add_argument('--load', action='store_true', help='Load existing URLs')
    
    args = parser.parse_args()
    
    setup = GumroadSetup()
    
    if args.load:
        setup.load_existing_urls()
    elif args.auto:
        setup.automated_setup()
    elif args.manual:
        setup.manual_setup_guide()
    else:
        # Interactive mode
        print("\n🚀 Gumroad Setup Helper")
        print("\nOptions:")
        print("1. Automated setup (requires ChromeDriver)")
        print("2. Manual setup guide")
        print("3. Load existing URLs")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == '1':
            setup.automated_setup()
        elif choice == '2':
            setup.manual_setup_guide()
        elif choice == '3':
            setup.load_existing_urls()
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
