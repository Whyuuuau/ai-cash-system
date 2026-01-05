"""
Landing Page Generator
Creates high-converting HTML landing pages for each product
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.helpers import load_niches, sanitize_filename

logger = get_logger("landing_generator")

class LandingPageGenerator:
    def __init__(self, output_dir="data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("LandingPageGenerator initialized")
    
    def generate_landing_page(self, niche, title, product_url="https://gumroad.com/l/PRODUCT", price=27):
        """Generate landing page HTML"""
        logger.info(f"Generating landing page for: {niche}")
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Instant Digital Download</title>
    <meta name="description" content="Get instant access to {title}. AI-powered system with step-by-step guide, tools, and templates.">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f7f9fc;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            margin: 10px 5px;
            font-size: 0.9em;
        }}
        
        .content-box {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .content-box h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2em;
        }}
        
        .benefits {{
            list-style: none;
            margin: 25px 0;
        }}
        
        .benefits li {{
            padding: 15px 15px 15px 50px;
            margin-bottom: 10px;
            position: relative;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .benefits li:before {{
            content: "✓";
            position: absolute;
            left: 20px;
            color: #28a745;
            font-weight: bold;
            font-size: 1.3em;
        }}
        
        .cta-button {{
            display: block;
            background: linear-gradient(135deg, #f97316 0%, #dc2626 100%);
            color: white;
            padding: 20px 40px;
            border-radius: 10px;
            text-decoration: none;
            font-size: 1.3em;
            font-weight: bold;
            text-align: center;
            margin: 30px 0;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 5px 20px rgba(249, 115, 22, 0.4);
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(249, 115, 22, 0.6);
        }}
        
        .price {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .price .amount {{
            font-size: 3em;
            color: #667eea;
            font-weight: bold;
        }}
        
        .price .original {{
            text-decoration: line-through;
            color: #999;
            font-size: 1.2em;
        }}
        
        .testimonial {{
            background: #f8f9fa;
            padding: 30px;
            border-left: 5px solid #667eea;
            margin: 25px 0;
            border-radius: 8px;
            font-style: italic;
        }}
        
        .testimonial .author {{
            margin-top: 15px;
            font-weight: bold;
            font-style: normal;
            color: #667eea;
        }}
        
        .guarantee {{
            text-align: center;
            padding: 30px;
            background: #d4edda;
            border-radius: 10px;
            margin: 30px 0;
        }}
        
        .guarantee h3 {{
            color: #155724;
            margin-bottom: 10px;
        }}
        
        .timer {{
            text-align: center;
            font-size: 1.5em;
            color: #dc2626;
            font-weight: bold;
            margin: 20px 0;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .urgent {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .urgent strong {{
            color: #dc2626;
            font-size: 1.2em;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content-box {{
                padding: 25px;
            }}
            
            .price .amount {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>AI-Powered System for Instant Results</p>
            <div class="badge">✅ Instant Digital Download</div>
            <div class="badge">✅ 30-Day Money Back Guarantee</div>
            <div class="badge">✅ Lifetime Updates</div>
        </div>
        
        <div class="urgent">
            <strong>🔥 72-HOUR SPECIAL OFFER 🔥</strong>
            <p>Price increases to $97 after first 100 copies sold!</p>
        </div>
        
        <div class="content-box">
            <h2>What You'll Get:</h2>
            <ul class="benefits">
                <li>Complete {title} System with step-by-step implementation guide</li>
                <li>AI Tools & Templates ready to use immediately</li>
                <li>Exclusive automation scripts and workflows</li>
                <li>Real-world case studies and examples</li>
                <li>Lifetime access to all updates and improvements</li>
                <li>Priority email support for questions</li>
            </ul>
        </div>
        
        <div class="testimonial">
            "This system completely transformed my approach. Within 72 hours, I saw real results. The AI tools alone are worth 10x the price!"
            <div class="author">— Sarah M., Early Adopter</div>
        </div>
        
        <div class="price">
            <div class="original">Regular Price: $97</div>
            <div class="amount">${price}</div>
            <p>One-time payment • Instant access</p>
        </div>
        
        <a href="{product_url}" class="cta-button" onclick="trackPurchase()">
            🚀 GET INSTANT ACCESS NOW
        </a>
        
        <div class="guarantee">
            <h3>💯 30-Day Money-Back Guarantee</h3>
            <p>Try it risk-free. If you're not completely satisfied, get a full refund within 30 days. No questions asked.</p>
        </div>
        
        <div class="content-box">
            <h2>Why This Works:</h2>
            <p>This isn't theory. This is a proven system built in 72 hours using cutting-edge AI technology. Every strategy, tool, and template has been tested in real-world conditions.</p>
            <p>You're not just buying an ebook—you're getting a complete automation system that continues to work for you.</p>
        </div>
        
        <div class="timer" id="countdown">
            ⏰ <span id="timer-display">72 hours remaining at this price</span>
        </div>
        
        <a href="{product_url}" class="cta-button">
            🚀 YES! I WANT INSTANT ACCESS
        </a>
        
        <div class="footer">
            <p>© 2026 72-Hour AI Cash System. All rights reserved.</p>
            <p>Questions? Email: support@example.com</p>
        </div>
    </div>
    
    <script>
        function trackPurchase() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'click', {{
                    'event_category': 'CTA',
                    'event_label': 'Purchase Button'
                }});
            }}
        }}
        
        // Countdown timer
        let hoursRemaining = 72;
        function updateTimer() {{
            const display = document.getElementById('timer-display');
            if (hoursRemaining > 0) {{
                display.textContent = hoursRemaining + ' hours remaining at this price';
                hoursRemaining--;
            }} else {{
                display.textContent = 'Special pricing ended!';
            }}
        }}
        
        // Update every hour (3600000 ms)
        setInterval(updateTimer, 3600000);
    </script>
</body>
</html>"""
        
        # Save HTML file
        filename = f"{sanitize_filename(niche)}_landing.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        logger.success(f"Generated landing page: {filename}")
        logger.info(f"Upload to: https://app.netlify.com/drop")
        logger.info(f"Suggested URL: https://{sanitize_filename(niche)}-ai-system.netlify.app")
        
        return str(filepath)
    
    def generate_all(self, niches=None):
        """Generate all landing pages"""
        if niches is None:
            niches = load_niches()
        
        logger.info(f"Generating {len(niches)} landing pages...")
        
        generated_files = []
        for niche, details in niches.items():
            try:
                filepath = self.generate_landing_page(
                    niche,
                    details['title'],
                    f"https://gumroad.com/l/{sanitize_filename(niche)}",
                    details.get('price', 27)
                )
                generated_files.append(filepath)
            except Exception as e:
                logger.error(f"Failed to generate landing page for {niche}: {e}")
        
        logger.success(f"Generated {len(generated_files)} landing pages")
        return generated_files

def main():
    generator = LandingPageGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()
