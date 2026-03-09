import requests
import json

try:
    response = requests.get('http://localhost:8000/api/v1/assets/')
    print('Assets API Status:', response.status_code)
    if response.ok:
        assets = response.json()
        print(f'Total assets: {len(assets)}')
        for asset in assets[:3]:
            print(f"  - {asset.get('name')} (ID: {asset.get('id')})")
        if len(assets) > 3:
            print(f"  ... and {len(assets) - 3} more")
except Exception as e:
    print('Error:', str(e))
