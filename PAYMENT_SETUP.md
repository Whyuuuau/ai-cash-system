# Payment Integration Setup Guide

## 🎯 Overview

Sistem ini sekarang mendukung 3 payment gateway:

1. **Gumroad** (Recommended - Easiest)
2. **Stripe** (Optional - More control)
3. **PayPal** (Optional - Global reach)

---

## 📋 MANUAL CONFIGURATION REQUIRED

### 1. Gumroad Setup (RECOMMENDED)

#### Step 1: Create Gumroad Account

1. Go to [gumroad.com](https://gumroad.com)
2. Sign up for free account
3. Verify email

#### Step 2: Get API Access Token

1. Go to https://app.gumroad.com/settings/advanced
2. Click "Generate access token"
3. Copy the token
4. Add to `.env` file:
   ```bash
   GUMROAD_ACCESS_TOKEN=your_token_here
   ```

#### Step 3: Create Products

**Option A: Manual (Recommended for first time)**

1. Go to https://app.gumroad.com/products
2. Click "New Product"
3. For each ebook:
   - Upload PDF from `data/output/`
   - Set price: $27
   - Set permalink (e.g., `men-lust-ai`)
   - Add description
   - Publish

**Option B: Semi-Automated**

```bash
python automation/gumroad_setup.py --auto
```

#### Step 4: Save Product URLs

Create file: `data/output/product_urls.txt`

```
men_lust:https://gumroad.com/l/men-lust-ai
women_beauty:https://gumroad.com/l/women-beauty-ai
rich_time:https://gumroad.com/l/rich-time-ai
parents_peace:https://gumroad.com/l/parents-peace-ai
kids_dreams:https://gumroad.com/l/kids-dreams-ai
poor_hope:https://gumroad.com/l/poor-hope-ai
```

#### Step 5: Setup Webhooks (For Auto-Delivery)

1. Start webhook server:

   ```bash
   python automation/webhook_handler.py --port 5000
   ```

2. Expose with ngrok:

   ```bash
   ngrok http 5000
   ```

3. In Gumroad advanced settings:
   - Webhook URL: `https://your-ngrok-url.ngrok.io/webhook/gumroad`
   - Secret: Generate random string, add to `.env` as `GUMROAD_WEBHOOK_SECRET`

---

### 2. Stripe Setup (OPTIONAL)

#### Prerequisites

Install Stripe package:

```bash
pip install stripe
```

#### Step 1: Create Stripe Account

1. Go to [stripe.com](https://stripe.com)
2. Sign up
3. Complete KYC verification

#### Step 2: Get API Keys

1. Go to https://dashboard.stripe.com/apikeys
2. Copy "Secret key" (starts with `sk_`)
3. Add to `.env`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   ```

#### Step 3: Setup Webhook (Optional)

1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://your-domain.com/webhook/stripe`
3. Select events: `charge.succeeded`, `payment_intent.succeeded`
4. Get signing secret, add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

---

### 3. PayPal Setup (OPTIONAL)

#### Step 1: Create PayPal Business Account

1. Go to [paypal.com/business](https://paypal.com/business)
2. Sign up for business account
3. Verify account

#### Step 2: Create REST API App

1. Go to https://developer.paypal.com/dashboard
2. Create new app
3. Get Client ID and Secret
4. Add to `.env`:
   ```bash
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_CLIENT_SECRET=your_client_secret
   ```

---

## 🔄 Auto-Sync Sales

### Test Payment Integration

```bash
python automation/payment_integration.py
```

### Manual Sync

```bash
python monitoring/sales_tracker.py --mode sync
```

### Auto-sync in Main Controller

Payment sync runs automatically every hour when using:

```bash
python main_controller.py --phase 3
```

---

## 🎣 Webhook Server

### Production Deployment

#### Option 1: Deploy to Railway/Render

1. Create `Procfile`:

   ```
   web: python automation/webhook_handler.py --port $PORT
   ```

2. Deploy to Railway.app or Render.com
3. Get your deployment URL
4. Add to payment platforms

#### Option 2: Run on VPS

```bash
# Install gunicorn
pip install gunicorn

# Run webhook server
gunicorn -w 4 -b 0.0.0.0:5000 automation.webhook_handler:app
```

#### Option 3: Local with ngrok (Testing)

```bash
# Terminal 1
python automation/webhook_handler.py

# Terminal 2
ngrok http 5000
```

---

## ⚡ Emergency Protocol Integration

Emergency protokol dapat update harga otomatis:

```python
# Activated automatically when:
# - Less than 24 hours + below 80% target
# - Less than 12 hours + below 90% target

# Updates:
# 1. Gumroad: Sets PWYW with $1 minimum
# 2. Stripe: Creates new $47 bundle price
# 3. Generates emergency content
```

---

## 🧪 Testing

### Test Payment Integration

```bash
python automation/payment_integration.py
```

### Test Webhook Handler

```bash
# Start webhook server
python automation/webhook_handler.py

# In another terminal, test endpoint
curl -X POST http://localhost:5000/webhook/test
```

### Simulate Sale

```bash
curl -X POST http://localhost:5000/webhook/gumroad \
  -H "Content-Type: application/json" \
  -d '{"sale": {"product_name": "Test Product", "price": 2700, "email": "test@example.com"}}'
```

---

## ❓ Troubleshooting

### "No payment platforms configured"

- Check `.env` file has at least `GUMROAD_ACCESS_TOKEN`
- Verify token is correct
- Test with: `python automation/payment_integration.py`

### Webhooks not receiving

- Check webhook URL is accessible
- Verify ngrok is running (for local testing)
- Check webhook secret matches
- View webhook logs in payment platform dashboard

### Sales not syncing

- Check API credentials in `.env`
- Verify products exist in Gumroad
- Check date range (only syncs last 24 hours)
- Run manual sync: `python monitoring/sales_tracker.py --mode sync`

---

## 📊 Dashboard Integration

Sales from all platforms appear in:

```bash
python monitoring/sales_tracker.py --mode dashboard
```

Shows:

- ✅ Gumroad sales (API + webhooks)
- ✅ Stripe sales (if configured)
- ✅ PayPal sales (if configured)
- ✅ Total revenue aggregated
- ✅ Real-time progress tracking

---

## 🎯 Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` from `.env.example`
- [ ] Create Gumroad account
- [ ] Get Gumroad API token → Add to `.env`
- [ ] Upload products to Gumroad OR use `gumroad_setup.py`
- [ ] Save product URLs to `product_urls.txt`
- [ ] (Optional) Setup Stripe/PayPal
- [ ] Test integration: `python automation/payment_integration.py`
- [ ] Start webhook server (for auto-delivery)
- [ ] Run main system: `python main_controller.py --phase 3`

---

## 💡 Tips

1. **Start with Gumroad only** - Easiest to setup
2. **Test webhooks locally** with ngrok before deploying
3. **Monitor logs** in `data/logs/` for issues
4. **Backup sales data** regularly from `data/analytics/`
5. **Emergency protocol** activates automatically - no manual intervention needed

---

## 🚨 Important Notes

- **Gumroad** handles payment processing, fraud detection, delivery
- **Webhooks** enable real-time analytics and auto-delivery
- **API tokens** never expire (but keep them secret)
- **Test mode** recommended before live launch
- **Emergency pricing** updates automatically on Gumroad
- **Sales sync** happens every hour automatically
