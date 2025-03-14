# Storage Test Script

This script tests the storage functionality of the YubiKey Bitcoin Seed Storage application.

## Prerequisites

- Python 3.8 or higher
- SQLite3
- YubiKey with FIDO2 support
- Test environment set up according to setup guide

## Test Environment Setup

1. Create a backup of the existing database (if any):
   ```bash
   mkdir -p data/backup
   cp data/yubikey_storage.db data/backup/ 2>/dev/null || echo "No database to backup"
   ```

2. Initialize a fresh database:
   ```bash
   rm -f data/yubikey_storage.db
   python -c "from models.database import DatabaseManager; DatabaseManager('data/yubikey_storage.db')"
   ```

## Test Cases

### 1. User Registration and YubiKey Association

1. Register a new user
2. Register a YubiKey for the user
3. Verify in database:
   ```bash
   sqlite3 data/yubikey_storage.db "SELECT * FROM users;"
   sqlite3 data/yubikey_storage.db "SELECT * FROM yubikeys;"
   ```

Expected results:
- User record should exist in the users table
- YubiKey record should exist in the yubikeys table with correct user_id

### 2. Seed Storage

1. Store a test seed phrase
2. Verify in database:
   ```bash
   sqlite3 data/yubikey_storage.db "SELECT * FROM seeds;"
   ```

Expected results:
- Seed record should exist in the seeds table
- Seed data should be encrypted
- Record should link to correct user_id

### 3. YubiKey Salt Management

1. Generate and store a salt
2. Verify in database:
   ```bash
   sqlite3 data/yubikey_storage.db "SELECT * FROM yubikey_salts;"
   ```

Expected results:
- Salt record should exist in yubikey_salts table
- Record should link to correct credential_id

### 4. Data Relationships

1. Verify foreign key relationships:
   ```bash
   sqlite3 data/yubikey_storage.db ".schema"
   sqlite3 data/yubikey_storage.db "PRAGMA foreign_key_list(seeds);"
   sqlite3 data/yubikey_storage.db "PRAGMA foreign_key_list(yubikeys);"
   sqlite3 data/yubikey_storage.db "PRAGMA foreign_key_list(yubikey_salts);"
   ```

Expected results:
- All foreign key constraints should be properly defined
- No orphaned records should exist

### 5. Cleanup

1. Restore the original database:
   ```bash
   cp data/backup/yubikey_storage.db data/ 2>/dev/null || echo "No backup to restore"
   ```

## Files to Review

- `yubikey_storage.db` - Main SQLite database
- Database schema in `models/database.py`
- Model files in `models/` directory

## Common Issues

1. Database permissions
2. Foreign key constraint violations
3. SQLite version compatibility
4. Database file locking issues

## Troubleshooting

1. Check database file permissions
2. Verify SQLite version compatibility
3. Check database integrity:
   ```bash
   sqlite3 data/yubikey_storage.db "PRAGMA integrity_check;"
   ```
4. Review application logs for database errors 