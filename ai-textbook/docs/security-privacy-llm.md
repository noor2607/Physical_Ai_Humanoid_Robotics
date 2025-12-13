---
title: "Security & Privacy for LLM Integration"
sidebar_label: "Security & Privacy"
sidebar_position: 109
---

# Security & Privacy Measures for LLM API Access and Student Data

## Overview

This document outlines comprehensive security and privacy measures for the Physical AI & Humanoid Robotics course, particularly focusing on LLM API access and student data protection. As the course integrates with external AI services, it's crucial to implement robust security measures to protect both student privacy and API credentials.

## LLM API Security Architecture

### 1. API Key Management

#### Secure Storage
```python
# secure_api_manager.py
import os
import boto3
from cryptography.fernet import Fernet
import keyring
from typing import Optional

class SecureAPIManager:
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)

    def _get_encryption_key(self) -> bytes:
        """Get encryption key from secure storage"""
        # Option 1: From environment variable
        key = os.environ.get('SECURE_STORAGE_KEY')
        if key:
            return key.encode()

        # Option 2: From AWS Parameter Store
        try:
            ssm = boto3.client('ssm')
            response = ssm.get_parameter(
                Name='/robotics-course/encryption-key',
                WithDecryption=True
            )
            return response['Parameter']['Value'].encode()
        except:
            # Fallback: generate new key (should be stored securely)
            return Fernet.generate_key()

    def store_api_key(self, service: str, key: str):
        """Securely store API key"""
        encrypted_key = self.cipher.encrypt(key.encode())

        # Store in secure location (AWS Secrets Manager, Azure Key Vault, etc.)
        if os.environ.get('CLOUD_PROVIDER') == 'aws':
            self._store_in_aws_secrets(service, encrypted_key)
        elif os.environ.get('CLOUD_PROVIDER') == 'azure':
            self._store_in_azure_keyvault(service, encrypted_key)
        else:
            # Store in system keyring as fallback
            keyring.set_password(f"robotics-course-{service}", "api_key", encrypted_key.decode())

    def retrieve_api_key(self, service: str) -> Optional[str]:
        """Retrieve and decrypt API key"""
        # Retrieve from secure location
        encrypted_key = None
        if os.environ.get('CLOUD_PROVIDER') == 'aws':
            encrypted_key = self._retrieve_from_aws_secrets(service)
        elif os.environ.get('CLOUD_PROVIDER') == 'azure':
            encrypted_key = self._retrieve_from_azure_keyvault(service)
        else:
            encrypted_key_str = keyring.get_password(f"robotics-course-{service}", "api_key")
            if encrypted_key_str:
                encrypted_key = encrypted_key_str.encode()

        if encrypted_key:
            try:
                decrypted_key = self.cipher.decrypt(encrypted_key)
                return decrypted_key.decode()
            except:
                return None
        return None

    def _store_in_aws_secrets(self, service: str, encrypted_key: bytes):
        """Store encrypted key in AWS Secrets Manager"""
        client = boto3.client('secretsmanager')
        secret_name = f"robotics-course/{service}-api-key"

        client.create_secret(
            Name=secret_name,
            SecretString=encrypted_key.decode(),
            Description=f"Encrypted API key for {service} service in robotics course"
        )

    def _retrieve_from_aws_secrets(self, service: str) -> Optional[bytes]:
        """Retrieve encrypted key from AWS Secrets Manager"""
        client = boto3.client('secretsmanager')
        secret_name = f"robotics-course/{service}-api-key"

        try:
            response = client.get_secret_value(SecretId=secret_name)
            return response['SecretString'].encode()
        except client.exceptions.ResourceNotFoundException:
            return None
```

