import os
import secrets
import base64
import json
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Data storage paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SHARED_DIR = os.path.join(DATA_DIR, "shared")

# Ensure data directories exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(SHARED_DIR):
    os.makedirs(SHARED_DIR)

# Initialize users file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

# Helper functions for cryptography
def derive_key(password, salt=None):
    """Derive a cryptographic key from a password."""
    if salt is None:
        salt = os.urandom(16)
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def hash_password(password, salt=None):
    """Hash a password with salt."""
    if salt is None:
        salt = os.urandom(16)
        
    # Combine password with salt and hash
    salted_password = password.encode() + salt
    hash_obj = hashes.Hash(hashes.SHA256())
    hash_obj.update(salted_password)
    password_hash = hash_obj.finalize().hex()
    
    return password_hash, salt.hex()

def verify_password(entered_password, stored_hash, stored_salt):
    """Verify a password against a stored hash."""
    salt = bytes.fromhex(stored_salt)
    salted_password = entered_password.encode() + salt
    hash_obj = hashes.Hash(hashes.SHA256())
    hash_obj.update(salted_password)
    computed_hash = hash_obj.finalize().hex()
    
    return computed_hash == stored_hash

def get_user_data_path(username):
    """Get path to user's encrypted data file."""
    return os.path.join(DATA_DIR, f"{username}_passwords.dat")

def encrypt_data(data, key):
    """Encrypt data (dictionary) with the given key."""
    fernet = Fernet(key)
    json_data = json.dumps(data)
    encrypted_data = fernet.encrypt(json_data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    """Decrypt data with the given key."""
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

def encrypt_password(password, key):
    """Encrypt a single password string."""
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_password(encrypted_password, key):
    """Decrypt a single password string."""
    try:
        fernet = Fernet(key)
        encrypted = base64.b64decode(encrypted_password)
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return None

def load_users():
    """Load all users from the users file."""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Save users to the users file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def save_user_passwords(username, encrypted_data):
    """Save encrypted password data for a user."""
    with open(get_user_data_path(username), 'wb') as f:
        f.write(encrypted_data)

def load_user_passwords(username):
    """Load encrypted password data for a user."""
    data_path = get_user_data_path(username)
    if not os.path.exists(data_path):
        return None
    
    with open(data_path, 'rb') as f:
        return f.read()

def create_shared_item(entry, username, expiration_hours=24, access_count=1):
    """Create a shared password entry."""
    # Generate a random access key
    access_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    # Create a copy of the entry for sharing
    shared_entry = {
        "title": entry.get("title", ""),
        "username": entry.get("username", ""),
        "password": entry.get("password", ""),
        "website": entry.get("website", ""),
        "notes": entry.get("notes", ""),
        "category": entry.get("category", ""),
        "shared_by": username
    }
    
    # Generate a unique ID for this shared item
    share_id = secrets.token_hex(16)
    
    # Set up expiration details
    expiration_time = time.time() + (expiration_hours * 3600)
    
    # Encrypt the entry with the access key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'sharing_salt',  # Fixed salt for simplicity
        iterations=100000,
    )
    sharing_key = base64.urlsafe_b64encode(kdf.derive(access_key.encode()))
    fernet = Fernet(sharing_key)
    
    encrypted_data = fernet.encrypt(json.dumps(shared_entry).encode())
    
    # Create share metadata
    share_data = {
        "encrypted_entry": base64.b64encode(encrypted_data).decode(),
        "created_at": time.time(),
        "expires_at": expiration_time,
        "access_count_limit": access_count,
        "access_count_current": 0,
        "is_valid": True,
        "owner": username
    }
    
    # Save shared item
    share_path = os.path.join(SHARED_DIR, f"{share_id}.json")
    with open(share_path, 'w') as f:
        json.dump(share_data, f)
    
    return share_id, access_key

