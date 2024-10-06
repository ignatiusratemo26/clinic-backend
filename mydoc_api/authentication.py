from django.http import JsonResponse
import firebase_admin
import logging
from firebase_admin import auth
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Profile


logger = logging.getLogger(__name__)

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        id_token = request.headers.get('Authorization')
        if not id_token:
            return JsonResponse({'error': 'Authorization header missing'}, status=400)
        
        if id_token.startswith('Bearer '):
            id_token = id_token.split(' ')[1]

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            profile = Profile.objects.get(firebase_uid=uid)
            user = profile.user
            return (user, None)
        except User.DoesNotExist:
            logger.error('User matching query does not exist')
            raise AuthenticationFailed('User matching query does not exist')
        except auth.InvalidIdTokenError:
            logger.error('Invalid Firebase token')
            return JsonResponse({'error', 'Invalid Firebase token'}, status=401)
        
        except auth.ExpiredIdTokenError:
            logger.error('Expired Firebase token')
            return JsonResponse({'error': 'Expired Firebase token'}, status=401)
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return JsonResponse({'error': 'Internal Server Error'}, status=500)