#### API Key Rotation
```python
# api_key_rotation.py
import datetime
from typing import Dict, Any

class APIKeyRotationManager:
    def __init__(self, api_manager: SecureAPIManager):
        self.api_manager = api_manager
        self.rotation_interval_days = 90  # Standard rotation interval

    def should_rotate_key(self, service: str) -> bool:
        """Check if API key should be rotated"""
        # Check last rotation date from secure storage
        last_rotation = self._get_last_rotation_date(service)
        if not last_rotation:
            return True  # New key, should set rotation date

        days_since_rotation = (datetime.datetime.now() - last_rotation).days
        return days_since_rotation >= self.rotation_interval_days

    def rotate_key(self, service: str, new_key: str) -> bool:
        """Rotate the API key for a service"""
        try:
            # Store new key
            self.api_manager.store_api_key(service, new_key)

            # Update rotation date
            self._update_rotation_date(service)

            # Log rotation event
            self._log_rotation_event(service)

            return True
        except Exception as e:
            print(f"Failed to rotate key for {service}: {e}")
            return False

    def _get_last_rotation_date(self, service: str) -> Optional[datetime.datetime]:
        """Get last rotation date from secure storage"""
        # Implementation would retrieve from secure storage
        pass

    def _update_rotation_date(self, service: str):
        """Update last rotation date in secure storage"""
        # Implementation would update in secure storage
        pass

    def _log_rotation_event(self, service: str):
        """Log key rotation event for audit purposes"""
        # Implementation would log to secure audit trail
        pass
```

### 2. API Access Control

#### Rate Limiting and Quotas
```python
# rate_limiter.py
import time
import threading
from collections import defaultdict, deque
from typing import Dict, Optional

class RateLimiter:
    def __init__(self):
        self.limits = {
            'openai': {'requests_per_minute': 3000, 'tokens_per_minute': 250000},
            'anthropic': {'requests_per_minute': 1000, 'tokens_per_minute': 100000},
            'google': {'requests_per_minute': 5000, 'tokens_per_minute': 300000}
        }
        self.request_counts = defaultdict(lambda: deque())
        self.token_counts = defaultdict(lambda: deque())
        self.lock = threading.Lock()

    def is_allowed(self, service: str, student_id: str, tokens_used: int = 1) -> bool:
        """Check if request is allowed based on rate limits"""
        with self.lock:
            now = time.time()
            minute_ago = now - 60

            # Clean old requests (older than 1 minute)
            while self.request_counts[(service, student_id)] and \
                  self.request_counts[(service, student_id)][0] < minute_ago:
                self.request_counts[(service, student_id)].popleft()

            while self.token_counts[(service, student_id)] and \
                  self.token_counts[(service, student_id)][0] < minute_ago:
                self.token_counts[(service, student_id)].popleft()

            # Check if within limits
            current_requests = len(self.request_counts[(service, student_id)])
            current_tokens = sum(self.token_counts[(service, student_id)])

            if current_requests >= self.limits[service]['requests_per_minute']:
                return False

            if current_tokens + tokens_used > self.limits[service]['tokens_per_minute']:
                return False

            # Add current request
            self.request_counts[(service, student_id)].append(now)
            self.token_counts[(service, student_id)].append((now, tokens_used))

            return True

    def get_remaining_quota(self, service: str, student_id: str) -> Dict[str, int]:
        """Get remaining quota for a student"""
        with self.lock:
            now = time.time()
            minute_ago = now - 60

            # Clean old requests
            while self.request_counts[(service, student_id)] and \
                  self.request_counts[(service, student_id)][0] < minute_ago:
                self.request_counts[(service, student_id)].popleft()

            while self.token_counts[(service, student_id)] and \
                  self.token_counts[(service, student_id)][0] < minute_ago:
                self.token_counts[(service, student_id)].popleft()

            current_requests = len(self.request_counts[(service, student_id)])
            current_tokens = sum(count for _, count in self.token_counts[(service, student_id)])

            return {
                'requests_remaining': self.limits[service]['requests_per_minute'] - current_requests,
                'tokens_remaining': self.limits[service]['tokens_per_minute'] - current_tokens
            }
```

