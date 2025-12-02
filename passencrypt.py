# ---- Begin secure storage helpers ----
import os
import stat
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import constant_time
import keyring   # cross-platform OS key store

# CONFIG
APP_NAME = "portt_app"              # arbitrary app name for keyring
KEYRING_KEY_ID = f"{APP_NAME}_master_key"
KEYFILE_PATH = os.path.expanduser("~/.portt_master.key")  # default location
ENCRYPTED_STATE = os.path.expanduser("~/.portt_state.enc")  # encrypted data file

# generate a fresh Fernet key
def generate_fernet_key():
    return Fernet.generate_key()  # already urlsafe base64 bytes

# save key into OS keyring (preferred)
def save_key_to_keyring(key: bytes):
    key_b64 = base64.urlsafe_b64encode(key).decode()
    keyring.set_password(APP_NAME, KEYRING_KEY_ID, key_b64)

# load key from OS keyring; returns bytes or None
def load_key_from_keyring():
    try:
        stored = keyring.get_password(APP_NAME, KEYRING_KEY_ID)
        if stored:
            return base64.urlsafe_b64decode(stored.encode())
    except Exception:
        pass
    return None

# save key to local keyfile with strict perms
def save_key_to_keyfile(key: bytes, path=KEYFILE_PATH):
    # write atomically
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(key)
    # set strict perms: owner read/write only (Unix)
    try:
        os.chmod(tmp, 0o600)
    except Exception:
        pass
    os.replace(tmp, path)
    # On Unix make sure perms are 600
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass

# load key from keyfile, return bytes or None
def load_key_from_keyfile(path=KEYFILE_PATH):
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

# helper: ensure key exists, prefer keyring, else keyfile, else create new key
def ensure_master_key():
    # 1) Try keyring
    key = load_key_from_keyring()
    if key:
        return key

    # 2) Try keyfile
    key = load_key_from_keyfile()
    if key:
        # attempt to also store into keyring for future
        try:
            save_key_to_keyring(key)
        except Exception:
            pass
        return key

    # 3) None found: generate new, save to keyring if possible, otherwise to keyfile
    key = generate_fernet_key()
    try:
        save_key_to_keyring(key)
    except Exception:
        # fallback to keyfile
        save_key_to_keyfile(key)
    return key

# encrypt / decrypt wrappers using Fernet and the master key
def encrypt_state(obj: dict, key: bytes, filename=ENCRYPTED_STATE):
    f = Fernet(key)
    plaintext = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    token = f.encrypt(plaintext)
    with open(filename, "wb") as fh:
        fh.write(token)
    # ensure file perms
    try:
        os.chmod(filename, 0o600)
    except Exception:
        pass

def decrypt_state(key: bytes, filename=ENCRYPTED_STATE):
    if not os.path.exists(filename):
        return None
    with open(filename, "rb") as fh:
        token = fh.read()
    f = Fernet(key)
    plaintext = f.decrypt(token)
    return json.loads(plaintext.decode("utf-8"))

# Provide a simple public API for the main app to use
MASTER_KEY = ensure_master_key()   # bytes

def save_state(obj: dict, filename=ENCRYPTED_STATE):
    """
    Save the provided dict into the encrypted state file using the master key.
    """
    encrypt_state(obj, MASTER_KEY, filename)

def load_state(filename=ENCRYPTED_STATE):
    """
    Load and return the decrypted state dict or None if not present.
    """
    try:
        return decrypt_state(MASTER_KEY, filename)
    except Exception:
        return None
# ---- End secure storage helpers ----




