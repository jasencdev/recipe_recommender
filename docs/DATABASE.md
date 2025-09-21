# Database Documentation

This document provides comprehensive documentation for the Recipe Recommender database schema, models, and data management.

## Overview

The application uses SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production) databases. The schema is designed for user management, recipe bookmarking, and secure password reset functionality.

## Database Configuration

### Supported Databases

**SQLite (Development)**
- File-based database stored in `instance/database.db`
- Automatically created on first run
- No additional setup required
- Suitable for development and testing

**PostgreSQL (Production)**
- Configured via `DATABASE_URL` environment variable
- Recommended for production deployments
- Supports connection pooling and concurrent access
- Better performance for multiple users

### Connection Configuration

```python
# SQLite (default)
# No configuration needed - uses instance/database.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database_name

# Railway PostgreSQL example
DATABASE_URL=postgresql://user:pass@containers-us-west-12.railway.app:6543/railway

# Persistent SQLite with custom directory
SQLITE_DIR=/data  # Uses /data/database.db
```

## Database Models

### User Model

**Table**: `user`

The User model handles user authentication and profile information with Flask-Login integration.

```python
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(50))
    newsletter_signup = db.Column(db.Boolean)
```

#### Schema Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | Integer | Primary Key, Auto-increment | Unique user identifier |
| `email_address` | String(100) | Not Null | User's email (normalized to lowercase) |
| `full_name` | String(80) | Not Null | User's display name |
| `password_hash` | String(255) | Not Null | Hashed password using Werkzeug |
| `country` | String(50) | Nullable | User's country (optional) |
| `newsletter_signup` | Boolean | Nullable | Newsletter subscription preference |

#### Key Features

- **Flask-Login Integration**: Implements `UserMixin` for session management
- **Email Normalization**: Emails stored in lowercase for consistency
- **Password Security**: Passwords hashed using Werkzeug's secure methods
- **Optional Fields**: Country and newsletter signup are optional

#### Indexes and Constraints

```sql
-- Implicit primary key index on user_id
-- Consider adding index on email_address for login performance
CREATE INDEX idx_user_email ON user (email_address);
```

### SavedRecipe Model

**Table**: `saved_recipe`

Manages user's saved recipe bookmarks with relationships to the User model.

```python
class SavedRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipe_id = db.Column(db.String(50), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe'),)
```

#### Schema Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique saved recipe record ID |
| `user_id` | Integer | Foreign Key to `user.user_id`, Not Null | Reference to user who saved recipe |
| `recipe_id` | String(50) | Not Null | Recipe identifier from ML model |
| `saved_at` | DateTime | Default: current UTC time | When recipe was saved |

#### Key Features

- **User Relationship**: Foreign key relationship to User model
- **Recipe Reference**: Links to recipes in the ML model dataset
- **Duplicate Prevention**: Unique constraint prevents saving same recipe twice
- **Audit Trail**: Timestamp tracking when recipes were saved

#### Constraints and Indexes

```sql
-- Foreign key constraint
FOREIGN KEY (user_id) REFERENCES user (user_id)

-- Unique constraint to prevent duplicate saves
CONSTRAINT unique_user_recipe UNIQUE (user_id, recipe_id)

-- Recommended indexes for performance
CREATE INDEX idx_saved_recipe_user_id ON saved_recipe (user_id);
CREATE INDEX idx_saved_recipe_recipe_id ON saved_recipe (recipe_id);
CREATE INDEX idx_saved_recipe_saved_at ON saved_recipe (saved_at);
```

### PasswordResetToken Model

**Table**: `password_reset_token`

Manages secure password reset tokens with expiration and usage tracking.