#### Student-Specific Quotas
```python
# student_quota_manager.py
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional

class StudentQuotaManager:
    def __init__(self, db_path: str = "student_quotas.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database for storing quotas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_quotas (
                student_id TEXT PRIMARY KEY,
                service TEXT,
                daily_limit INTEGER,
                daily_used INTEGER,
                last_reset DATE,
                monthly_limit INTEGER,
                monthly_used INTEGER,
                monthly_reset DATE
            )
        ''')

        conn.commit()
        conn.close()

    def get_daily_quota(self, student_id: str, service: str) -> Dict[str, int]:
        """Get daily quota information for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if record exists
        cursor.execute('''
            SELECT daily_limit, daily_used, last_reset
            FROM student_quotas
            WHERE student_id = ? AND service = ?
        ''', (student_id, service))

        result = cursor.fetchone()
        if result:
            daily_limit, daily_used, last_reset = result
            reset_date = datetime.fromisoformat(last_reset)

            # Check if we need to reset
            if reset_date.date() < datetime.now().date():
                daily_used = 0
                cursor.execute('''
                    UPDATE student_quotas
                    SET daily_used = 0, last_reset = ?
                    WHERE student_id = ? AND service = ?
                ''', (datetime.now().isoformat(), student_id, service))

            remaining = daily_limit - daily_used
        else:
            # Default quotas
            daily_limit = self._get_default_daily_limit(service)
            daily_used = 0
            remaining = daily_limit

            # Insert new record
            cursor.execute('''
                INSERT INTO student_quotas
                (student_id, service, daily_limit, daily_used, last_reset, monthly_limit, monthly_used, monthly_reset)
                VALUES (?, ?, ?, 0, ?, ?, 0, ?)
            ''', (
                student_id, service, daily_limit, datetime.now().isoformat(),
                self._get_default_monthly_limit(service), datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

        return {
            'limit': daily_limit,
            'used': daily_used,
            'remaining': remaining
        }

    def consume_quota(self, student_id: str, service: str, tokens_used: int) -> bool:
        """Consume quota for a request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current usage
        cursor.execute('''
            SELECT daily_limit, daily_used, monthly_limit, monthly_used
            FROM student_quotas
            WHERE student_id = ? AND service = ?
        ''', (student_id, service))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return False

        daily_limit, daily_used, monthly_limit, monthly_used = result

        # Check if within limits
        if daily_used + tokens_used > daily_limit:
            conn.close()
            return False

        if monthly_used + tokens_used > monthly_limit:
            conn.close()
            return False

        # Update usage
        cursor.execute('''
            UPDATE student_quotas
            SET daily_used = daily_used + ?,
                monthly_used = monthly_used + ?
            WHERE student_id = ? AND service = ?
        ''', (tokens_used, tokens_used, student_id, service))

        conn.commit()
        conn.close()
        return True

    def _get_default_daily_limit(self, service: str) -> int:
        """Get default daily limit for a service"""
        defaults = {
            'openai': 100000,  # 100k tokens per day
            'anthropic': 80000,  # 80k tokens per day
            'google': 150000,  # 150k tokens per day
        }
        return defaults.get(service, 50000)

    def _get_default_monthly_limit(self, service: str) -> int:
        """Get default monthly limit for a service"""
        defaults = {
            'openai': 3000000,  # 3M tokens per month
            'anthropic': 2400000,  # 2.4M tokens per month
            'google': 4500000,  # 4.5M tokens per month
        }
        return defaults.get(service, 1500000)
```

### 3. Secure API Gateway

