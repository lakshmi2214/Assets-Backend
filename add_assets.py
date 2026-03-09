import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')
django.setup()

from assets.models import Asset, Location

# Check existing
print(f"Existing Assets: {Asset.objects.count()}")
print(f"Existing Locations: {Location.objects.count()}")

# Create locations if they don't exist
locations_data = [
    {'name': 'Main Office', 'description': 'Head office location'},
    {'name': 'Warehouse A', 'description': 'Storage facility A'},
    {'name': 'Branch Office', 'description': 'Secondary office'},
]

for loc_data in locations_data:
    loc, created = Location.objects.get_or_create(
        name=loc_data['name'],
        defaults={'description': loc_data['description']}
    )
    if created:
        print(f"[+] Created location: {loc.name}")
    else:
        print(f"[*] Location already exists: {loc.name}")

# Create assets if they don't exist
locations = Location.objects.all()
main_office = locations.first()

assets_data = [
    {'name': 'Laptop Dell XPS', 'serial': 'DELL-001', 'description': 'High-performance laptop for development'},
    {'name': 'Sony A6400 Camera', 'serial': 'SONY-CAM-001', 'description': 'Professional mirrorless camera'},
    {'name': 'Canon 5D Mark IV', 'serial': 'CANON-001', 'description': 'Full-frame DSLR camera'},
    {'name': 'Drone DJI Mavic 3', 'serial': 'DJI-001', 'description': 'Professional drone with 4K camera'},
    {'name': 'MacBook Pro 16', 'serial': 'MAC-001', 'description': 'MacBook Pro 16 inch M2 Max'},
    {'name': 'Audio Equipment Set', 'serial': 'AUDIO-001', 'description': 'Professional microphone and mixer'},
]

for asset_data in assets_data:
    asset, created = Asset.objects.get_or_create(
        name=asset_data['name'],
        defaults={
            'serial_number': asset_data['serial'],
            'description': asset_data['description'],
            'location': main_office,
            'available': True
        }
    )
    if created:
        print(f"[+] Created asset: {asset.name}")
    else:
        print(f"[*] Asset already exists: {asset.name}")

print(f"\nFinal count - Assets: {Asset.objects.count()}, Locations: {Location.objects.count()}")
