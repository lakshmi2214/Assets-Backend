
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')
django.setup()

from assets.models import Category, SubCategory

# Define the structure: Parent Category -> List of Subcategories
hierarchy = {
    'Mics': ['Wireless Mic', 'Podcast Mic', 'Condenser', 'Dynamic'],
    'Lights': ['Light with Stand', 'LED Panel', 'Softbox', 'Spotlight']
}

for parent_name, subs in hierarchy.items():
    # Ensure parent category exists
    parent, _ = Category.objects.get_or_create(name=parent_name)
    print(f"Checking/Creating Parent: {parent_name}")
    
    for sub_name in subs:
        sub, created = SubCategory.objects.get_or_create(category=parent, name=sub_name)
        if created:
            print(f"  - Created subcategory: {sub_name}")
        else:
            print(f"  - Subcategory exists: {sub_name}")

print("Sub-categories seeded successfully.")