#### Request Proxy with Security
```python
# secure_api_proxy.py
from flask import Flask, request, jsonify
import openai
import threading
import logging
from typing import Dict, Any

app = Flask(__name__)

# Initialize security components
rate_limiter = RateLimiter()
quota_manager = StudentQuotaManager()
api_manager = SecureAPIManager()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/llm/<service>/chat/completions', methods=['POST'])
def proxy_chat_completion(service):
    """Secure proxy for LLM chat completions"""
    try:
        # Extract student ID from authentication
        student_id = get_student_id_from_auth()
        if not student_id:
            return jsonify({'error': 'Authentication required'}), 401

        # Get request data
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-3.5-turbo')
        max_tokens = data.get('max_tokens', 1000)

        # Check rate limits
        if not rate_limiter.is_allowed(service, student_id, estimate_tokens(messages)):
            return jsonify({'error': 'Rate limit exceeded'}), 429

        # Check student quotas
        quota = quota_manager.get_daily_quota(student_id, service)
        if quota['remaining'] <= 0:
            return jsonify({'error': 'Daily quota exceeded'}), 429

        # Get API key securely
        api_key = api_manager.retrieve_api_key(service)
        if not api_key:
            logger.error(f"Missing API key for service: {service}")
            return jsonify({'error': 'Service unavailable'}), 503

        # Prepare the request (sanitize sensitive data)
        sanitized_data = sanitize_request_data(data)

        # Log the request for audit purposes
        log_request(student_id, service, sanitized_data)

        # Make the actual API call
        response = make_llm_request(service, api_key, sanitized_data)

        # Consume quota
        tokens_used = estimate_tokens(response.get('choices', []))
        quota_manager.consume_quota(student_id, service, tokens_used)

        # Log the response
        log_response(student_id, service, tokens_used)

        return jsonify(response)

    except Exception as e:
        logger.error(f"API proxy error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def get_student_id_from_auth():
    """Extract student ID from authentication headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    # Validate token and return student ID
    # Implementation would validate JWT or other auth mechanism
    return validate_student_token(token)

def estimate_tokens(data) -> int:
    """Estimate number of tokens in request/response"""
    # Simple estimation - in practice, use proper token counting
    text = str(data)
    return len(text) // 4  # Rough estimation

def sanitize_request_data(data: Dict) -> Dict:
    """Remove sensitive information from request data"""
    sanitized = data.copy()

    # Remove any potential PII from messages
    if 'messages' in sanitized:
        for message in sanitized['messages']:
            if 'content' in message:
                # Apply content filtering here
                message['content'] = filter_content(message['content'])

    return sanitized

def filter_content(content: str) -> str:
    """Filter potentially sensitive content"""
    # Remove potential email addresses, phone numbers, etc.
    import re

    # Filter email addresses
    content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REMOVED]', content)

    # Filter phone numbers
    content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REMOVED]', content)

    return content

def log_request(student_id: str, service: str, data: Dict):
    """Log request for audit and monitoring"""
    logger.info(f"Request: student={student_id}, service={service}, data_keys={list(data.keys())}")

def log_response(student_id: str, service: str, tokens_used: int):
    """Log response for audit and monitoring"""
    logger.info(f"Response: student={student_id}, service={service}, tokens_used={tokens_used}")

def make_llm_request(service: str, api_key: str, data: Dict) -> Dict:
    """Make the actual LLM request"""
    if service == 'openai':
        openai.api_key = api_key
        return openai.ChatCompletion.create(**data)
    # Add other services as needed
    else:
        raise ValueError(f"Unsupported service: {service}")

def validate_student_token(token: str) -> str:
    """Validate student authentication token"""
    # Implementation would validate JWT or other token type
    # and return student ID
    pass
```

## Student Data Protection

### 1. Data Encryption

#### End-to-End Encryption
```python
# data_encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Union

class DataEncryptionManager:
    def __init__(self):
        self.key = self._get_encryption_key()

    def _get_encryption_key(self) -> bytes:
        """Get encryption key from secure source"""
        # Use environment variable or secure storage
        key = os.environ.get('DATA_ENCRYPTION_KEY')
        if key:
            return base64.urlsafe_b64decode(key)

        # Generate new key (should be stored securely)
        key = Fernet.generate_key()
        # In production, securely store this key
        return key

    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data"""
        f = Fernet(self.key)
        if isinstance(data, str):
            data = data.encode()

        encrypted_data = f.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        f = Fernet(self.key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_bytes = f.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()

    def encrypt_student_data(self, student_id: str, data: Dict) -> Dict:
        """Encrypt sensitive student data"""
        encrypted_data = data.copy()

        # Encrypt sensitive fields
        sensitive_fields = ['email', 'phone', 'address', 'personal_info']
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[f'{field}_encrypted'] = self.encrypt_data(str(encrypted_data[field]))
                del encrypted_data[field]

        # Add metadata
        encrypted_data['encrypted_at'] = str(datetime.now().isoformat())
        encrypted_data['student_id'] = student_id

        return encrypted_data

    def decrypt_student_data(self, encrypted_data: Dict) -> Dict:
        """Decrypt sensitive student data"""
        decrypted_data = encrypted_data.copy()

        # Decrypt sensitive fields
        for key in list(decrypted_data.keys()):
            if key.endswith('_encrypted'):
                original_key = key[:-10]  # Remove '_encrypted' suffix
                decrypted_data[original_key] = self.decrypt_data(decrypted_data[key])
                del decrypted_data[key]

        return decrypted_data
```

