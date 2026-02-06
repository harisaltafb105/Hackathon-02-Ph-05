"""
Test Authentication Flow
Tests registration and login with the real backend
Run: uv run python test-auth.py
"""

import requests
import time

BACKEND_URL = 'http://localhost:8000'

def test_auth_flow():
    print('\n[TEST] Testing Real Authentication Flow\n')
    print('=' * 50)

    # Test 1: Register a new user
    print('\n[1] Testing User Registration:')
    test_email = f'testuser{int(time.time())}@example.com'
    test_password = 'password123'
    test_name = 'Test User'

    try:
        response = requests.post(
            f'{BACKEND_URL}/auth/register',
            json={
                'email': test_email,
                'password': test_password,
                'name': test_name,
            }
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 201:
            data = response.json()
            print(f'   [OK] User created: {data["user"]["email"]}')
            print(f'   [OK] User ID: {data["user"]["id"]}')
            print(f'   [OK] Token received: {data["token"][:50]}...')
            user_id = data["user"]["id"]
            token = data["token"]
        else:
            print(f'   [FAIL] Registration failed: {response.json()}')
            return
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')
        return

    # Test 2: Try to register with same email (should fail)
    print('\n[2] Testing Duplicate Email Registration (should fail):')
    try:
        response = requests.post(
            f'{BACKEND_URL}/auth/register',
            json={
                'email': test_email,
                'password': test_password,
                'name': test_name,
            }
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 400:
            data = response.json()
            print(f'   [OK] Correctly rejected: {data["detail"]}')
        else:
            print(f'   [WARN] Expected 400 but got {response.status_code}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 3: Login with correct credentials
    print('\n[3] Testing Login with Correct Credentials:')
    try:
        response = requests.post(
            f'{BACKEND_URL}/auth/login',
            json={
                'email': test_email,
                'password': test_password,
            }
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print(f'   [OK] Login successful: {data["user"]["email"]}')
            print(f'   [OK] Token received: {data["token"][:50]}...')
            login_token = data["token"]
        else:
            print(f'   [FAIL] Login failed: {response.json()}')
            return
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')
        return

    # Test 4: Login with wrong password (should fail)
    print('\n[4] Testing Login with Wrong Password (should fail):')
    try:
        response = requests.post(
            f'{BACKEND_URL}/auth/login',
            json={
                'email': test_email,
                'password': 'wrongpassword',
            }
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 401:
            data = response.json()
            print(f'   [OK] Correctly rejected: {data["detail"]}')
        else:
            print(f'   [WARN] Expected 401 but got {response.status_code}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 5: Login with non-existent email (should fail)
    print('\n[5] Testing Login with Non-existent Email (should fail):')
    try:
        response = requests.post(
            f'{BACKEND_URL}/auth/login',
            json={
                'email': 'nonexistent@example.com',
                'password': test_password,
            }
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 401:
            data = response.json()
            print(f'   [OK] Correctly rejected: {data["detail"]}')
        else:
            print(f'   [WARN] Expected 401 but got {response.status_code}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 6: Use token to access protected endpoint
    print('\n[6] Testing Token with Protected Endpoint:')
    try:
        response = requests.get(
            f'{BACKEND_URL}/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {login_token}'}
        )
        print(f'   [OK] Status: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print(f'   [OK] Tasks retrieved: {len(data)} tasks')
            print(f'   [OK] Token is valid and working')
        else:
            print(f'   [WARN] Expected 200 but got {response.status_code}')
            print(f'   Response: {response.json()}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    print('\n' + '=' * 50)
    print('\n[SUCCESS] Authentication Flow Test Complete!\n')
    print(f'Test User Created:')
    print(f'  Email: {test_email}')
    print(f'  Password: {test_password}')
    print(f'  User ID: {user_id}')
    print(f'\nYou can use these credentials to login via the frontend!\n')

if __name__ == '__main__':
    test_auth_flow()
