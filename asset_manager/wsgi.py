import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')

application = get_wsgi_application()

app = application

# VERCEL AUTO-SETUP: Run migrations and create superuser automatically
# This handles the "relation auth_user does not exist" error without needing a manual link click.
if 'VERCEL' in os.environ:
    try:
        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        
        print("--- Vercel: Starting Auto-Migration ---")
        call_command('migrate')
        print("--- Vercel: Migration Complete ---")
        
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            print("--- Vercel: Creating Superuser 'admin' ---")
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("--- Vercel: Superuser Created ---")
    except Exception as e:
        print(f"--- Vercel Check Setup Error: {e} ---")