### 2. Privacy-Preserving Analytics

#### Differential Privacy
```python
# differential_privacy.py
import numpy as np
from typing import List, Dict, Any
import math

class DifferentialPrivacyManager:
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon

    def add_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """Add Laplace noise for differential privacy"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

    def privatize_histogram(self, data: List[int], bins: int) -> List[float]:
        """Privatize a histogram"""
        # Create histogram
        hist, _ = np.histogram(data, bins=bins)

        # Add noise to each bin
        privatized_hist = [self.add_noise(count) for count in hist]

        # Ensure non-negative values
        privatized_hist = [max(0, count) for count in privatized_hist]

        return privatized_hist

    def privatize_average(self, values: List[float]) -> float:
        """Calculate privatized average"""
        if not values:
            return 0.0

        # Clip values to reasonable range
        clipped_values = [max(0, min(100, v)) for v in values]  # Assuming 0-100 range

        # Calculate average
        avg = sum(clipped_values) / len(clipped_values)

        # Add noise based on sensitivity
        sensitivity = 100.0 / len(values)  # Max change in average if one value changes
        privatized_avg = self.add_noise(avg, sensitivity)

        return max(0, min(100, privatized_avg))  # Ensure in range

    def privatize_student_performance(self, student_data: List[Dict]) -> Dict:
        """Privatize student performance data for analytics"""
        results = {}

        # Privatize average scores
        scores = [s.get('score', 0) for s in student_data if 'score' in s]
        results['average_score'] = self.privatize_average(scores)

        # Privatize completion rates
        completions = [s.get('completed', 0) for s in student_data]
        results['completion_rate'] = self.privatize_average(completions)

        # Privatize time spent
        times = [s.get('time_spent', 0) for s in student_data]
        results['average_time_spent'] = self.privatize_average(times)

        return results
```

### 3. Secure Data Storage

#### Database Security
```python
# secure_database.py
import sqlite3
import hashlib
import hmac
from cryptography.fernet import Fernet
from typing import Dict, List, Optional

class SecureDatabase:
    def __init__(self, db_path: str, encryption_key: bytes):
        self.db_path = db_path
        self.cipher = Fernet(encryption_key)
        self._init_db()

    def _init_db(self):
        """Initialize secure database with encrypted fields"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create students table with encrypted fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email_encrypted BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_hash TEXT  -- For integrity verification
            )
        ''')

        # Create course progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_progress (
                progress_id TEXT PRIMARY KEY,
                student_id TEXT,
                module_id INTEGER,
                data_encrypted BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_student(self, student_id: str, username: str, email: str) -> bool:
        """Add a new student with encrypted email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Encrypt email
            encrypted_email = self.cipher.encrypt(email.encode())

            # Create integrity hash
            data_to_hash = f"{student_id}{username}{email}".encode()
            data_hash = hashlib.sha256(data_to_hash).hexdigest()

            cursor.execute('''
                INSERT INTO students (student_id, username, email_encrypted, data_hash)
                VALUES (?, ?, ?, ?)
            ''', (student_id, username, encrypted_email, data_hash))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[Dict]:
        """Retrieve student with decrypted email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT student_id, username, email_encrypted, data_hash
            FROM students
            WHERE student_id = ?
        ''', (student_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            student_id, username, encrypted_email, stored_hash = row

            # Decrypt email
            try:
                email = self.cipher.decrypt(encrypted_email).decode()
            except:
                return None  # Decryption failed

            # Verify integrity
            data_to_verify = f"{student_id}{username}{email}".encode()
            calculated_hash = hashlib.sha256(data_to_verify).hexdigest()

            if hmac.compare_digest(calculated_hash, stored_hash):
                return {
                    'student_id': student_id,
                    'username': username,
                    'email': email
                }

        return None

    def add_course_progress(self, student_id: str, module_id: int, progress_data: Dict):
        """Add encrypted course progress data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Serialize and encrypt progress data
        data_json = str(progress_data)  # In practice, use proper JSON serialization
        encrypted_data = self.cipher.encrypt(data_json.encode())

        cursor.execute('''
            INSERT INTO course_progress (student_id, module_id, data_encrypted)
            VALUES (?, ?, ?)
        ''', (student_id, module_id, encrypted_data))

        conn.commit()
        conn.close()
```

