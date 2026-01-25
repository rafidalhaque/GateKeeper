# 🔐 Email Templates RBAC - Permission-Based Access Control

## ✅ **Implementation Complete**

Email template CRUD operations are now protected with permission-based access control (RBAC) following the plan.md specifications.

---

## 🎯 **Permissions Added**

### **Email Template Permissions:**

| Permission Key | Description | Feature Group |
|----------------|-------------|---------------|
| `email_template.read` | Read email templates | email_templates |
| `email_template.create` | Create email templates | email_templates |
| `email_template.update` | Update email templates | email_templates |
| `email_template.delete` | Delete email templates | email_templates |
| `email_template.test` | Send test emails | email_templates |

---

## 🔧 **Implementation Details**

### **1. Permission Definitions**

**File**: `app/cli.py`

Added to `seed-permissions` command:
```python
# Email Templates
('email_template.read', 'Read email templates', 'email_templates'),
('email_template.create', 'Create email templates', 'email_templates'),
('email_template.update', 'Update email templates', 'email_templates'),
('email_template.delete', 'Delete email templates', 'email_templates'),
('email_template.test', 'Send test emails', 'email_templates'),
```

### **2. Route Protection**

**File**: `app/routes/email_templates.py`

All API endpoints now use `@permission_required` decorator:

```python
@bp.route('/api/email-templates', methods=['GET'])
@permission_required('email_template.read')
def list_templates():
    """List all templates - requires read permission"""

@bp.route('/api/email-templates', methods=['POST'])
@permission_required('email_template.create')
def create_template():
    """Create template - requires create permission"""

@bp.route('/api/email-templates/<id>', methods=['PUT'])
@permission_required('email_template.update')
def update_template(template_id):
    """Update template - requires update permission"""

@bp.route('/api/email-templates/<id>', methods=['DELETE'])
@permission_required('email_template.delete')
def delete_template(template_id):
    """Delete template - requires delete permission"""

@bp.route('/api/email-templates/send-test', methods=['POST'])
@permission_required('email_template.test')
def send_test_email():
    """Send test email - requires test permission"""
```

### **3. Default Role Assignments**

**File**: `app/cli.py`

Updated **Event Admin** role to include email template permissions:
```python
event_admin_permissions = [
    # ...existing permissions...
    'email_template.read', 
    'email_template.create', 
    'email_template.update', 
    'email_template.delete', 
    'email_template.test',
    # ...other permissions...
]
```

---

## 👥 **Role Capabilities**

### **Super Admin**
✅ **All Permissions** - Bypasses all permission checks
- Can do everything without restriction

### **Event Admin**
✅ **Full Email Template Access**:
- ✅ Read email templates
- ✅ Create email templates
- ✅ Update email templates
- ✅ Delete email templates
- ✅ Send test emails

### **Booth Manager**
❌ **No Email Template Access**:
- Limited to check-in operations only
- Cannot access email templates

---

## 🚀 **Setup Instructions**

### **1. Seed Permissions (First Time Setup):**
```bash
flask --app run.py seed-permissions
```

**Expected Output:**
```
Seeding permissions...
  Created permission: email_template.read
  Created permission: email_template.create
  Created permission: email_template.update
  Created permission: email_template.delete
  Created permission: email_template.test
Permissions seeded successfully!
```

### **2. Seed Roles (First Time Setup):**
```bash
flask --app run.py seed-roles
```

**Expected Output:**
```
Seeding default roles...
  Created role: Super Admin
  Created role: Event Admin
  Created role: Booth Manager
Roles seeded successfully!
```

### **3. Verify Permissions:**
```bash
flask --app run.py shell
```
```python
from app.models.auth import Permission
templates_perms = Permission.query.filter(
    Permission.key.like('email_template.%')
).all()
for p in templates_perms:
    print(f"{p.key} - {p.description}")
```

---

## 🔒 **Access Control Behavior**

### **Authenticated User with Permissions:**
```
User: event_admin@example.com
Role: Event Admin
Permissions: email_template.read, email_template.create, etc.

Request: GET /api/email-templates
Response: 200 OK - [list of templates]
```

### **Authenticated User without Permissions:**
```
User: booth_manager@example.com
Role: Booth Manager
Permissions: attendance.read, attendance.mark

Request: GET /api/email-templates
Response: 403 Forbidden
{
  "error": "Insufficient permissions"
}
```

### **Unauthenticated User:**
```
Request: GET /api/email-templates
Response: 401 Unauthorized
{
  "error": "Authentication required"
}
```

### **Super Admin (Bypasses All Checks):**
```
User: super_admin@example.com
Role: Super Admin
is_super_admin: True

Request: ANY /api/email-templates/*
Response: Success (permission checks bypassed)
```

---

## 📋 **Permission Checking Logic**

### **How it Works:**

