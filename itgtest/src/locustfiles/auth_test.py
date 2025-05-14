from locust import HttpUser, task, between
from helpers.utils import generate_user_data, load_test_users
from locust.exception import StopUser
import random
import logging

class UserBehavior(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"  # Django backend URL
    
    def on_start(self):
        self.test_users = load_test_users()
        self.current_user = None
        self.access_token = None

    @task(1)
    def register_and_login(self):
        if self.access_token:
            return
            
        # Generate random user data
        user_data = generate_user_data()
        
        # Register
        with self.client.post("/api/register/", json=user_data, catch_response=True) as response:
            if response.status_code == 201:
                logging.info(f"Successfully registered user: {user_data['username']}")
                self.current_user = user_data
            else:
                logging.error(f"Failed to register user: {response.text}")
                response.failure(f"Failed to register: {response.text}")
                return

        # Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        with self.client.post("/api/login/", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.access_token = response.json()["token"]
                logging.info(f"Successfully logged in user: {user_data['username']}")
            else:
                logging.error(f"Failed to login: {response.text}")
                response.failure(f"Failed to login: {response.text}")

    @task(2)
    def update_profile(self):
        if not self.access_token:
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Toggle MFA
        with self.client.post("/api/toggle-mfa/", headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                logging.error(f"Failed to toggle MFA: {response.text}")
                response.failure(f"Failed to toggle MFA: {response.text}")
                return

        # Update phone number
        phone_data = {"phone_number": f"+1555{random.randint(1000000, 9999999)}"}
        with self.client.post("/api/update-phone/", json=phone_data, headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                logging.error(f"Failed to update phone: {response.text}")
                response.failure(f"Failed to update phone: {response.text}")
    
    @task(1)
    def logout(self):
        if not self.access_token:
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        with self.client.post("/api/logout/", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                self.access_token = None
                self.current_user = None
                logging.info("Successfully logged out")
            else:
                logging.error(f"Failed to logout: {response.text}")
                response.failure(f"Failed to logout: {response.text}")