## Authentication and Authorization

### 1. JWT-Based Authentication

#### Secure JWT Implementation
```python
# jwt_auth.py
import jwt
import datetime
from typing import Dict, Optional, Tuple
import os

class JWTAuthManager:
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY')
        if not self.secret_key:
            # Generate a new secret key (should be stored securely in production)
            import secrets
            self.secret_key = secrets.token_urlsafe(32)

    def generate_token(self, student_id: str, username: str, role: str = 'student') -> str:
        """Generate JWT token for student"""
        payload = {
            'student_id': student_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),  # 24-hour expiration
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an existing token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        # Create new token with extended expiration
        new_payload = payload.copy()
        new_payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        new_payload['iat'] = datetime.datetime.utcnow()
        new_payload['refreshed_at'] = datetime.datetime.utcnow().isoformat()

        return jwt.encode(new_payload, self.secret_key, algorithm='HS256')

    def validate_student_access(self, token: str, required_role: str = 'student') -> Tuple[bool, Optional[Dict]]:
        """Validate student access and return student info"""
        payload = self.verify_token(token)
        if not payload:
            return False, None

        if payload.get('role') != required_role and required_role != 'any':
            return False, None

        return True, payload
```

### 2. Role-Based Access Control

#### RBAC Implementation
```python
# rbac.py
from enum import Enum
from typing import Dict, List, Set
import functools

class Role(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    TA = "ta"

class RBACManager:
    def __init__(self):
        self.role_permissions = {
            Role.STUDENT: {
                'read_own_progress',
                'submit_assignments',
                'access_course_materials',
                'participate_discussions'
            },
            Role.TA: {
                'read_own_progress',
                'submit_assignments',
                'access_course_materials',
                'participate_discussions',
                'grade_assignments',
                'view_student_progress'
            },
            Role.TEACHER: {
                'read_own_progress',
                'submit_assignments',
                'access_course_materials',
                'participate_discussions',
                'grade_assignments',
                'view_student_progress',
                'manage_course',
                'view_analytics'
            },
            Role.ADMIN: {
                'read_own_progress',
                'submit_assignments',
                'access_course_materials',
                'participate_discussions',
                'grade_assignments',
                'view_student_progress',
                'manage_course',
                'view_analytics',
                'manage_users',
                'system_admin'
            }
        }

    def has_permission(self, role: Role, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.role_permissions.get(role, set())

    def get_permissions(self, role: Role) -> Set[str]:
        """Get all permissions for a role"""
        return self.role_permissions.get(role, set())

    def require_permission(self, required_permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract role from request context (implementation depends on your framework)
                # This is a simplified example
                user_role = get_current_user_role()  # Implementation needed
                if not self.has_permission(user_role, required_permission):
                    raise PermissionError(f"Permission '{required_permission}' required")
                return func(*args, **kwargs)
            return wrapper
        return decorator

def get_current_user_role():
    """Get current user's role from request context"""
    # Implementation depends on your web framework
    # This is a placeholder
    pass

# Example usage
rbac = RBACManager()

@rbac.require_permission('view_student_progress')
def get_student_progress(student_id: str):
    """Only users with 'view_student_progress' permission can access this"""
    # Implementation here
    pass
```

## Audit and Monitoring

### 1. Comprehensive Logging

#### Security Event Logging
```python
# security_logging.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    def __init__(self, log_file: str = "security_events.log"):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # Create file handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_api_access(self, student_id: str, service: str, tokens_used: int, success: bool):
        """Log API access events"""
        event = {
            'event_type': 'api_access',
            'student_id': student_id,
            'service': service,
            'tokens_used': tokens_used,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))

    def log_authentication_event(self, student_id: str, event_type: str, success: bool, details: Dict[str, Any] = None):
        """Log authentication events"""
        event = {
            'event_type': f'auth_{event_type}',
            'student_id': student_id,
            'success': success,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))

    def log_data_access(self, student_id: str, action: str, resource: str, success: bool):
        """Log data access events"""
        event = {
            'event_type': 'data_access',
            'student_id': student_id,
            'action': action,
            'resource': resource,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))

    def log_security_alert(self, alert_type: str, severity: str, details: Dict[str, Any]):
        """Log security alerts"""
        event = {
            'event_type': 'security_alert',
            'alert_type': alert_type,
            'severity': severity,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.warning(json.dumps(event))

# Initialize security logger
security_logger = SecurityLogger()
```

