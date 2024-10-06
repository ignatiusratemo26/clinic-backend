from django.core.management.base import BaseCommand
from mydoc_api.models import Profile
from django.db import models

class Command(BaseCommand):
    help = 'Find and handle duplicate firebase_uid in Profile model'

    def handle(self, *args, **kwargs):
        # Find duplicates based on firebase_uid
        duplicate_uids = Profile.objects.values('firebase_uid').annotate(count=models.Count('firebase_uid')).filter(count__gt=1)

        if duplicate_uids.exists():
            self.stdout.write(self.style.WARNING('Found duplicate firebase_uid entries:'))
            for duplicate in duplicate_uids:
                firebase_uid = duplicate['firebase_uid']
                profiles = Profile.objects.filter(firebase_uid=firebase_uid)
                self.stdout.write(f"firebase_uid: {firebase_uid} - {profiles.count()} duplicates")
                
                # Handle duplicates: keep the first one and delete the rest
                for i, profile in enumerate(profiles):
                    if i == 0:
                        self.stdout.write(self.style.SUCCESS(f"Keeping profile: {profile.user.username}"))
                    else:
                        self.stdout.write(f"Deleting duplicate profile: {profile.user.username}")
                        profile.delete()

            self.stdout.write(self.style.SUCCESS('Duplicate handling complete.'))
        else:
            self.stdout.write(self.style.SUCCESS('No duplicate firebase_uid found.'))
