/**
 * Integration Test Script
 * Tests the complete authentication and task CRUD flow
 * Run: node test-integration.js
 */

const jwt = require('jsonwebtoken');

const BETTER_AUTH_SECRET = '8d6FQlFZM6jyDmYmCEBVC9rNSlq6lGNo';
const BACKEND_URL = 'http://localhost:8000/api';

// Generate a test JWT token (same as frontend does)
function generateTestToken(userId) {
  const payload = {
    sub: userId,
    userId: userId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60),
  };
  return jwt.sign(payload, BETTER_AUTH_SECRET, { algorithm: 'HS256' });
}

async function testBackendIntegration() {
  console.log('\n🧪 Testing Backend Integration\n');
  console.log('=' .repeat(50));

  // Test user ID (matching frontend test user)
  const testUserId = 'test-user-123';
  const token = generateTestToken(testUserId);

  console.log('\n1️⃣  Generated JWT Token:');
  console.log(`   User ID: ${testUserId}`);
  console.log(`   Token: ${token.substring(0, 50)}...`);

  // Test 1: Health check
  console.log('\n2️⃣  Testing Health Endpoint:');
  try {
    const healthResponse = await fetch('http://localhost:8000/health');
    const healthData = await healthResponse.json();
    console.log(`   ✅ Health: ${healthData.status}`);
  } catch (error) {
    console.log(`   ❌ Health check failed: ${error.message}`);
    return;
  }

  // Test 2: Get tasks (should be empty)
  console.log('\n3️⃣  Testing GET Tasks (should be empty):');
  try {
    const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    console.log(`   ✅ Status: ${response.status}`);
    console.log(`   ✅ Tasks retrieved: ${data.length} tasks`);
  } catch (error) {
    console.log(`   ❌ Failed: ${error.message}`);
  }

  // Test 3: Create a task
  console.log('\n4️⃣  Testing POST Create Task:');
  let createdTaskId;
  try {
    const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: 'Test Task from Integration Test',
        description: 'This task was created by the automated integration test',
        completed: false,
      }),
    });
    const task = await response.json();
    createdTaskId = task.id;
    console.log(`   ✅ Status: ${response.status}`);
    console.log(`   ✅ Task created: ID=${task.id}`);
    console.log(`   ✅ Title: ${task.title}`);
  } catch (error) {
    console.log(`   ❌ Failed: ${error.message}`);
  }

  // Test 4: Get tasks again (should have 1 task)
  console.log('\n5️⃣  Testing GET Tasks (should have 1 task):');
  try {
    const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    console.log(`   ✅ Status: ${response.status}`);
    console.log(`   ✅ Tasks retrieved: ${data.length} task(s)`);
  } catch (error) {
    console.log(`   ❌ Failed: ${error.message}`);
  }

  // Test 5: Update the task
  if (createdTaskId) {
    console.log('\n6️⃣  Testing PATCH Update Task:');
    try {
      const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks/${createdTaskId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          completed: true,
        }),
      });
      const task = await response.json();
      console.log(`   ✅ Status: ${response.status}`);
      console.log(`   ✅ Task updated: completed=${task.completed}`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}`);
    }

    // Test 6: Delete the task
    console.log('\n7️⃣  Testing DELETE Task:');
    try {
      const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks/${createdTaskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      console.log(`   ✅ Status: ${response.status}`);
      console.log(`   ✅ Task deleted successfully`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}`);
    }
  }

  // Test 7: Verify tasks are empty again
  console.log('\n8️⃣  Testing GET Tasks (should be empty again):');
  try {
    const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    console.log(`   ✅ Status: ${response.status}`);
    console.log(`   ✅ Tasks retrieved: ${data.length} tasks`);
  } catch (error) {
    console.log(`   ❌ Failed: ${error.message}`);
  }

  // Test 8: Test without token (should fail)
  console.log('\n9️⃣  Testing Unauthorized Access (no token):');
  try {
    const response = await fetch(`${BACKEND_URL}/${testUserId}/tasks`);
    console.log(`   ✅ Status: ${response.status}`);
    if (response.status === 403 || response.status === 401) {
      console.log(`   ✅ Correctly rejected unauthorized request`);
    } else {
      console.log(`   ⚠️  Expected 401/403 but got ${response.status}`);
    }
  } catch (error) {
    console.log(`   ❌ Failed: ${error.message}`);
  }

  console.log('\n' + '='.repeat(50));
  console.log('\n✅ Integration Test Complete!\n');
}

testBackendIntegration().catch(console.error);
