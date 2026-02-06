"""
Create test user with sample tasks
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def create_test_user():
    """Create demo user and sample tasks"""

    print("=" * 60)
    print("Creating Test User with Sample Tasks")
    print("=" * 60)

    # Step 1: Register user
    print("\n[1/6] Registering test user...")
    register_data = {
        "email": "demo@todoapp.com",
        "password": "demo12345",
        "name": "Demo User"
    }

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data
    )

    if response.status_code == 201:
        data = response.json()
        user_id = data["user"]["id"]
        token = data["token"]
        print(f"   SUCCESS: User created!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Name: {data['user']['name']}")
    elif response.status_code == 409:
        # User already exists, try to login
        print("   User already exists, logging in...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": register_data["email"], "password": register_data["password"]}
        )
        if login_response.status_code == 200:
            data = login_response.json()
            user_id = data["user"]["id"]
            token = data["token"]
            print(f"   SUCCESS: Logged in!")
            print(f"   User ID: {user_id}")
        else:
            print(f"   ERROR: Login failed: {login_response.text}")
            return
    else:
        print(f"   ERROR: Registration failed: {response.text}")
        return

    # Step 2: Create sample tasks
    sample_tasks = [
        {
            "title": "Welcome to your Todo App! 🎉",
            "description": "This is your first task. Click the checkbox to mark it as complete!"
        },
        {
            "title": "Buy groceries 🛒",
            "description": "Milk, eggs, bread, cheese, fruits, vegetables"
        },
        {
            "title": "Finish project report 📊",
            "description": "Complete the Q4 analysis and prepare presentation slides"
        },
        {
            "title": "Call dentist for appointment 🦷",
            "description": "Schedule regular checkup for next month"
        },
        {
            "title": "Plan weekend trip ✈️",
            "description": "Research hotels and activities for beach vacation"
        },
        {
            "title": "Exercise for 30 minutes 💪",
            "description": "Morning jog or home workout routine"
        },
        {
            "title": "Read 2 chapters of book 📚",
            "description": "Continue reading 'Atomic Habits'"
        }
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n[2/6] Creating {len(sample_tasks)} sample tasks...")
    created_count = 0

    for i, task in enumerate(sample_tasks, 1):
        response = requests.post(
            f"{BASE_URL}/api/{user_id}/tasks",
            json=task,
            headers=headers
        )

        if response.status_code == 201:
            created_count += 1
            task_data = response.json()
            print(f"   [{i}/{len(sample_tasks)}] Created: {task['title']}")
        else:
            print(f"   [{i}/{len(sample_tasks)}] Failed: {task['title']} - {response.text}")

    print(f"\n[3/6] Successfully created {created_count}/{len(sample_tasks)} tasks")

    # Step 3: Mark some tasks as complete
    print("\n[4/6] Marking some tasks as complete...")

    # Get all tasks
    response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks",
        headers=headers
    )

    if response.status_code == 200:
        tasks = response.json()
        # Mark first 2 tasks as complete
        for i, task in enumerate(tasks[:2]):
            patch_response = requests.patch(
                f"{BASE_URL}/api/{user_id}/tasks/{task['id']}/complete",
                headers=headers
            )
            if patch_response.status_code == 200:
                print(f"   Completed: {task['title']}")

    print("\n[5/6] Test user setup complete!")

    # Print login credentials
    print("\n" + "=" * 60)
    print("TEST USER CREDENTIALS")
    print("=" * 60)
    print(f"Email:    demo@todoapp.com")
    print(f"Password: demo12345")
    print("=" * 60)

    print("\n[6/6] Ready to test!")
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Click 'Login' (or go to http://localhost:3000/login)")
    print("3. Enter the credentials above")
    print("4. You'll see 7 sample tasks (2 already completed)")
    print("\nEnjoy testing your Todo App! 🎉")
    print("=" * 60)

if __name__ == "__main__":
    create_test_user()