### 2. Threat Detection

#### Anomaly Detection
```python
# threat_detection.py
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

class ThreatDetectionSystem:
    def __init__(self):
        self.access_patterns = {}  # student_id -> list of access times
        self.token_usage = {}      # student_id -> list of token usages
        self.anomaly_threshold = 3.0  # Standard deviations for anomaly detection

    def record_access(self, student_id: str, tokens_used: int = 0):
        """Record access event for anomaly detection"""
        now = datetime.utcnow().timestamp()

        # Record access time
        if student_id not in self.access_patterns:
            self.access_patterns[student_id] = []
        self.access_patterns[student_id].append(now)

        # Record token usage
        if student_id not in self.token_usage:
            self.token_usage[student_id] = []
        self.token_usage[student_id].append(tokens_used)

    def detect_anomalies(self, student_id: str) -> List[str]:
        """Detect potential security anomalies for a student"""
        anomalies = []

        # Check access frequency
        if self._check_access_frequency(student_id):
            anomalies.append("Unusual access frequency")

        # Check token usage patterns
        if self._check_token_usage_anomaly(student_id):
            anomalies.append("Unusual token usage pattern")

        # Check access timing
        if self._check_access_timing(student_id):
            anomalies.append("Access outside normal hours")

        return anomalies

    def _check_access_frequency(self, student_id: str) -> bool:
        """Check if access frequency is unusual"""
        if student_id not in self.access_patterns:
            return False

        accesses = self.access_patterns[student_id]
        if len(accesses) < 10:  # Need sufficient data
            return False

        # Calculate access rate in last hour
        one_hour_ago = datetime.utcnow().timestamp() - 3600
        recent_accesses = [t for t in accesses if t > one_hour_ago]
        recent_rate = len(recent_accesses)

        # Calculate historical average
        historical_rates = []
        for i in range(24):  # Check last 24 hours
            hour_start = one_hour_ago - (i * 3600)
            hour_end = hour_start + 3600
            hour_accesses = [t for t in accesses if hour_start < t <= hour_end]
            historical_rates.append(len(hour_accesses))

        if not historical_rates:
            return False

        avg_rate = np.mean(historical_rates)
        std_rate = np.std(historical_rates)

        if std_rate == 0:  # Avoid division by zero
            return recent_rate > avg_rate * 2

        z_score = (recent_rate - avg_rate) / std_rate
        return z_score > self.anomaly_threshold

    def _check_token_usage_anomaly(self, student_id: str) -> bool:
        """Check if token usage is unusual"""
        if student_id not in self.token_usage:
            return False

        usages = self.token_usage[student_id]
        if len(usages) < 5:
            return False

        recent_usage = usages[-5:]  # Last 5 requests
        avg_usage = np.mean(usages[:-5]) if len(usages) > 5 else np.mean(usages)
        std_usage = np.std(usages[:-5]) if len(usages) > 5 else np.std(usages)

        if std_usage == 0:
            return np.mean(recent_usage) > avg_usage * 3

        z_scores = [(usage - avg_usage) / std_usage for usage in recent_usage]
        return any(z > self.anomaly_threshold for z in z_scores)

    def _check_access_timing(self, student_id: str) -> bool:
        """Check if access timing is unusual"""
        if student_id not in self.access_patterns:
            return False

        accesses = self.access_patterns[student_id]
        if len(accesses) < 5:
            return False

        # Convert to hours of day
        hours = [datetime.fromtimestamp(t).hour for t in accesses[-24:]]  # Last 24 accesses

        # Define normal hours (8 AM to 10 PM)
        normal_hours = set(range(8, 23))
        unusual_accesses = [h for h in hours if h not in normal_hours]

        # If more than 30% of accesses are outside normal hours
        return len(unusual_accesses) / len(hours) > 0.3

# Initialize threat detection system
threat_detector = ThreatDetectionSystem()
```

## Compliance and Data Governance

### 1. GDPR Compliance

