import requests
import json

try:
    response = requests.post('http://localhost:8050/api/v1/auth/signup/', json={'username': 'testuser123', 'password': 'testpass123'})
    print('Signup Status:', response.status_code)
    print('Signup Response:', response.text)
    print()

    response2 = requests.post('http://localhost:8050/api/v1/auth/token/', json={'username': 'testuser123', 'password': 'testpass123'})
    print('Token Status:', response2.status_code)
    print('Token Response:', response2.text)
    print()

    # Test assets endpoint
    response3 = requests.get('http://localhost:8050/api/v1/assets/')
    print('Assets Status:', response3.status_code)
    if response3.status_code == 200:
        data = response3.json()
        print('Assets loaded:', len(data), 'items')
    else:
        print('Assets Response:', response3.text)
except Exception as e:
    print('Error:', str(e))