```python
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

#### Schema Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique token record ID |
| `user_id` | Integer | Foreign Key to `user.user_id`, Not Null | User requesting password reset |
| `token` | String(255) | Unique, Not Null | Cryptographically secure reset token |
| `expires_at` | DateTime | Not Null | Token expiration time (1 hour from creation) |
| `used` | Boolean | Default: False, Not Null | Whether token has been consumed |
| `created_at` | DateTime | Default: current UTC time, Not Null | Token creation timestamp |

#### Key Features

- **Security**: Cryptographically secure tokens using `secrets.token_urlsafe(32)`
- **Expiration**: Tokens expire 1 hour after creation
- **Single Use**: Tokens marked as used after successful password reset
- **User Association**: Linked to specific user account
- **Cleanup**: Old tokens can be cleaned up via admin endpoints

#### Security Considerations

```python
# Token generation (from auth.py)
import secrets
raw_token = secrets.token_urlsafe(32)  # 256-bit entropy
expires_at = datetime.utcnow() + timedelta(hours=1)
```

#### Constraints and Indexes

```sql
-- Foreign key constraint
FOREIGN KEY (user_id) REFERENCES user (user_id)

-- Unique constraint on token
CONSTRAINT password_reset_token_token_key UNIQUE (token)

-- Recommended indexes
CREATE INDEX idx_password_reset_token_user_id ON password_reset_token (user_id);
CREATE INDEX idx_password_reset_token_expires_at ON password_reset_token (expires_at);
CREATE INDEX idx_password_reset_token_used ON password_reset_token (used);
```

### PasswordResetRequestLog Model

**Table**: `password_reset_request_log`

Logs password reset requests for rate limiting and abuse prevention.

```python
class PasswordResetRequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True)
    ip = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

#### Schema Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique log entry ID |
| `email` | String(120) | Nullable | Email address used in request (if provided) |
| `ip` | String(64) | Not Null | IP address of requester |
| `created_at` | DateTime | Default: current UTC time, Not Null | Request timestamp |

#### Key Features

- **Rate Limiting**: Enables IP and email-based rate limiting
- **Abuse Prevention**: Tracks patterns of password reset requests
- **Privacy**: Email can be null for invalid requests
- **Audit Trail**: Complete log of reset request attempts

#### Rate Limiting Implementation

```python
# Example rate limiting logic (from auth.py)
window_start = datetime.utcnow() - timedelta(hours=1)

# Check IP-based limits
ip_count = PasswordResetRequestLog.query.filter(
    PasswordResetRequestLog.ip == ip,
    PasswordResetRequestLog.created_at >= window_start
).count()

# Check email-based limits
email_count = PasswordResetRequestLog.query.filter(
    PasswordResetRequestLog.email == email,
    PasswordResetRequestLog.created_at >= window_start
).count()
```

#### Constraints and Indexes

```sql
-- Indexes for rate limiting queries
CREATE INDEX idx_password_reset_log_ip_created ON password_reset_request_log (ip, created_at);
CREATE INDEX idx_password_reset_log_email_created ON password_reset_request_log (email, created_at);
CREATE INDEX idx_password_reset_log_created_at ON password_reset_request_log (created_at);
```

## Database Relationships

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐
│      User       │       │    SavedRecipe      │
├─────────────────┤       ├─────────────────────┤
│ user_id (PK)    │◄─────┐│ id (PK)             │
│ email_address   │      ││ user_id (FK)        │
│ full_name       │      ││ recipe_id           │
│ password_hash   │      ││ saved_at            │
│ country         │      │└─────────────────────┘
│ newsletter_signup│      │
└─────────────────┘      │
        ▲                │
        │                │
        ├────────────────┘
        │
        │                ┌─────────────────────────┐
        │                │  PasswordResetToken     │
        │                ├─────────────────────────┤
        └───────────────►│ id (PK)                 │
                         │ user_id (FK)            │
                         │ token (UNIQUE)          │
                         │ expires_at              │
                         │ used                    │
                         │ created_at              │
                         └─────────────────────────┘

