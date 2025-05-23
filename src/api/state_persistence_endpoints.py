"""
State Persistence API Endpoints
Provides server-side backup for critical user state
"""
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from quart import Blueprint, request, jsonify
from quart_jwt_extended import jwt_required, get_jwt_identity

# Create blueprint for state persistence
state_persistence_bp = Blueprint('state_persistence', __name__)

# Directory for storing state files
STATE_DIR = os.path.join(os.getcwd(), 'data', 'user_states')
os.makedirs(STATE_DIR, exist_ok=True)

# Maximum state storage per user (in bytes)
MAX_STATE_SIZE = 1024 * 1024  # 1MB

# Maximum state backups to keep per user
MAX_BACKUPS_PER_USER = 5

def get_user_state_path(username: str, backup_id: Optional[str] = None) -> str:
    """Get the file path for a user's state file"""
    if backup_id:
        return os.path.join(STATE_DIR, f"{username}_{backup_id}.json")
    else:
        return os.path.join(STATE_DIR, f"{username}_current.json")

async def clean_old_backups(username: str) -> None:
    """Remove old backups to keep storage usage reasonable"""
    # List all backup files for this user
    user_files = [f for f in os.listdir(STATE_DIR) 
                if f.startswith(username) and f.endswith('.json')]
    
    # Skip if we're under the limit
    if len(user_files) <= MAX_BACKUPS_PER_USER:
        return
    
    # Get file info with modification times
    file_info = []
    for file in user_files:
        if file == f"{username}_current.json":
            continue  # Skip the current state file
        
        file_path = os.path.join(STATE_DIR, file)
        mod_time = os.path.getmtime(file_path)
        file_info.append((file_path, mod_time))
    
    # Sort by modification time (oldest first)
    file_info.sort(key=lambda x: x[1])
    
    # Delete the oldest files
    for file_path, _ in file_info[:-(MAX_BACKUPS_PER_USER-1)]:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting old backup {file_path}: {e}")

@state_persistence_bp.route('/api/state/backup', methods=['POST'])
@jwt_required
async def backup_state():
    """Save the client state to the server"""
    username = get_jwt_identity()
    
    try:
        # Get state data from request
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check size limit
        state_size = len(json.dumps(data))
        if state_size > MAX_STATE_SIZE:
            return jsonify({'error': 'State data exceeds maximum size limit'}), 413
        
        # Create a backup of the current state first
        current_path = get_user_state_path(username)
        if os.path.exists(current_path):
            # Create backup with timestamp
            backup_id = int(time.time())
            backup_path = get_user_state_path(username, str(backup_id))
            try:
                with open(current_path, 'r') as current_file:
                    with open(backup_path, 'w') as backup_file:
                        backup_file.write(current_file.read())
            except Exception as e:
                print(f"Error creating backup: {e}")
        
        # Save the new state
        with open(current_path, 'w') as f:
            json.dump({
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'state': data
            }, f)
        
        # Clean up old backups
        await clean_old_backups(username)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error saving state for {username}: {e}")
        return jsonify({'error': str(e)}), 500

@state_persistence_bp.route('/api/state/restore', methods=['GET'])
@jwt_required
async def restore_state():
    """Retrieve the client state from the server"""
    username = get_jwt_identity()
    
    try:
        # Get the current state file path
        state_path = get_user_state_path(username)
        
        # Check if the state file exists
        if not os.path.exists(state_path):
            return jsonify({'success': False, 'reason': 'No state found'}), 404
        
        # Read the state data
        with open(state_path, 'r') as f:
            state_data = json.load(f)
        
        return jsonify({
            'success': True,
            'timestamp': state_data.get('timestamp'),
            'state': state_data.get('state')
        })
    
    except Exception as e:
        print(f"Error retrieving state for {username}: {e}")
        return jsonify({'error': str(e)}), 500

@state_persistence_bp.route('/api/state/history', methods=['GET'])
@jwt_required
async def state_history():
    """Get a list of available state backups"""
    username = get_jwt_identity()
    
    try:
        # List all backup files for this user
        user_files = [f for f in os.listdir(STATE_DIR) 
                    if f.startswith(username) and f.endswith('.json')]
        
        backups = []
        for file in user_files:
            file_path = os.path.join(STATE_DIR, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    backups.append({
                        'id': file.replace('.json', '').replace(f"{username}_", ''),
                        'timestamp': data.get('timestamp'),
                        'size': os.path.getsize(file_path)
                    })
            except Exception as e:
                print(f"Error reading backup file {file}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'backups': backups
        })
    
    except Exception as e:
        print(f"Error retrieving state history for {username}: {e}")
        return jsonify({'error': str(e)}), 500

@state_persistence_bp.route('/api/state/restore/<backup_id>', methods=['GET'])
@jwt_required
async def restore_backup(backup_id):
    """Restore a specific state backup"""
    username = get_jwt_identity()
    
    try:
        # Get the backup file path
        backup_path = get_user_state_path(username, backup_id)
        
        # Check if the backup file exists
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'reason': 'Backup not found'}), 404
        
        # Read the backup data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        return jsonify({
            'success': True,
            'timestamp': backup_data.get('timestamp'),
            'state': backup_data.get('state')
        })
    
    except Exception as e:
        print(f"Error restoring backup {backup_id} for {username}: {e}")
        return jsonify({'error': str(e)}), 500
