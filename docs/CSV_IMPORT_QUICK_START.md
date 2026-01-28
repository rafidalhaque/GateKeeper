# CSV Import with Custom Fields - Quick Start

## ✅ Feature Complete

CSV import now fully supports custom fields! Import participants with event-specific data in bulk.

---

## How to Use

### 1️⃣ Configure Custom Fields (Optional)
If your event needs custom data (dietary preferences, t-shirt sizes, etc.):
- Go to **Event Detail** → Click **"Configure Fields & Schedule"**
- Add custom fields
- Save

### 2️⃣ Download CSV Template
- Go to **Event Detail** → Click **"Import CSV"**
- Click **"Download CSV Template"**
- Template includes ALL fields (standard + custom)

### 3️⃣ Fill the CSV
- Open template in Excel/Google Sheets
- Fill participant data
- Include values for custom fields

### 4️⃣ Import
- Upload CSV file
- Wait for import to complete
- Check results

---

## CSV Format

### Solo Mode
```csv
participant_name,participant_email,dietary_preference,emergency_contact
John Doe,john@example.com,Halal,+1234567890
Jane Smith,jane@example.com,Vegetarian,+0987654321
```

### Team Mode
```csv
team_id,team_name,member_name,member_email,player_role
TEAM001,Warriors,Ahmed,ahmed@example.com,Captain
TEAM001,Warriors,Bilal,bilal@example.com,Player
```

---

## Key Features

✅ **Auto-template generation** - Includes your custom fields  
✅ **Smart validation** - Catches errors before import  
✅ **Duplicate detection** - Prevents duplicate emails  
✅ **Error reporting** - Shows which rows failed and why  
✅ **Background processing** - Handles large files  
✅ **Safe rollback** - Automatic rollback on critical errors  

---

## Examples Included

Check the `examples/` folder:
- `solo_mode_with_custom_fields.csv`
- `team_mode_with_custom_fields.csv`

---

## Documentation

- **Full Guide:** `docs/CSV_IMPORT_WITH_CUSTOM_FIELDS.md`
- **Implementation:** `docs/CSV_IMPORT_IMPLEMENTATION_SUMMARY.md`
- **Quick Reference:** This file

---

## Tips

💡 **Always download the template** - It has the correct columns  
💡 **Test with 2-3 rows first** - Verify before bulk import  
💡 **Column names must match exactly** - Use template to avoid typos  
💡 **Empty cells = null** - Leave optional fields blank if needed  

---

## Troubleshooting

**Custom data not showing?**
- Check column name matches field `name` (not `label`)
- Download fresh template to verify

**Import fails?**
- Check CSV has all required columns
- Verify no duplicate emails
- Check file is valid CSV format

**Need help?**
- See full documentation: `docs/CSV_IMPORT_WITH_CUSTOM_FIELDS.md`

---

**Status:** ✅ Ready to use  
**Last Updated:** January 26, 2026
