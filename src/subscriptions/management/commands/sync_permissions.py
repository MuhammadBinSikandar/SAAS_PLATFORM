from django.core.management.base import BaseCommand
from typing import Any
from subscriptions.models import Subscription
from subscriptions import utils as sub_utils


class Command(BaseCommand):

    def handle(self, *args:Any, **kwargs:Any):
        sub_utils.sync_subs_groups_permissions()