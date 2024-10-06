# mydoc_api/management/commands/sync_firebase_users.py
from django.core.management.base import BaseCommand
from mydoc_api.utils import sync_firebase_users

class Command(BaseCommand):
    help = 'Sync Firebase users with Django'

    def handle(self, *args, **kwargs):
        sync_firebase_users()
        self.stdout.write(self.style.SUCCESS('Successfully synced Firebase users'))