┌─────────────────────────────┐
│  PasswordResetRequestLog    │
├─────────────────────────────┤
│ id (PK)                     │
│ email                       │
│ ip                          │
│ created_at                  │
└─────────────────────────────┘
```

### Relationship Details

**User → SavedRecipe (One-to-Many)**
- One user can save multiple recipes
- Foreign key: `saved_recipe.user_id` → `user.user_id`
- Cascade behavior: Consider CASCADE DELETE for user deletion

**User → PasswordResetToken (One-to-Many)**
- One user can have multiple reset tokens (though typically one active)
- Foreign key: `password_reset_token.user_id` → `user.user_id`
- Old unused tokens are periodically cleaned up

**PasswordResetRequestLog (Independent)**
- No foreign key relationships
- Logs all reset attempts regardless of user existence
- Used purely for rate limiting and auditing

## Database Operations

### Initialization

```python
# Database initialization (from __init__.py)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Database configuration
    if database_url := os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # SQLite fallback
        sqlite_dir = os.getenv('SQLITE_DIR', app.instance_path)
        os.makedirs(sqlite_dir, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_dir}/database.db'

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Create tables if they don't exist
```

### Common Queries

#### User Operations

```python
# User registration
user = User(
    email_address=email.lower(),  # Normalized
    full_name=full_name,
    country=country,
    newsletter_signup=newsletter_signup
)
user.password_hash = generate_password_hash(password)
db.session.add(user)
db.session.commit()

# User login (case-insensitive email lookup)
user = User.query.filter(func.lower(User.email_address) == email.lower()).first()

# Check password
if user and check_password_hash(user.password_hash, password):
    login_user(user)
```

#### Saved Recipe Operations

```python
# Check if recipe is saved
existing = SavedRecipe.query.filter_by(
    user_id=current_user.user_id,
    recipe_id=recipe_id
).first()

# Save recipe
saved = SavedRecipe(user_id=current_user.user_id, recipe_id=recipe_id)
db.session.add(saved)
db.session.commit()

# Get user's saved recipes
saved_recipes = SavedRecipe.query.filter_by(user_id=current_user.user_id).all()
recipe_ids = [sr.recipe_id for sr in saved_recipes]

# Remove saved recipe
saved = SavedRecipe.query.filter_by(
    user_id=current_user.user_id,
    recipe_id=recipe_id
).first()
if saved:
    db.session.delete(saved)
    db.session.commit()
```

#### Password Reset Operations

```python
# Create reset token
import secrets
raw_token = secrets.token_urlsafe(32)
expires_at = datetime.utcnow() + timedelta(hours=1)

# Clear existing tokens for user
PasswordResetToken.query.filter_by(user_id=user.user_id, used=False).delete()

# Create new token
reset_token = PasswordResetToken(
    user_id=user.user_id,
    token=raw_token,
    expires_at=expires_at
)
db.session.add(reset_token)
db.session.commit()

# Validate and use token
token_record = PasswordResetToken.query.filter_by(
    token=token,
    used=False
).first()

if token_record and token_record.expires_at > datetime.utcnow():
    # Token is valid - update password and mark as used
    user = User.query.get(token_record.user_id)
    user.password_hash = generate_password_hash(new_password)
    token_record.used = True
    db.session.commit()
```

#### Rate Limiting Queries

```python
# Check rate limits for password reset
from datetime import datetime, timedelta

window_start = datetime.utcnow() - timedelta(hours=1)

# IP-based rate limiting
ip_count = PasswordResetRequestLog.query.filter(
    PasswordResetRequestLog.ip == ip,
    PasswordResetRequestLog.created_at >= window_start
).count()

# Email-based rate limiting
email_count = PasswordResetRequestLog.query.filter(
    PasswordResetRequestLog.email == email,
    PasswordResetRequestLog.created_at >= window_start
).count()

