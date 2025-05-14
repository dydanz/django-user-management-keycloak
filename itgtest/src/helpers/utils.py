import faker
import random
import json
import os

fake = faker.Faker()

def generate_user_data():
    """Generate random user data for testing"""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "Test@123"  # Using a fixed password for testing
    }

def load_test_users():
    """Load test users from data file if exists"""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_users.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []

def save_test_users(users):
    """Save test users to data file"""
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_users.json')
    with open(data_file, 'w') as f:
        json.dump(users, f, indent=2)
