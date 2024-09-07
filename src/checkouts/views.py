from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect("/checkout")

@login_required
def checkhout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    print("checkout_subscription_price_id", checkout_subscription_price_id)
    if checkout_subscription_price_id is None:
        return redirect("/pricing")
    customer_stripe_id = request.user.customer.stripe_id
    return redirect("/checkout/abac")

def checkout_finalize_view(request):
    return