# Log the request
log_entry = PasswordResetRequestLog(email=email, ip=ip)
db.session.add(log_entry)
db.session.commit()
```

## Database Migrations

### Manual Schema Updates

For schema changes, manual migration may be required:

```sql
-- Example: Add index for better performance
CREATE INDEX idx_user_email ON user (email_address);

-- Example: Increase password hash column size (already done)
ALTER TABLE user ALTER COLUMN password_hash TYPE VARCHAR(255);
```

### PostgreSQL Specific Features

```sql
-- Use PostgreSQL-specific features for better performance
CREATE INDEX CONCURRENTLY idx_saved_recipe_user_recipe ON saved_recipe (user_id, recipe_id);

-- Partial indexes for active tokens only
CREATE INDEX idx_active_tokens ON password_reset_token (user_id, expires_at)
WHERE used = false;
```

## Data Maintenance

### Cleanup Operations

#### Admin Maintenance Endpoint

```python
# Clean up old password reset data
def clear_reset_data(days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Delete old request logs
    logs_deleted = PasswordResetRequestLog.query.filter(
        PasswordResetRequestLog.created_at < cutoff
    ).delete()

    # Delete old/expired tokens
    tokens_deleted = PasswordResetToken.query.filter(
        (PasswordResetToken.expires_at < cutoff) |
        (PasswordResetToken.created_at < cutoff)
    ).delete()

    db.session.commit()
    return {"logs": logs_deleted, "tokens": tokens_deleted}
```

### Performance Considerations

#### Index Optimization

```sql
-- Essential indexes for performance
CREATE INDEX idx_user_email ON user (email_address);
CREATE INDEX idx_saved_recipe_user_id ON saved_recipe (user_id);
CREATE INDEX idx_saved_recipe_recipe_id ON saved_recipe (recipe_id);
CREATE INDEX idx_password_reset_log_ip_created ON password_reset_request_log (ip, created_at);
CREATE INDEX idx_password_reset_log_email_created ON password_reset_request_log (email, created_at);
```

#### Query Optimization

- Use compound indexes for common query patterns
- Limit result sets with pagination
- Use `func.lower()` for case-insensitive comparisons
- Consider connection pooling for PostgreSQL

## Security Considerations

### Password Security

- Passwords hashed using Werkzeug's secure `generate_password_hash()`
- Password hash column increased to 255 characters for algorithm flexibility
- No password complexity requirements enforced at database level

### Token Security

- Reset tokens use `secrets.token_urlsafe(32)` for cryptographic security
- Tokens have 1-hour expiration
- Single-use tokens marked as used after consumption
- Old tokens cleaned up regularly

### Rate Limiting

- IP-based and email-based rate limiting prevents abuse
- Configurable limits via environment variables
- Request logging for audit trails

### Data Privacy

- Email addresses normalized to lowercase for consistency
- No sensitive data stored in plain text
- Optional fields respect user privacy preferences

## Backup and Recovery

### SQLite Backup

```bash
# Backup SQLite database
cp instance/database.db backup/database_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp backup/database_20240115_120000.db instance/database.db
```

### PostgreSQL Backup

```bash
# Backup PostgreSQL database
pg_dump $DATABASE_URL > backup/database_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql $DATABASE_URL < backup/database_20240115_120000.sql
```

## Monitoring and Analytics

### Useful Queries for Monitoring

```sql
-- User registration trends
SELECT DATE(created_at) as date, COUNT(*) as registrations
FROM user
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Most saved recipes
SELECT recipe_id, COUNT(*) as save_count
FROM saved_recipe
GROUP BY recipe_id
ORDER BY save_count DESC
LIMIT 10;

-- Password reset request patterns
SELECT DATE(created_at) as date, COUNT(*) as requests
FROM password_reset_request_log
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Rate limiting violations
SELECT ip, COUNT(*) as attempts
FROM password_reset_request_log
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY ip
HAVING COUNT(*) > 5;
```

---

For API integration details, see [API.md](API.md).

For application architecture, see [README.md](../README.md).