def access_shared_item(share_id, access_key):
    """Access a shared password item."""
    # Load the shared item
    share_path = os.path.join(SHARED_DIR, f"{share_id}.json")
    if not os.path.exists(share_path):
        return None
    
    with open(share_path, 'r') as f:
        share_data = json.load(f)
    
    # Check if share is valid
    if not share_data.get("is_valid", False):
        return None
    
    # Check if expired
    current_time = time.time()
    if current_time > share_data.get("expires_at", 0):
        # Mark as invalid due to expiration
        share_data["is_valid"] = False
        with open(share_path, 'w') as f:
            json.dump(share_data, f)
        return None
    
    # Check access count
    current_count = share_data.get("access_count_current", 0)
    limit = share_data.get("access_count_limit", 1)
    
    if limit > 0 and current_count >= limit:
        # Mark as invalid due to max access count reached
        share_data["is_valid"] = False
        with open(share_path, 'w') as f:
            json.dump(share_data, f)
        return None
    
    # Increment access count
    share_data["access_count_current"] = current_count + 1
    if limit > 0 and share_data["access_count_current"] >= limit:
        share_data["is_valid"] = False
    
    # Save updated access count
    with open(share_path, 'w') as f:
        json.dump(share_data, f)
    
    # Decrypt the shared item
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'sharing_salt',  # Fixed salt for simplicity
            iterations=100000,
        )
        sharing_key = base64.urlsafe_b64encode(kdf.derive(access_key.encode()))
        fernet = Fernet(sharing_key)
        
        encrypted_data = base64.b64decode(share_data["encrypted_entry"])
        decrypted_data = fernet.decrypt(encrypted_data)
        
        return json.loads(decrypted_data.decode())
    except Exception as e:
        print(f"Error decrypting shared item: {e}")
        return None

def get_user_shares(username):
    """Get all shares created by a user."""
    shares = []
    
    for filename in os.listdir(SHARED_DIR):
        if filename.endswith(".json"):
            share_id = filename[:-5]  # Remove .json extension
            share_path = os.path.join(SHARED_DIR, filename)
            
            with open(share_path, 'r') as f:
                share_data = json.load(f)
            
            if share_data.get("owner") == username:
                # Add share ID to the data
                share_info = {
                    "id": share_id,
                    "created_at": share_data.get("created_at"),
                    "expires_at": share_data.get("expires_at"),
                    "access_count_limit": share_data.get("access_count_limit"),
                    "access_count_current": share_data.get("access_count_current"),
                    "is_valid": share_data.get("is_valid")
                }
                shares.append(share_info)
    
    return shares

def invalidate_shared_item(share_id, username):
    """Invalidate a shared item if owned by the user."""
    share_path = os.path.join(SHARED_DIR, f"{share_id}.json")
    if not os.path.exists(share_path):
        return False
    
    with open(share_path, 'r') as f:
        share_data = json.load(f)
    
    # Verify ownership
    if share_data.get("owner") != username:
        return False
    
    share_data["is_valid"] = False
    
    with open(share_path, 'w') as f:
        json.dump(share_data, f)
    
    return True

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('register.html')
        
        # Check if username exists
        users = load_users()
        if username in users:
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # Create user
        password_hash, salt = hash_password(password)
        
        # Derive encryption key
        key, key_salt = derive_key(password)
        
        users[username] = {
            "password_hash": password_hash,
            "password_salt": salt,
            "key_salt": key_salt.hex(),
            "created_at": time.time()
        }
        
        save_users(users)
        
        # Create initial empty password database
        initial_data = {
            "entries": [],
            "version": 1
        }
        
        encrypted_data = encrypt_data(initial_data, key)
        save_user_passwords(username, encrypted_data)
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Check credentials
        users = load_users()
        if username not in users:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        user_data = users[username]
        if not verify_password(password, user_data['password_hash'], user_data['password_salt']):
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        # Derive key for decryption
        key_salt = bytes.fromhex(user_data['key_salt'])
        key, _ = derive_key(password, key_salt)
        
        # Store username and key in session
        session['username'] = username
        session['key'] = key.decode()  # Store key as string
        session.permanent = True
        
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/api/passwords', methods=['GET'])
def get_passwords():
    if 'username' not in session or 'key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()  # Convert string back to bytes
    
    encrypted_data = load_user_passwords(username)
    if not encrypted_data:
        return jsonify({"entries": []})
    
    data = decrypt_data(encrypted_data, key)
    if not data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    # Don't send encrypted passwords to frontend
    entries = data.get("entries", [])
    for entry in entries:
        if "password" in entry and entry.get("encrypted", False):
            entry["password_hidden"] = True
            entry["password"] = "********"
    
    return jsonify({"entries": entries})

