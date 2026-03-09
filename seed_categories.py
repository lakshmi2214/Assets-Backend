
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')
django.setup()

from assets.models import Category

categories = [
    'Tripods',
    'Camera',
    'Lights',
    'Mics',
    'Camera Holder'
]

for cat_name in categories:
    cat, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f"Created category: {cat_name}")
    else:
        print(f"Category already exists: {cat_name}")

print("Categories seeded successfully.")
