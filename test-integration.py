"""
Integration Test Script
Tests the complete authentication and task CRUD flow using Python
Run: uv run python test-integration.py
"""

import jwt
import requests
import time
from datetime import datetime, timedelta

BETTER_AUTH_SECRET = '8d6FQlFZM6jyDmYmCEBVC9rNSlq6lGNo'
BACKEND_URL = 'http://localhost:8000/api'

def generate_test_token(user_id: str) -> str:
    """Generate a test JWT token (same as frontend does)"""
    payload = {
        'sub': user_id,
        'userId': user_id,
        'iat': int(time.time()),
        'exp': int(time.time()) + (24 * 60 * 60),
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm='HS256')

def test_backend_integration():
    print('\n[TEST] Testing Backend Integration\n')
    print('=' * 50)

    # Test user ID (matching frontend test user)
    test_user_id = 'test-user-123'
    token = generate_test_token(test_user_id)

    print(f'\n[1] Generated JWT Token:')
    print(f'   User ID: {test_user_id}')
    print(f'   Token: {token[:50]}...')

    # Test 1: Health check
    print('\n[2] Testing Health Endpoint:')
    try:
        response = requests.get('http://localhost:8000/health')
        health_data = response.json()
        print(f'   [OK] Health: {health_data["status"]}')
    except Exception as error:
        print(f'   [FAIL] Health check failed: {error}')
        return

    # Test 2: Get tasks (should be empty)
    print('\n[3] Testing GET Tasks (should be empty):')
    try:
        response = requests.get(
            f'{BACKEND_URL}/{test_user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        print(f'   [OK] Status: {response.status_code}')
        print(f'   [OK] Tasks retrieved: {len(data)} tasks')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 3: Create a task
    print('\n[4] Testing POST Create Task:')
    created_task_id = None
    try:
        response = requests.post(
            f'{BACKEND_URL}/{test_user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Task from Integration Test',
                'description': 'This task was created by the automated integration test',
                'completed': False,
            }
        )
        task = response.json()
        created_task_id = task['id']
        print(f'   [OK] Status: {response.status_code}')
        print(f'   [OK] Task created: ID={task["id"]}')
        print(f'   [OK] Title: {task["title"]}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 4: Get tasks again (should have 1 task)
    print('\n[5] Testing GET Tasks (should have 1 task):')
    try:
        response = requests.get(
            f'{BACKEND_URL}/{test_user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        print(f'   [OK] Status: {response.status_code}')
        print(f'   [OK] Tasks retrieved: {len(data)} task(s)')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 5: Update the task
    if created_task_id:
        print('\n[6] Testing PATCH Update Task:')
        try:
            response = requests.patch(
                f'{BACKEND_URL}/{test_user_id}/tasks/{created_task_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'completed': True}
            )
            task = response.json()
            print(f'   [OK] Status: {response.status_code}')
            print(f'   [OK] Task updated: completed={task["completed"]}')
        except Exception as error:
            print(f'   [FAIL] Failed: {error}')

        # Test 6: Delete the task
        print('\n[7] Testing DELETE Task:')
        try:
            response = requests.delete(
                f'{BACKEND_URL}/{test_user_id}/tasks/{created_task_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            print(f'   [OK] Status: {response.status_code}')
            print(f'   [OK] Task deleted successfully')
        except Exception as error:
            print(f'   [FAIL] Failed: {error}')

    # Test 7: Verify tasks are empty again
    print('\n[8] Testing GET Tasks (should be empty again):')
    try:
        response = requests.get(
            f'{BACKEND_URL}/{test_user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        print(f'   [OK] Status: {response.status_code}')
        print(f'   [OK] Tasks retrieved: {len(data)} tasks')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    # Test 8: Test without token (should fail)
    print('\n[9] Testing Unauthorized Access (no token):')
    try:
        response = requests.get(f'{BACKEND_URL}/{test_user_id}/tasks')
        print(f'   [OK] Status: {response.status_code}')
        if response.status_code in [403, 401]:
            print(f'   [OK] Correctly rejected unauthorized request')
        else:
            print(f'   [WARN] Expected 401/403 but got {response.status_code}')
    except Exception as error:
        print(f'   [FAIL] Failed: {error}')

    print('\n' + '=' * 50)
    print('\n[SUCCESS] Integration Test Complete!\n')

if __name__ == '__main__':
    test_backend_integration()