@app.route('/api/passwords', methods=['POST'])
def add_password():
    if 'username' not in session or 'key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()
    
    # Get request data
    entry = request.json
    
    # Encrypt password
    if "password" in entry:
        entry["password"] = encrypt_password(entry["password"], key)
        entry["encrypted"] = True
    
    # Add timestamps
    entry["created_at"] = time.time()
    entry["modified_at"] = time.time()
    
    # Load current entries
    encrypted_data = load_user_passwords(username)
    if encrypted_data:
        data = decrypt_data(encrypted_data, key)
    else:
        data = {"entries": [], "version": 1}
    
    if not data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    # Add new entry
    data["entries"].append(entry)
    
    # Save updated data
    encrypted_data = encrypt_data(data, key)
    save_user_passwords(username, encrypted_data)
    
    return jsonify({"success": True, "entry": entry})

@app.route('/api/passwords/<int:entry_id>', methods=['PUT'])
def update_password(entry_id):
    if 'username' not in session or 'key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()
    
    # Get request data
    updated_entry = request.json
    
    # Load current entries
    encrypted_data = load_user_passwords(username)
    if not encrypted_data:
        return jsonify({"error": "No data found"}), 404
    
    data = decrypt_data(encrypted_data, key)
    if not data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    entries = data.get("entries", [])
    
    # Ensure entry_id is valid
    if entry_id < 0 or entry_id >= len(entries):
        return jsonify({"error": "Entry not found"}), 404
    
    # If the password was changed, encrypt it
    if "password" in updated_entry and (not entries[entry_id].get("encrypted", False) or 
                                       updated_entry["password"] != "********"):
        updated_entry["password"] = encrypt_password(updated_entry["password"], key)
        updated_entry["encrypted"] = True
    
    # Update timestamps
    updated_entry["modified_at"] = time.time()
    if "created_at" not in updated_entry and "created_at" in entries[entry_id]:
        updated_entry["created_at"] = entries[entry_id]["created_at"]
    
    # Update entry
    entries[entry_id] = updated_entry
    
    # Save updated data
    encrypted_data = encrypt_data(data, key)
    save_user_passwords(username, encrypted_data)
    
    return jsonify({"success": True, "entry": updated_entry})

@app.route('/api/passwords/<int:entry_id>', methods=['DELETE'])
def delete_password(entry_id):
    if 'username' not in session or 'key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()
    
    # Load current entries
    encrypted_data = load_user_passwords(username)
    if not encrypted_data:
        return jsonify({"error": "No data found"}), 404
    
    data = decrypt_data(encrypted_data, key)
    if not data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    entries = data.get("entries", [])
    
    # Ensure entry_id is valid
    if entry_id < 0 or entry_id >= len(entries):
        return jsonify({"error": "Entry not found"}), 404
    
    # Delete entry
    deleted_entry = entries.pop(entry_id)
    
    # Save updated data
    encrypted_data = encrypt_data(data, key)
    save_user_passwords(username, encrypted_data)
    
    return jsonify({"success": True, "deleted": deleted_entry})

