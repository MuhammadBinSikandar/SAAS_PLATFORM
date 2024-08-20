from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
            ("pro", "Pro Perm"),
            ("standard","Standard Perm"),
            ("basic", "Basic Perm"),
            ("basic_ai", "Basic AI Perm"),
        ] 

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, limit_choices_to={
        "content_type__app_label": "subscriptions",
        "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
        }
    )
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # one to one relationship with the user
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True) # foreign key relationship with the subscription
    active = models.BooleanField(default=True) # boolean field to check if the subscription is active or not

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