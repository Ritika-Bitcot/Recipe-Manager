# Manual Testing Guide for Authentication Bypass

## 🧪 Testing Development vs Production Modes

### **Test 1: Development Mode (Bypass Enabled)**

**Step 1: Start Server with Bypass**
```bash
cd /home/bitcot/Desktop/Recipe-Manager

AUTH_BYPASS_EMAIL=test@example.com \
SECRET_KEY=test-secret-key \
ALLOWED_ORIGINS='["http://localhost:3000"]' \
ENVIRONMENT=development \
python -m src.api.app
```

**Step 2: Test Endpoints (in new terminal)**
```bash
# These should work WITHOUT any auth headers
curl -X GET http://localhost:5000/api/recipes
curl -X GET http://localhost:5000/api/auth/me

# Expected Results:
# ✅ Status: 200 OK
# ✅ No Authorization header required
# ✅ Server logs show "Bypassing authentication for development"
```

**Step 3: Test with Auth Header (should still work)**
```bash
# Even with auth header, bypass should work
curl -X GET http://localhost:5000/api/recipes \
  -H "Authorization: Bearer fake-token"

# Expected: 200 OK (bypass takes precedence)
```

---

### **Test 2: Production Mode (Bypass Disabled)**

**Step 1: Stop Server and Restart Without Bypass**
```bash
# Stop server (Ctrl+C) and restart without AUTH_BYPASS_EMAIL
SECRET_KEY=test-secret-key \
ALLOWED_ORIGINS='["http://localhost:3000"]' \
ENVIRONMENT=production \
python -m src.api.app
```

**Step 2: Test Endpoints Without Auth (should fail)**
```bash
# These should FAIL without auth headers
curl -X GET http://localhost:5000/api/recipes
curl -X GET http://localhost:5000/api/auth/me

# Expected Results:
# ❌ Status: 401 Unauthorized
# ❌ Error: "Authorization token required"
```

**Step 3: Test with Valid JWT Token**
```bash
# First, login to get JWT token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "your-password-here"
  }'

# Then use the JWT token from response
curl -X GET http://localhost:5000/api/recipes \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Expected: 200 OK
```

---

### **Test 3: Automated Testing**

**Run the automated test script:**
```bash
python3 test_production_vs_development.py
```

This will automatically test both modes and show you the results.

---

## 📊 Expected Results Summary

| **Mode** | **AUTH_BYPASS_EMAIL** | **No Auth Header** | **With Auth Header** | **Expected Behavior** |
|----------|----------------------|-------------------|---------------------|---------------------|
| **Development** | `test@example.com` | ✅ 200 OK | ✅ 200 OK | Bypass works |
| **Production** | Not set | ❌ 401 Unauthorized | ✅ 200 OK (if valid JWT) | Normal JWT auth |

---

## 🔍 What to Look For

### **Development Mode (Bypass Enabled)**
- ✅ All requests work without Authorization header
- ✅ Server logs show "Bypassing authentication for development"
- ✅ User ID 5 (test@example.com) is used automatically
- ✅ No JWT token validation occurs

### **Production Mode (Bypass Disabled)**
- ❌ Requests without Authorization header fail with 401
- ✅ Requests with valid JWT token work normally
- ✅ Normal JWT authentication flow
- ✅ No bypass messages in logs

---

## 🚨 Troubleshooting

### **If Development Mode Fails:**
1. Check that `AUTH_BYPASS_EMAIL=test@example.com` is set
2. Verify user `test@example.com` exists in database
3. Check server logs for error messages

### **If Production Mode Fails:**
1. Ensure `AUTH_BYPASS_EMAIL` is not set
2. Verify JWT token is valid and not expired
3. Check that user exists and is active

### **Common Issues:**
- **Port 5000 in use**: Kill existing processes with `pkill -f "python.*src.api.app"`
- **Database connection**: Ensure database is running and accessible
- **User not found**: Verify bypass user exists in database

---

## 🎯 Success Criteria

Your authentication bypass is working correctly if:

1. **Development Mode**: All endpoints work without auth headers
2. **Production Mode**: All endpoints require valid JWT tokens
3. **Security**: Bypass only works when `AUTH_BYPASS_EMAIL` is set
4. **Logging**: Appropriate bypass messages appear in logs
5. **User Context**: Correct user is used when bypass is enabled

If all these criteria are met, your implementation is working perfectly! 🎉
