"""
Webhook Handler for Payment Notifications
Handles automatic product delivery and sales tracking
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
import hmac
import hashlib
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import get_env_variable

logger = get_logger("webhook_handler")

app = Flask(__name__)

# Import tracking systems
try:
    from monitoring.sales_tracker import SalesTracker
    from automation.telegram_bot import TelegramBot
except ImportError:
    logger.warning("Could not import sales tracker or telegram bot")
    SalesTracker = None
    TelegramBot = None


class WebhookHandler:
    def __init__(self):
        self.sales_tracker = SalesTracker() if SalesTracker else None
        self.telegram_bot = TelegramBot() if TelegramBot else None
        self.gumroad_secret = get_env_variable('GUMROAD_WEBHOOK_SECRET', required=False)
        logger.info("WebhookHandler initialized")
    
    def verify_gumroad_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Gumroad webhook signature"""
        if not self.gumroad_secret:
            logger.warning("No Gumroad webhook secret configured")
            return True  # Skip verification if no secret
        
        computed = hmac.new(
            self.gumroad_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed, signature)
    
    def handle_gumroad_sale(self, data: dict) -> dict:
        """Process Gumroad sale webhook"""
        try:
            sale = data.get('sale', {})
            
            # Extract sale info
            product_name = sale.get('product_name', 'Unknown Product')
            amount = float(sale.get('price', 0)) / 100  # Gumroad uses cents
            email = sale.get('email')
            product_id = sale.get('product_id')
            sale_id = sale.get('id')
            
            logger.info(f"Processing Gumroad sale: {product_name} - ${amount}")
            
            # 1. Add to sales tracker
            if self.sales_tracker:
                self.sales_tracker.add_sale(
                    product=product_name,
                    amount=amount,
                    source='gumroad_webhook'
                )
                logger.success(f"Added to sales tracker: {sale_id}")
            
            # 2. Send confirmation via Telegram
            if self.telegram_bot and email:
                try:
                    message = f"""🎉 **New Sale!**
                    
Product: {product_name}
Amount: ${amount}
Customer: {email}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for your purchase! 🙏"""
                    
                    # Note: This would need customer's Telegram ID
                    # In practice, send to admin channel
                    logger.info(f"Sale notification ready: {product_name}")
                except Exception as e:
                    logger.error(f"Failed to send Telegram notification: {e}")
            
            # 3. Log for analytics
            self._log_sale(sale)
            
            return {
                'status': 'success',
                'sale_id': sale_id,
                'message': 'Sale processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to process Gumroad sale: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def handle_stripe_webhook(self, data: dict) -> dict:
        """Process Stripe webhook event"""
        try:
            event_type = data.get('type')
            
            if event_type == 'charge.succeeded':
                charge = data['data']['object']
                
                # Extract info
                amount = float(charge.get('amount', 0)) / 100
                description = charge.get('description', 'Product')
                email = charge.get('billing_details', {}).get('email')
                
                logger.info(f"Processing Stripe charge: {description} - ${amount}")
                
                # Add to sales tracker
                if self.sales_tracker:
                    self.sales_tracker.add_sale(
                        product=description,
                        amount=amount,
                        source='stripe_webhook'
                    )
                
                return {'status': 'success'}
            
            elif event_type == 'payment_intent.succeeded':
                logger.info("Payment intent succeeded")
                return {'status': 'success'}
            
            else:
                logger.info(f"Unhandled Stripe event: {event_type}")
                return {'status': 'ignored'}
                
        except Exception as e:
            logger.error(f"Failed to process Stripe webhook: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _log_sale(self, sale: dict):
        """Log sale to file for backup"""
        log_file = Path("data/analytics/webhook_sales.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {sale}\n")


# Global handler instance
webhook_handler = WebhookHandler()


# Flask routes
@app.route('/webhook/gumroad', methods=['POST'])
def gumroad_webhook():
    """Gumroad webhook endpoint"""
    try:
        # Get signature from headers
        signature = request.headers.get('X-Gumroad-Signature', '')
        
        # Verify signature
        if not webhook_handler.verify_gumroad_signature(request.data, signature):
            logger.warning("Invalid Gumroad signature")
            return jsonify({'error': 'Invalid signature'}), 403
        
        # Process sale
        data = request.json
        result = webhook_handler.handle_gumroad_sale(data)
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
        
    except Exception as e:
        logger.error(f"Gumroad webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe webhook endpoint"""
    try:
        # Verify Stripe signature (if configured)
        stripe_secret = get_env_variable('STRIPE_WEBHOOK_SECRET', required=False)
        
        if stripe_secret:
            signature = request.headers.get('Stripe-Signature')
            try:
                import stripe
                event = stripe.Webhook.construct_event(
                    request.data,
                    signature,
                    stripe_secret
                )
                data = event
            except Exception as e:
                logger.warning(f"Invalid Stripe signature: {e}")
                return jsonify({'error': 'Invalid signature'}), 403
        else:
            data = request.json
        
        # Process webhook
        result = webhook_handler.handle_stripe_webhook(data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test endpoint for webhook verification"""
    logger.info("Test webhook received")
    return jsonify({
        'status': 'ok',
        'message': 'Webhook handler is working',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'webhook_handler',
        'sales_tracker': webhook_handler.sales_tracker is not None,
        'telegram_bot': webhook_handler.telegram_bot is not None
    })


def run_webhook_server(host='0.0.0.0', port=5000, debug=False):
    """Run the webhook server"""
    logger.info(f"Starting webhook server on {host}:{port}")
    print(f"""
    ===============================================
    🎣 Webhook Handler Server Started
    ===============================================
    
    Endpoints:
    • POST /webhook/gumroad - Gumroad webhooks
    • POST /webhook/stripe - Stripe webhooks  
    • POST /webhook/test - Test endpoint
    • GET  /health - Health check
    
    Configure webhook URLs in your payment platforms:
    • Gumroad: http://your-domain.com/webhook/gumroad
    • Stripe: http://your-domain.com/webhook/stripe
    
    For local testing, use ngrok:
    $ ngrok http {port}
    
    ===============================================
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Webhook Handler Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_webhook_server(host=args.host, port=args.port, debug=args.debug)
