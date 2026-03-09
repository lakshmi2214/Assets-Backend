
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')
django.setup()

from assets.models import Asset

print(f"Total Assets: {Asset.objects.count()}")
for asset in Asset.objects.all():
    print(f"Asset: {asset.name}, Image: {asset.image}, ID: {asset.id}")
