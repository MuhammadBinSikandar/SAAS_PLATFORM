from django.core.management.base import BaseCommand, CommandParser
from typing import Any
from subscriptions import utils as sub_utils
from customers.models import Customer 
import helpers.billing as billing


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--clear-dangling", action="store_true", default=False)

    def handle(self, *args:Any, **options:Any):
        print(options)
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing Dangling Subscriptions not in use in stripe account")
            sub_utils.clear_dangling_subs()
        else:
            print("Syncing active Subscriptions")
            print("Done")