@app.route('/api/passwords/decrypt/<int:entry_id>', methods=['GET'])
def decrypt_password_api(entry_id):
    if 'username' not in session or 'key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()
    
    # Load current entries
    encrypted_data = load_user_passwords(username)
    if not encrypted_data:
        return jsonify({"error": "No data found"}), 404
    
    data = decrypt_data(encrypted_data, key)
    if not data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    entries = data.get("entries", [])
    
    # Ensure entry_id is valid
    if entry_id < 0 or entry_id >= len(entries):
        return jsonify({"error": "Entry not found"}), 404
    
    entry = entries[entry_id]
    
    # Decrypt password if encrypted
    if "password" in entry and entry.get("encrypted", False):
        decrypted_password = decrypt_password(entry["password"], key)
        if decrypted_password:
            return jsonify({"success": True, "password": decrypted_password})
    
    return jsonify({"error": "Could not decrypt password"}), 500

@app.route('/api/share', methods=['POST'])
def share_password():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    key = session['key'].encode()
    
    # Get request data
    data = request.json
    entry_id = data.get('entry_id')
    expiration_hours = data.get('expiration_hours', 24)
    access_count = data.get('access_count', 1)
    
    # Load current entries
    encrypted_data = load_user_passwords(username)
    if not encrypted_data:
        return jsonify({"error": "No data found"}), 404
    
    decrypted_data = decrypt_data(encrypted_data, key)
    if not decrypted_data:
        return jsonify({"error": "Could not decrypt data"}), 500
    
    entries = decrypted_data.get("entries", [])
    
    # Ensure entry_id is valid
    if entry_id < 0 or entry_id >= len(entries):
        return jsonify({"error": "Entry not found"}), 404
    
    entry = entries[entry_id]
    
    # Decrypt password if encrypted
    if "password" in entry and entry.get("encrypted", False):
        entry["password"] = decrypt_password(entry["password"], key)
    
    # Create share
    share_id, access_key = create_shared_item(entry, username, expiration_hours, access_count)
    
    # Generate sharing URL
    share_url = url_for('access_share', share_id=share_id, _external=True)
    
    return jsonify({
        "success": True,
        "share_id": share_id,
        "access_key": access_key,
        "share_url": share_url
    })

@app.route('/api/shares', methods=['GET'])
def get_shares():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    
    # Get shares for user
    shares = get_user_shares(username)
    
    # Format for display
    for share in shares:
        # Format timestamps
        created_at = datetime.fromtimestamp(share["created_at"])
        expires_at = datetime.fromtimestamp(share["expires_at"])
        
        share["created_at_formatted"] = created_at.strftime("%Y-%m-%d %H:%M")
        share["expires_at_formatted"] = expires_at.strftime("%Y-%m-%d %H:%M")
        
        # Calculate remaining time
        now = time.time()
        remaining_seconds = max(0, share["expires_at"] - now)
        remaining_hours = remaining_seconds / 3600
        
        if remaining_hours < 1:
            share["remaining_text"] = f"{int(remaining_seconds / 60)} minutes remaining"
        elif remaining_hours < 24:
            share["remaining_text"] = f"{int(remaining_hours)} hours remaining"
        elif remaining_hours < 48:
            share["remaining_text"] = "1 day remaining"
        else:
            share["remaining_text"] = f"{int(remaining_hours / 24)} days remaining"
    
    return jsonify({"shares": shares})

@app.route('/api/shares/<share_id>', methods=['DELETE'])
def revoke_share(share_id):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    
    # Invalidate share
    success = invalidate_shared_item(share_id, username)
    
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Could not revoke share"}), 500

@app.route('/shared/<share_id>', methods=['GET'])
def access_share(share_id):
    return render_template('shared.html', share_id=share_id)

@app.route('/api/shared/<share_id>', methods=['POST'])
def access_shared_password(share_id):
    access_key = request.json.get('access_key')
    
    if not access_key:
        return jsonify({"error": "Access key is required"}), 400
    
    # Access shared item
    shared_entry = access_shared_item(share_id, access_key)
    
    if not shared_entry:
        return jsonify({"error": "Invalid access key or expired share"}), 403
    
    return jsonify({"success": True, "entry": shared_entry})

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('key', None)
    return redirect(url_for('login'))

@app.route('/generator')
def generator():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('generator.html')

