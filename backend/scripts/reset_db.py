#!/usr/bin/env python3
"""
Script to reset the database for testing.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from models.database import DatabaseManager
from models.user import User
from models.yubikey import YubiKey

def reset_database():
    """Reset the database by dropping all tables and recreating them."""
    try:
        db = DatabaseManager()
        
        # Drop all tables if they exist
        tables = [
            'wrapped_keys',      # Drop in correct order due to foreign keys
            'seeds',
            'yubikey_salts',
            'yubikeys',
            'users',
            'webauthn_challenges',
            'challenges'         # Added this table
        ]
        
        # Drop each table with error handling
        for table in tables:
            try:
                db.execute_query(f"DROP TABLE IF EXISTS {table}", commit=True)
                print(f"✓ Dropped table: {table}")
            except Exception as e:
                print(f"! Warning: Could not drop table {table}: {str(e)}")
        
        print("\n✓ All existing tables dropped")
        
        # Reinitialize the schema
        try:
            db.initialize_schema()
            print("✓ Reinitialized database schema")
            return True
        except Exception as e:
            print(f"! Error reinitializing schema: {str(e)}")
            return False
        
    except Exception as e:
        print(f"! Error resetting database: {str(e)}")
        return False

def show_database_state():
    """Show the current state of the database."""
    try:
        db = DatabaseManager()
        
        # Get all users
        cursor = db.execute_query("SELECT * FROM users")
        users = cursor.fetchall()
        print("\nUsers:")
        print("-------")
        for user in users:
            print(f"ID: {user['user_id']}, Username: {user['username']}, Max YubiKeys: {user['max_yubikeys']}")
            
            # Get YubiKeys for this user
            cursor = db.execute_query("SELECT * FROM yubikeys WHERE user_id = ?", (user['user_id'],))
            yubikeys = cursor.fetchall()
            if yubikeys:
                print("  YubiKeys:")
                for yk in yubikeys:
                    print(f"  - ID: {yk['credential_id']}, Nickname: {yk['nickname']}, Primary: {bool(yk['is_primary'])}")
            else:
                print("  No YubiKeys registered")
        
        if not users:
            print("No users found")
            
    except Exception as e:
        print(f"Error showing database state: {str(e)}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Show current state
    print("\nCurrent database state:")
    show_database_state()
    
    # Ask for confirmation
    response = input("\nDo you want to reset the database? This will delete all data! (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    print("\nResetting database...")
    if reset_database():
        print("Database reset successfully!")
        
        print("\nNew database state:")
        show_database_state()
    else:
        print("Failed to reset database!")
        sys.exit(1)
