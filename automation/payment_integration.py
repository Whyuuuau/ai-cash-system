"""
Payment Integration Module
Supports Gumroad, Stripe, and PayPal for automated sales tracking and payment processing
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.logger import get_logger
from utils.helpers import get_env_variable

logger = get_logger("payment_integration")

class PaymentIntegration:
    def __init__(self):
        self.platforms = {}
        self.last_sync = {}
        
        # Initialize Gumroad
        gumroad_token = get_env_variable('GUMROAD_ACCESS_TOKEN', required=False)
        if gumroad_token:
            self.platforms['gumroad'] = GumroadAPI(gumroad_token)
            logger.info("Gumroad integration enabled")
        
        # Initialize Stripe (optional)
        stripe_key = get_env_variable('STRIPE_SECRET_KEY', required=False)
        if stripe_key:
            try:
                import stripe
                self.platforms['stripe'] = StripeAPI(stripe_key)
                logger.info("Stripe integration enabled")
            except ImportError:
                logger.warning("Stripe package not installed. Run: pip install stripe")
        
        # Initialize PayPal (optional)
        paypal_id = get_env_variable('PAYPAL_CLIENT_ID', required=False)
        paypal_secret = get_env_variable('PAYPAL_CLIENT_SECRET', required=False)
        if paypal_id and paypal_secret:
            try:
                self.platforms['paypal'] = PayPalAPI(paypal_id, paypal_secret)
                logger.info("PayPal integration enabled")
            except Exception as e:
                logger.warning(f"PayPal initialization failed: {e}")
        
        if not self.platforms:
            logger.warning("No payment platforms configured. Sales tracking will be manual.")
    
    def fetch_all_sales(self, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch sales from all configured platforms"""
        all_sales = []
        
        for platform_name, platform_obj in self.platforms.items():
            try:
                logger.info(f"Fetching sales from {platform_name}...")
                sales = platform_obj.get_sales(since=since)
                
                # Normalize sales data
                for sale in sales:
                    sale['platform'] = platform_name
                    all_sales.append(sale)
                
                logger.success(f"Fetched {len(sales)} sales from {platform_name}")
                self.last_sync[platform_name] = datetime.now()
                
            except Exception as e:
                logger.error(f"Failed to fetch from {platform_name}: {e}")
        
        return all_sales
    
    def create_payment_links(self, product_name: str, price: float, product_id: str = None) -> Dict[str, str]:
        """Generate payment links for all platforms"""
        links = {}
        
        for platform_name, platform_obj in self.platforms.items():
            try:
                link = platform_obj.create_payment_link(product_name, price, product_id)
                if link:
                    links[platform_name] = link
                    logger.info(f"Generated {platform_name} link for {product_name}")
            except Exception as e:
                logger.error(f"Failed to create {platform_name} link: {e}")
        
        return links
    
    def update_product_price(self, product_id: str, new_price: float, platform: str = 'gumroad') -> bool:
        """Update product pricing (for emergency protocol)"""
        if platform not in self.platforms:
            logger.error(f"Platform {platform} not configured")
            return False
        
        try:
            result = self.platforms[platform].update_price(product_id, new_price)
            if result:
                logger.success(f"Updated {product_id} to ${new_price} on {platform}")
            return result
        except Exception as e:
            logger.error(f"Failed to update price: {e}")
            return False
    
    def get_product_urls(self, product_mapping: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Get payment URLs for all products across all platforms"""
        product_urls = {}
        
        for product_id, product_name in product_mapping.items():
            product_urls[product_id] = self.create_payment_links(
                product_name=product_name,
                price=27,  # Default price
                product_id=product_id
            )
        
        return product_urls


class GumroadAPI:
    """Gumroad API Integration"""
    
    def __init__(self, access_token: str):
        self.token = access_token
        self.base_url = "https://api.gumroad.com/v2"
        logger.info("GumroadAPI initialized")
    
    def get_sales(self, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch sales from Gumroad"""
        params = {"access_token": self.token}
        
        if since:
            # Gumroad uses 'after' parameter with timestamp
            params['after'] = since.isoformat()
        
        try:
            response = requests.get(f"{self.base_url}/sales", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                sales = []
                for sale in data.get('sales', []):
                    sales.append({
                        'id': sale.get('id'),
                        'product': sale.get('product_name'),
                        'amount': float(sale.get('price', 0)) / 100,  # Gumroad uses cents
                        'email': sale.get('email'),
                        'timestamp': sale.get('created_at'),
                        'product_id': sale.get('product_id')
                    })
                return sales
            else:
                logger.error(f"Gumroad API error: {data.get('message')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Gumroad API request failed: {e}")
            return []
    
    def create_payment_link(self, product_name: str, price: float, product_id: str = None) -> Optional[str]:
        """Get Gumroad product URL"""
        if product_id:
            # If we have product ID, construct URL
            # Format: https://yourusername.gumroad.com/l/product-permalink
            return f"https://gumroad.com/l/{product_id}"
        else:
            # Would need to create new product via API
            logger.warning("Product creation not implemented. Please create products manually.")
            return None
    
    def update_price(self, product_id: str, new_price: float) -> bool:
        """Update product price"""
        data = {
            "access_token": self.token,
            "price": int(new_price * 100)  # Convert to cents
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/products/{product_id}",
                data=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to update Gumroad price: {e}")
            return False


class StripeAPI:
    """Stripe API Integration"""
    
    def __init__(self, secret_key: str):
        import stripe
        stripe.api_key = secret_key
        self.stripe = stripe
        logger.info("StripeAPI initialized")
    
    def get_sales(self, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch charges from Stripe"""
        try:
            params = {'limit': 100}
            if since:
                params['created'] = {'gte': int(since.timestamp())}
            
            charges = self.stripe.Charge.list(**params)
            
            sales = []
            for charge in charges.auto_paging_iter():
                if charge.status == 'succeeded':
                    sales.append({
                        'id': charge.id,
                        'product': charge.description or 'Product',
                        'amount': float(charge.amount) / 100,  # Stripe uses cents
                        'email': charge.billing_details.email if charge.billing_details else None,
                        'timestamp': datetime.fromtimestamp(charge.created).isoformat(),
                        'product_id': charge.metadata.get('product_id')
                    })
            
            return sales
            
        except Exception as e:
            logger.error(f"Stripe API error: {e}")
            return []
    
    def create_payment_link(self, product_name: str, price: float, product_id: str = None) -> Optional[str]:
        """Create Stripe payment link"""
        try:
            # Create price object
            price_obj = self.stripe.Price.create(
                unit_amount=int(price * 100),
                currency="usd",
                product_data={"name": product_name}
            )
            
            # Create payment link
            link = self.stripe.PaymentLink.create(
                line_items=[{"price": price_obj.id, "quantity": 1}]
            )
            
            return link.url
            
        except Exception as e:
            logger.error(f"Failed to create Stripe link: {e}")
            return None
    
    def update_price(self, product_id: str, new_price: float) -> bool:
        """Stripe prices are immutable, need to create new price and update product"""
        try:
            # Create new price
            new_price_obj = self.stripe.Price.create(
                unit_amount=int(new_price * 100),
                currency="usd",
                product=product_id
            )
            
            # Update product default price
            self.stripe.Product.modify(
                product_id,
                default_price=new_price_obj.id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Stripe price: {e}")
            return False


class PayPalAPI:
    """PayPal API Integration"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api-m.paypal.com"  # Production
        # self.base_url = "https://api-m.sandbox.paypal.com"  # Sandbox
        self.access_token = None
        self._get_access_token()
        logger.info("PayPalAPI initialized")
    
    def _get_access_token(self):
        """Get OAuth access token"""
        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                timeout=30
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
        except Exception as e:
            logger.error(f"PayPal auth failed: {e}")
    
    def get_sales(self, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch transactions from PayPal"""
        if not self.access_token:
            return []
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Define date range
            end_date = datetime.now()
            start_date = since or (end_date - timedelta(days=7))
            
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'fields': 'all'
            }
            
            response = requests.get(
                f"{self.base_url}/v1/reporting/transactions",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            sales = []
            for txn in data.get('transaction_details', []):
                if txn.get('transaction_info', {}).get('transaction_status') == 'S':  # Success
                    info = txn.get('transaction_info', {})
                    sales.append({
                        'id': info.get('transaction_id'),
                        'product': info.get('transaction_subject', 'Product'),
                        'amount': float(info.get('transaction_amount', {}).get('value', 0)),
                        'email': txn.get('payer_info', {}).get('email_address'),
                        'timestamp': info.get('transaction_initiation_date'),
                        'product_id': None
                    })
            
            return sales
            
        except Exception as e:
            logger.error(f"PayPal API error: {e}")
            return []
    
    def create_payment_link(self, product_name: str, price: float, product_id: str = None) -> Optional[str]:
        """PayPal payment links require product setup in dashboard"""
        logger.warning("PayPal payment link creation requires dashboard setup")
        return None
    
    def update_price(self, product_id: str, new_price: float) -> bool:
        """PayPal price updates require dashboard access"""
        logger.warning("PayPal price updates require dashboard access")
        return False


def main():
    """Test payment integration"""
    print("="*60)
    print("Payment Integration Test")
    print("="*60)
    
    integration = PaymentIntegration()
    
    print(f"\nConfigured platforms: {list(integration.platforms.keys())}")
    
    if integration.platforms:
        print("\nFetching recent sales...")
        sales = integration.fetch_all_sales(since=datetime.now() - timedelta(days=7))
        
        print(f"\nFound {len(sales)} sales:")
        for sale in sales[:5]:  # Show first 5
            print(f"  • {sale['product']}: ${sale['amount']} ({sale['platform']})")
    else:
        print("\n⚠️ No payment platforms configured.")
        print("Set environment variables:")
        print("  - GUMROAD_ACCESS_TOKEN")
        print("  - STRIPE_SECRET_KEY (optional)")
        print("  - PAYPAL_CLIENT_ID & PAYPAL_CLIENT_SECRET (optional)")

if __name__ == "__main__":
    main()
