"""
Add sample tasks to demo user
"""
import requests

BASE_URL = "http://localhost:8001"

# Login first
print("Logging in as demo user...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "demo@todoapp.com", "password": "demo12345"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

data = login_response.json()
user_id = data["user"]["id"]
token = data["token"]
print(f"Logged in as: {data['user']['email']}")
print(f"User ID: {user_id}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sample tasks without emojis
sample_tasks = [
    {
        "title": "Welcome to your Todo App!",
        "description": "This is your first task. Click the checkbox to mark it as complete!"
    },
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread, cheese, fruits, vegetables"
    },
    {
        "title": "Finish project report",
        "description": "Complete the Q4 analysis and prepare presentation slides"
    },
    {
        "title": "Call dentist for appointment",
        "description": "Schedule regular checkup for next month"
    },
    {
        "title": "Plan weekend trip",
        "description": "Research hotels and activities for beach vacation"
    },
    {
        "title": "Exercise for 30 minutes",
        "description": "Morning jog or home workout routine"
    },
    {
        "title": "Read 2 chapters of book",
        "description": "Continue reading Atomic Habits"
    }
]

print(f"\nCreating {len(sample_tasks)} sample tasks...")
created_count = 0

for i, task in enumerate(sample_tasks, 1):
    response = requests.post(
        f"{BASE_URL}/api/{user_id}/tasks",
        json=task,
        headers=headers
    )

    if response.status_code == 201:
        created_count += 1
        print(f"[{i}/{len(sample_tasks)}] Created: {task['title']}")
    else:
        print(f"[{i}/{len(sample_tasks)}] Failed: {task['title']}")

print(f"\nSuccessfully created {created_count}/{len(sample_tasks)} tasks")

# Mark first 2 tasks as complete
print("\nMarking some tasks as complete...")
response = requests.get(
    f"{BASE_URL}/api/{user_id}/tasks",
    headers=headers
)

if response.status_code == 200:
    tasks = response.json()
    for task in tasks[:2]:
        patch_response = requests.patch(
            f"{BASE_URL}/api/{user_id}/tasks/{task['id']}/complete",
            headers=headers
        )
        if patch_response.status_code == 200:
            print(f"Completed: {task['title']}")

print("\n" + "="*60)
print("TEST USER READY!")
print("="*60)
print("Email:    demo@todoapp.com")
print("Password: demo12345")
print("="*60)
print("\nOpen http://localhost:3000/login and use these credentials")
print("You will see 7 tasks (2 completed, 5 active)")
print("="*60)
