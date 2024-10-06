# mydoc_api/utils.py
import firebase_admin
from firebase_admin import credentials, auth
from django.contrib.auth.models import User
from .models import Profile


def sync_firebase_users():
    users = auth.list_users().iterate_all()
    for user in users:
        django_user, created = User.objects.get_or_create(username=user.uid, defaults={'email': user.email})
        if created:
            Profile.objects.create(user=django_user, firebase_uid=user.uid)
        else:
            profile = Profile.objects.get(user=django_user)
            profile.firebase_uid = user.uid
            profile.save()