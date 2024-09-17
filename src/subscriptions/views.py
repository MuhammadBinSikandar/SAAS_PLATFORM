from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import helpers.billing as billing
from django.contrib import messages
from subscriptions import utils as subs_utils

# Create your views here.
@login_required
def user_subscription_view(request,):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("Refresh Subscription")
        finished = subs_utils.refresh_active_users_subscription(user_ids=[request.user.id], active_only=False)
        if finished:
            messages.success(request, "Subscription Has Been Activated!")
        else:
            messages.error(request, "There was an error with your subscription. Please try again.")
        return redirect(user_sub_obj.get_absolute_url())
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": user_sub_obj})

@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("Refresh Subscription")
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = billing.cancel_subscription(
                user_sub_obj.stripe_id, 
                reason="User wanted to end",
                feedback="other",
                cancel_at_period_end=True,
                raw=False)
            for key, value in sub_data.items():
                setattr(user_sub_obj, key, value)
            user_sub_obj.save()
            messages.success(request, "Subscription Cancelled")
            return redirect(user_sub_obj.get_absolute_url())
    if user_sub_obj.stripe_id:
        sub_data = billing.get_subscription(user_sub_obj.stripe_id, raw=False)
    return render(request, 'subscriptions/user_cancel_view.html', {"subscription": user_sub_obj})


def subscription_price_view(request, interval = "month"):
    qs = SubscriptionPrice.objects.filter(featured=True)
    inv_mo = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoices.YEARLY
    object_list = qs.filter(interval = inv_mo)
    url_path_name = "pricing_interval" 
    mo_url = reverse(url_path_name, kwargs={"interval": inv_mo})
    yr_url = reverse(url_path_name, kwargs={"interval": inv_yr})
    active = inv_mo
    if interval == inv_yr:
        active = inv_yr
        object_list = qs.filter(interval = inv_yr)
    return render(
            request, 'subscriptions/pricing.html', 
            {
                "object_list": object_list,
                "mo_url": mo_url,
                "yr_url": yr_url, 
                "active": active
            }
        )