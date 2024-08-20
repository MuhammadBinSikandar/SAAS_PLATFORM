import safepay #type: ignore
from decouple import config

# Load environment variables
DJANGO_DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
SAFEPAY_API_KEY = config("SAFEPAY_API_KEY", default="", cast=str)
SAFEPAY_V1_SECRET = config("SAFEPAY_V1_SECRET", default="", cast=str)
SAFEPAY_WEBHOOK_SECRET = config("SAFEPAY_WEBHOOK_SECRET", default="", cast=str)

# Initialize Safepay environment
env = safepay.Safepay(
    {
        "environment": "sandbox" if DJANGO_DEBUG else "production",
        "apiKey": SAFEPAY_API_KEY,
        "v1Secret": SAFEPAY_V1_SECRET,
        "webhookSecret": SAFEPAY_WEBHOOK_SECRET,
    }
)

# Set payment details
payment_response = env.set_payment_details(
    {  
        "currency": "PKR", 
        "amount": 1000
    }
)

# Retrieve token from payment response
token = payment_response["data"]["token"]

# Generate checkout URL
checkout_url = env.get_checkout_url(
  {
      "beacon": token,
      "cancelUrl": "http://example.com/cancel",
      "orderId": "T800",
      "redirectUrl": "http://example.com/success",
      "source": "custom",
      "webhooks": True,
  }
)

# Redirect the user to the checkout URL
# Example: return redirect(checkout_url)  (if inside a Django view)