#### Data Subject Rights Implementation
```python
# gdpr_compliance.py
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class GDPRComplianceManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def right_to_access(self, student_id: str) -> Dict:
        """Implement right to access - provide all personal data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get student information
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student_data = cursor.fetchone()

        # Get course progress
        cursor.execute("SELECT * FROM course_progress WHERE student_id = ?", (student_id,))
        progress_data = cursor.fetchall()

        # Get API usage
        cursor.execute("SELECT * FROM api_usage WHERE student_id = ?", (student_id,))
        api_usage = cursor.fetchall()

        conn.close()

        return {
            'student_data': student_data,
            'course_progress': progress_data,
            'api_usage': api_usage,
            'request_timestamp': datetime.utcnow().isoformat()
        }

    def right_to_rectification(self, student_id: str, updates: Dict) -> bool:
        """Implement right to rectification - update inaccurate data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update student information
            if 'email' in updates:
                cursor.execute(
                    "UPDATE students SET email_encrypted = ? WHERE student_id = ?",
                    (updates['email'], student_id)
                )

            # Log the update for audit trail
            cursor.execute('''
                INSERT INTO data_changes (student_id, field_changed, old_value, new_value, changed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, 'email', '[REDACTED]', '[REDACTED]', datetime.utcnow().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error updating data: {e}")
            return False

    def right_to_erasure(self, student_id: str) -> bool:
        """Implement right to erasure - delete all personal data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Anonymize instead of delete to maintain analytics integrity
            cursor.execute('''
                UPDATE students
                SET username = 'ANONYMIZED',
                    email_encrypted = 'REDACTED',
                    data_hash = 'REDACTED'
                WHERE student_id = ?
            ''', (student_id,))

            # Remove course progress data
            cursor.execute("DELETE FROM course_progress WHERE student_id = ?", (student_id,))

            # Anonymize API usage data
            cursor.execute('''
                UPDATE api_usage
                SET student_id = 'ANONYMIZED_' || student_id
                WHERE student_id = ?
            ''', (student_id,))

            # Log the erasure
            cursor.execute('''
                INSERT INTO data_erasure_log (student_id, erased_at, reason)
                VALUES (?, ?, ?)
            ''', (student_id, datetime.utcnow().isoformat(), 'Right to erasure request'))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error erasing data: {e}")
            return False

    def right_to_data_portability(self, student_id: str) -> str:
        """Implement right to data portability - provide data in structured format"""
        data = self.right_to_access(student_id)
        return json.dumps(data, indent=2, default=str)

    def consent_management(self, student_id: str, purpose: str, granted: bool) -> bool:
        """Manage consent for data processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if consent record exists
            cursor.execute('''
                SELECT consent_id FROM consents
                WHERE student_id = ? AND purpose = ?
            ''', (student_id, purpose))

            if cursor.fetchone():
                # Update existing consent
                cursor.execute('''
                    UPDATE consents
                    SET granted = ?, updated_at = ?
                    WHERE student_id = ? AND purpose = ?
                ''', (granted, datetime.utcnow().isoformat(), student_id, purpose))
            else:
                # Create new consent record
                cursor.execute('''
                    INSERT INTO consents (student_id, purpose, granted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, purpose, granted, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error managing consent: {e}")
            return False

    def get_consent_status(self, student_id: str, purpose: str) -> Optional[bool]:
        """Get consent status for a specific purpose"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT granted FROM consents
            WHERE student_id = ? AND purpose = ?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (student_id, purpose))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None
```

This comprehensive security and privacy guide provides:

1. **API Key Management**: Secure storage and rotation of LLM API keys
2. **Access Control**: Rate limiting, quotas, and student-specific limits
3. **Data Encryption**: End-to-end encryption for sensitive data
4. **Privacy Protection**: Differential privacy for analytics
5. **Authentication**: JWT-based authentication with role-based access
6. **Audit Logging**: Comprehensive logging of security events
7. **Threat Detection**: Anomaly detection for unusual access patterns
8. **Compliance**: GDPR compliance with data subject rights
9. **Secure Architecture**: Proxy-based API access with filtering

The implementation provides multiple layers of security to protect both student data and API credentials while maintaining the functionality needed for the Physical AI & Humanoid Robotics course.

Last updated: December 13, 2025