@app.route('/api/settings', methods=['POST'])
def save_settings():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    settings = request.json
    username = session['username']
    
    try:
        # Load master config
        config = load_users()[username]
        
        # Update settings
        if 'app_settings' not in config:
            config['app_settings'] = {}
            
        config['app_settings'].update(settings)
        
        # Save updated config
        users = load_users()
        users[username] = config
        save_users(users)
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving settings: {e}")
        return jsonify({"error": "Failed to save settings"}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    
    try:
        # Load master config
        config = load_users()[username]
        
        # Get settings
        settings = config.get('app_settings', {})
        
        # Set defaults if not present
        if 'theme_mode' not in settings:
            settings['theme_mode'] = 'system'
        if 'clipboard_timeout' not in settings:
            settings['clipboard_timeout'] = '30'
        if 'auto_logout' not in settings:
            settings['auto_logout'] = '0'
            
        return jsonify(settings)
    except Exception as e:
        print(f"Error getting settings: {e}")
        return jsonify({
            "theme_mode": "system",
            "clipboard_timeout": "30",
            "auto_logout": "0"
        })

@app.route('/api/generate-password', methods=['POST'])
def generate_password_api():
    import random
    import string
    
    data = request.json
    length = data.get('length', 16)
    include_uppercase = data.get('include_uppercase', True)
    include_lowercase = data.get('include_lowercase', True)
    include_numbers = data.get('include_numbers', True)
    include_symbols = data.get('include_symbols', True)
    exclude_similar = data.get('exclude_similar', False)
    exclude_ambiguous = data.get('exclude_ambiguous', False)
    
    # Character sets
    uppercase_chars = string.ascii_uppercase
    lowercase_chars = string.ascii_lowercase
    number_chars = string.digits
    symbol_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
    similar_chars = "il1Lo0O"
    ambiguous_chars = "{}[]()/\\'\"`~,;:.<>"
    
    # Build character set
    char_set = ""
    required_chars = []
    
    if include_uppercase:
        chars = uppercase_chars
        if exclude_similar:
            chars = ''.join(c for c in chars if c not in similar_chars)
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in ambiguous_chars)
        char_set += chars
        if chars:
            required_chars.append(random.choice(chars))
    
    if include_lowercase:
        chars = lowercase_chars
        if exclude_similar:
            chars = ''.join(c for c in chars if c not in similar_chars)
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in ambiguous_chars)
        char_set += chars
        if chars:
            required_chars.append(random.choice(chars))
    
    if include_numbers:
        chars = number_chars
        if exclude_similar:
            chars = ''.join(c for c in chars if c not in similar_chars)
        char_set += chars
        if chars:
            required_chars.append(random.choice(chars))
    
    if include_symbols:
        chars = symbol_chars
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in ambiguous_chars)
        char_set += chars
        if chars:
            required_chars.append(random.choice(chars))
    
    # Ensure we have characters to choose from
    if not char_set:
        return jsonify({"error": "No characters available with current settings"}), 400
    
    # Generate password
    if len(required_chars) > length:
        required_chars = required_chars[:length]
    
    password_chars = required_chars
    
    # Fill remaining length with random characters
    remaining_length = length - len(password_chars)
    password_chars.extend(random.choice(char_set) for _ in range(remaining_length))
    
    # Shuffle the password characters
    random.shuffle(password_chars)
    
    password = ''.join(password_chars)
    
    # Calculate strength (simplified)
    strength = 0
    
    # Length check
    if length >= 16:
        strength += 40
    elif length >= 12:
        strength += 30
    elif length >= 8:
        strength += 20
    else:
        strength += 10
    
    # Character variety
    if include_uppercase:
        strength += 15
    if include_lowercase:
        strength += 15
    if include_numbers:
        strength += 15
    if include_symbols:
        strength += 15
    
    # Clamp to 0-100
    strength = max(0, min(100, strength))
    
    return jsonify({
        "password": password,
        "strength": strength
    })

@app.route('/shared')
def shared():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('shared_passwords.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)