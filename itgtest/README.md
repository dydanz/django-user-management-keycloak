# Django User Management Load Testing

This directory contains Locust load tests for the Django User Management system with Keycloak integration.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the Django backend is running at http://localhost:8000

## Running the Tests

To run the load tests:

```bash
cd src
locust -f locustfiles/auth_test.py
```

Then open http://localhost:8089 in your browser to access the Locust web interface.

## Test Scenarios

The load tests cover the following scenarios:

1. User Registration
   - Generates random user data
   - Registers new users via `/api/register/`
   - Verifies successful registration

2. User Login
   - Logs in with registered user credentials
   - Gets authentication token
   - Verifies successful login

3. Profile Updates
   - Toggles MFA settings
   - Updates phone number
   - Verifies profile changes

4. User Logout
   - Performs user logout
   - Verifies session termination

## Configuration

- Default host is set to `http://localhost:8000`
- Wait time between tasks: 1-3 seconds
- Test data is stored in `src/data/test_users.json`

## Test Data

The tests use both:
- Generated random test data using Faker
- Predefined test users from test_users.json

## Metrics

The tests collect metrics for:
- Response times
- Request rates
- Error rates
- Number of concurrent users

## Error Handling

The tests include proper error handling and logging for:
- Registration failures
- Login failures
- Profile update failures
- Logout failures
