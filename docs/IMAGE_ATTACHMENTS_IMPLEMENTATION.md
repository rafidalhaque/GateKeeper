# Image Attachment System - Implementation Complete

## Overview
The image attachment system allows admins to upload and manage images for use in email templates, tickets, and tokens. Images are stored in the database with file metadata and served through API endpoints.

## Features Implemented

### 1. Database Model
- **Table**: `image_attachments`
- **Fields**:
  - `id`: Unique identifier (String UUID)
  - `filename`: System-generated unique filename
  - `original_filename`: User's original filename
  - `content_type`: MIME type (image/png, image/jpeg, etc.)
  - `file_size`: Size in bytes
  - `file_path`: Relative path to the uploaded file
  - `cid`: Content-ID for email embedding (format: `img_xxxxx@gatekeeper`)
  - `description`: Optional user description
  - `uploaded_by`: Foreign key to admin_users (UUID)
  - `usage_type`: Where image is used (email, ticket, token, all)
  - `is_active`: Soft delete flag
  - `created_at`, `updated_at`: Timestamps

### 2. API Endpoints

#### Upload Image
- **Endpoint**: `POST /api/attachments/upload`
- **Permission**: `manage_email_templates`
- **Body**: multipart/form-data
  - `file` (required): Image file (PNG, JPG, GIF, SVG, max 5MB)
  - `description` (optional): Description text
  - `usage_type` (optional): email|ticket|token|all (default: all)
- **Response**: Image details including URL, CID, and HTML code

#### List Images
- **Endpoint**: `GET /api/attachments/`
- **Permission**: `manage_email_templates`
- **Query Params**: 
  - `usage_type` (optional): Filter by usage type
- **Response**: Array of image objects

#### Get Image Details
- **Endpoint**: `GET /api/attachments/<attachment_id>`
- **Response**: Full image metadata

#### Serve Image
- **Endpoint**: `GET /api/attachments/image/<attachment_id>`
- **Response**: Binary image file with proper MIME type

#### Update Image Metadata
- **Endpoint**: `PUT /api/attachments/<attachment_id>`
- **Permission**: `manage_email_templates`
- **Body**: JSON with `description` and/or `usage_type`

#### Delete Image
- **Endpoint**: `DELETE /api/attachments/<attachment_id>`
- **Permission**: `manage_email_templates`
- **Note**: Soft delete (can be recovered)

### 3. Frontend - Image Library
- **URL**: `/admin/image-library`
- **Features**:
  - Upload images with preview
  - Grid view of all uploaded images
  - Filter by usage type
  - View image details with copy-to-clipboard codes
  - Delete images
  - Shows file size, format, and metadata

### 4. Image Usage Codes

#### For Email Templates (CID)
```html
<img src="cid:img_abc123@gatekeeper" alt="Logo" />
```
The system will embed the image directly in the email.

#### For Tickets/Tokens (Direct URL)
```html
<img src="/api/attachments/image/abc-123-xyz" alt="Logo" style="width: 100px;" />
```
The PDF renderer will fetch and embed the image.

#### Background Images
```css
.header {
  background-image: url('/api/attachments/image/abc-123-xyz');
  background-size: cover;
  background-position: center;
}
```

### 5. CSS Guide Updates
Added comprehensive image section to `/admin/css-guide` including:
- CID vs Direct URL explanation
- Image styling techniques
- Common use cases (logos, photos, watermarks)
- Best practices
- Direct link to Image Library

### 6. Settings Page Integration
Added "Image Library" button to settings quick links section for easy access.

### 7. API Documentation
Added "Image Attachments" section to Swagger UI with:
- Full endpoint documentation
- Request/response schemas
- Example payloads
- Authentication requirements

## File Structure
```
app/
├── models/
│   └── attachments.py          # ImageAttachment model
├── routes/
│   └── attachments.py          # API endpoints
├── templates/
│   └── admin/
│       ├── image_library.html  # Frontend page
│       ├── css_guide.html      # Updated with image section
│       └── settings.html       # Added image library link
└── swagger_spec.py             # Updated API docs

uploads/
└── attachments/                # Image storage directory
```

## Usage Examples

### 1. Upload an Image
```bash
curl -X POST http://localhost:5000/api/attachments/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@logo.png" \
  -F "description=Company Logo" \
  -F "usage_type=all"
```

### 2. In Email Template
```html
<style>
  .header { text-align: center; padding: 20px; }
  .logo { width: 150px; }
</style>

<div class="header">
  <img src="cid:img_abc123@gatekeeper" class="logo" alt="Event Logo">
  <h1>Welcome to {{ event_name }}</h1>
</div>
```

### 3. In Ticket Template
```html
<style>
  .ticket {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    color: white;
  }
  .sponsor-logos img {
    width: 80px;
    margin: 10px;
    opacity: 0.8;
  }
</style>

<div class="ticket">
  <h1>{{ event_name }}</h1>
  <p>{{ participant_name }}</p>
  
  <div class="sponsor-logos">
    <img src="/api/attachments/image/sponsor1-id" alt="Sponsor 1">
    <img src="/api/attachments/image/sponsor2-id" alt="Sponsor 2">
  </div>
</div>
```

## Security Considerations
1. **File Type Validation**: Only allows image types (PNG, JPG, GIF, SVG, BMP, WEBP)
2. **File Size Limit**: Maximum 5MB per image
3. **Authentication Required**: All upload/modify operations require `manage_email_templates` permission
4. **Soft Delete**: Images are marked inactive, not permanently deleted
5. **Foreign Key**: Links to admin user for audit trail
6. **Secure Filenames**: Uses UUID-based filenames to prevent path traversal

## Testing
1. Log in as admin with `manage_email_templates` permission
2. Navigate to Settings → Image Library
3. Upload a test image (logo, photo, etc.)
4. Copy the HTML code
5. Go to Email Templates, Ticket Designer, or Token Designer
6. Paste the image code in the HTML section
7. Preview to see the image rendered

## Migration
The database migration has been applied:
```bash
flask --app run.py db migrate -m "Add image_attachments table with UUID foreign key"
flask --app run.py db upgrade
```

## Configuration
- **Upload Directory**: Configured in `app/config.py` as `UPLOAD_FOLDER` (default: `uploads`)
- **Max File Size**: Configured in `app/config.py` as `MAX_CONTENT_LENGTH` (default: 16MB)
- **Allowed Extensions**: Defined in `app/routes/attachments.py` (PNG, JPG, GIF, SVG, BMP, WEBP)

## Future Enhancements
- [ ] Image optimization/compression on upload
- [ ] Image cropping/editing tool
- [ ] Batch upload support
- [ ] CDN integration for faster delivery
- [ ] Image usage tracking (which templates use which images)
- [ ] Image categories/tags for better organization

## Status
✅ **COMPLETE** - All features implemented and tested
- Database model created
- API endpoints working
- Frontend UI functional
- Documentation updated
- Migration applied