1. **Request arrives** at protected endpoint
2. **Decorator checks**:
   - ✅ Is user authenticated?
   - ✅ Is user super admin? → **Allow (bypass)**
   - ✅ Does user have required permission? → **Allow**
   - ❌ Otherwise → **Deny (403)**

### **Code Flow:**
```python
@permission_required('email_template.create')
def create_template():
    # 1. Get current user from session/JWT
    # 2. Check if super admin (bypass)
    # 3. Check if user.has_permission('email_template.create')
    # 4. If yes, proceed; if no, return 403
    # 5. Execute function
```

---

## 🎨 **Frontend Implications**

### **UI Elements Should Check Permissions:**

```javascript
// Example: Hide/show create button based on permissions
const userPermissions = getUserPermissions(); // from session

if (userPermissions.includes('email_template.create')) {
    showCreateButton();
} else {
    hideCreateButton();
}
```

### **API Error Handling:**

```javascript
try {
    const response = await fetch('/api/email-templates', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.status === 403) {
        showAlert('You do not have permission to view templates', 'error');
    } else if (response.status === 401) {
        redirectToLogin();
    }
} catch (error) {
    showAlert('Error loading templates', 'error');
}
```

---

## 🔄 **Updating Existing Users**

### **Grant Email Template Permissions to Existing Event Admins:**

```bash
flask --app run.py shell
```

```python
from app.models import db
from app.models.auth import Role, Permission, AdminUser

# Get Event Admin role
event_admin = Role.query.filter_by(name='Event Admin').first()

# Get email template permissions
template_perms = Permission.query.filter(
    Permission.key.like('email_template.%')
).all()

# Add permissions to role
for perm in template_perms:
    if perm not in event_admin.permissions:
        event_admin.permissions.append(perm)

db.session.commit()
print(f"Added {len(template_perms)} permissions to Event Admin role")
```

---

## ✅ **Testing Permission Enforcement**

### **Test 1: Super Admin (Should Always Work)**
```bash
curl -X GET http://localhost:5000/api/email-templates \
  -H "Authorization: Bearer <super_admin_jwt>" \
  -H "Content-Type: application/json"

# Expected: 200 OK with template list
```

### **Test 2: Event Admin (Should Work)**
```bash
curl -X POST http://localhost:5000/api/email-templates \
  -H "Authorization: Bearer <event_admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","type":"custom","subject":"Test"}'

# Expected: 201 Created
```

### **Test 3: Booth Manager (Should Fail)**
```bash
curl -X GET http://localhost:5000/api/email-templates \
  -H "Authorization: Bearer <booth_manager_jwt>" \
  -H "Content-Type: application/json"

# Expected: 403 Forbidden
# {"error": "Insufficient permissions"}
```

### **Test 4: No Auth (Should Fail)**
```bash
curl -X GET http://localhost:5000/api/email-templates

# Expected: 401 Unauthorized
# {"error": "Authentication required"}
```

---

## 📊 **Permission Matrix**

| Action | Endpoint | Super Admin | Event Admin | Booth Manager |
|--------|----------|-------------|-------------|---------------|
| View Templates | GET /api/email-templates | ✅ | ✅ | ❌ |
| Create Template | POST /api/email-templates | ✅ | ✅ | ❌ |
| Update Template | PUT /api/email-templates/{id} | ✅ | ✅ | ❌ |
| Delete Template | DELETE /api/email-templates/{id} | ✅ | ✅ | ❌ |
| Send Test Email | POST /api/email-templates/send-test | ✅ | ✅ | ❌ |

---

## 🎯 **Best Practices**

### **1. Principle of Least Privilege**
- Users get only permissions they need
- Booth Managers can't modify templates
- Event Admins have full template access

### **2. Granular Permissions**
- Separate read/write permissions
- Test email has its own permission
- Can be customized per role

### **3. Audit Trail**
- All permission checks logged
- Failed access attempts tracked
- User actions tied to permissions

---

## 🎊 **Summary**

✅ **Permissions Defined** - 5 email template permissions
✅ **Routes Protected** - All CRUD endpoints secured
✅ **Roles Updated** - Event Admin has full access
✅ **Super Admin Bypass** - Unrestricted access maintained
✅ **Booth Manager Restricted** - No template access
✅ **Documentation Complete** - Full guide provided

**Email templates are now secured with enterprise-grade RBAC!** 🔐

---

## 📚 **Related Documentation**

- `plan.md` - Overall system architecture
- `EMAIL_TEMPLATES_IMPLEMENTATION.md` - Feature implementation
- `EMAIL_TEMPLATES_FIXED.md` - Bug fixes and migration

---

## 🚀 **Next Steps**

1. **Run permission seed**: `flask --app run.py seed-permissions`
2. **Run role seed**: `flask --app run.py seed-roles`
3. **Test access control**: Try different user roles
4. **Update frontend**: Add permission checks in UI

**Your email templates are now production-ready with proper access control!** 🎉
