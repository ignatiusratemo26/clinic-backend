
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mydocBackend.settings')

application = get_wsgi_application()
# to connect it to the vercel application
app = application