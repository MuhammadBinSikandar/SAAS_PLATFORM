from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings
import helpers.billing as billing
import stripe
from decouple import config
from django.urls import reverse

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS = True

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="", cast=str)


SUBSCRIPTION_PERMISSIONS = [
            ("pro", "Pro Perm"),
            ("standard","Standard Perm"),
            ("basic", "Basic Perm"),
            ("basic_ai", "Basic AI Perm"),
        ] 

# Create your models here.
class Subscription(models.Model):
    """
    Subscription Plan = Stripe Product
    """
    name = models.CharField(max_length=120)
    subtitle = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group) # one-to-one
    permissions =  models.ManyToManyField(Permission, limit_choices_to={
        "content_type__app_label": "subscriptions", "codename__in": [x[0]for x in SUBSCRIPTION_PERMISSIONS]
        }
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    order = models.IntegerField(default=-1, help_text='Ordering on Django pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Django pricing page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(help_text="Features for pricing, seperated by new line", blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['order', 'featured', '-updated']
        permissions = SUBSCRIPTION_PERMISSIONS

    def get_features_as_list(self):
        if not self.features:
            return []
        return [x.strip() for x in self.features.split("\n")]

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = billing.create_product(
                    name=self.name, 
                    metadata={
                        "subscription_plan_id": self.id
                    }, 
                    raw=False
                )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
                    

class SubscriptionPrice(models.Model):
    """
    Subscription Price = Stripe Price
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120, 
                                default=IntervalChoices.MONTHLY, 
                                choices=IntervalChoices.choices
                            )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text='Ordering on Django pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Django pricing page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subscription__order', 'order', 'featured', '-updated']

    def get_checkout_url(self):
        return reverse("sub-price-checkout", 
            kwargs = {"price_id": self.id}  
            )

    @property
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_as_list()
    
    @property
    def display_sub_name(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.name

    @property
    def display_sub_subtitle(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.subtitle
    
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        """
        remove decimal places
        """
        return int(self.price * 100)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    def save(self, *args, **kwargs):
        if (not self.stripe_id and 
            self.product_stripe_id is not None):
            stripe_id = billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={
                        "subscription_plan_price_id": self.id
                },
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELLED = "cancelled", "Cancelled"
    INCOMPLETE = "incomplete", "Incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete Expired"
    PAST_DUE = "past_due", "Past Due"
    TRIALING = "trialing", "Trialing"
    UNPAID = "unpaid", "Unpaid"
    PAUSED = "paused", "Paused"

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # one to one relationship with the user
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True) # foreign key relationship with the subscription
    active = models.BooleanField(default=True) # boolean field to check if the subscription is active or not
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    user_cancelled = models.BooleanField(default=False) # boolean field to check if the user has cancelled the subscription
    current_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True) # datetime field to store the start date of the current period
    current_period_end = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True) # datetime field to store the end date of the current period 
    original_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True) # datetime field to store the start date of the original period
    status = models.CharField(max_length=120, choices=SubscriptionStatus.choices, blank=True, null=True) # char field to store the status of the subscription
    cancel_at_period_end = models.BooleanField(default=False) # boolean field to check if the subscription is cancelled at the end of the period

    def get_absolute_url(self):
        return reverse("user_subscription")
    
    def get_cancel_url(self):
        return reverse("user_subscription_cancel")

    @property
    def is_active_status(self):
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    @property
    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name

    def serialize(self):
        return {
            "plan_name": self.plan_name,
            "status": self.status,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,
        }

    @property
    def billing_cycle_anchor(self):
        """
        Optional Delay to start the new subscription
        """
        if not self.current_period_end:
            return None    
        return int(self.current_period_end.timestamp())

    def save(self, *args, **kwargs):
        if (self.original_period_start is None and 
            self.current_period_start is not None):
            self.original_period_start = self.current_period_start
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.subscription}"


def user_sub_post_save(sender, instance, created, *args, **kwargs):
    user_sub_instance = instance # instance of UserSubscription
    user = user_sub_instance.user # user instance
    subscription_obj = user_sub_instance.subscription # subscription instance
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all() # fetching all the groups of the subscription
        groups_ids = groups.values_list("id", flat=True) # fetching all the ids of the groups
    if not ALLOW_CUSTOM_GROUPS: # if custom groups are not allowed
        user.groups.set(groups_ids) # setting the groups of the user to the groups of the subscription
    else:
        subs_qs = Subscription.objects.filter(active=True) # fetching all the active subscriptions except the current subscription
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True) # fetching all the groups of the active subscriptions
        subs_groups_set = set(subs_groups) # converting the groups to a set
        # groups_ids = groups.values_list("id", flat=True) # fetches all the ids of the groups
        current_groups = user.groups.all().values_list("id", flat=True) # fetches all the ids of the current groups
        groups_ids_set = set(groups_ids) # converting the groups ids to a set
        current_groups_set = set(current_groups) - subs_groups_set # subtracting the groups of the active subscriptions from the current groups
        final_groups_ids = list(groups_ids_set | current_groups_set) # union of the two sets
        user.groups.set(final_groups_ids) # setting the groups of the user to the final groups ids

post_save.connect(user_sub_post_save, sender=UserSubscription) # connecting the post_save signal with the user_sub_post_save function