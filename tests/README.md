# Keycloak iam_spi API Testing Suite

Python testing framework for the Keycloak iam_spi custom extension API endpoints.

## Overview

This testing suite provides automated tests for all iam_spi REST API endpoints including:
- User management
- Institution management
- Mail/messaging
- Event management
- Network management
- CSV export functionality
- Role-based permission testing
- Integration testing

Client (UI) tests are located in `client/src/tests`.

## Prerequisites

- Python 3.8 or higher
- pip
- A running instance of this software in development mode (see docker/README.md)

## Dependencies

```bash
cd tests
pip install -r requirements.txt
```

- Firefox browser installed
- GeckoDriver (automatically managed by webdriver-manager)

## Running Tests

### Quick Start

```bash
cd docker
docker compose --env-file dev.env -f docker-compose.yml -f docker-compose.dev.yml down --volumes
docker compose --env-file dev.env -f docker-compose.yml -f docker-compose.dev.yml up -d
cd ../tests
./run_tests.py
# or
pytest
```

### Run Specific Test Suites

```bash
./run_tests.py user              # Run user API tests only
./run_tests.py backend           # Run all backend API tests
./run_tests.py frontend          # Run frontend tests only
./run_tests.py institution       # Run institution tests
./run_tests.py mail event        # Run mail and event tests
./run_tests.py --verbose         # Run with verbose output
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLIENT_URL` | Client base URL | `http://localhost:48081` |
| `KEYCLOAK_URL` | Keycloak base URL | `http://localhost:48080` |
| `REALM` | Keycloak realm name | `imis3` |
| `CLIENT_ID` | OAuth2 client ID | `iam-client` |
| `CLIENT_SECRET` | OAuth2 client secret | `exampleclientsecret` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `30` |
| `DB_HOST` | Database hostname | `localhost` |
| `DB_PORT` | Database port | `2345` |
| `DB_USER` | Database username | `keycloak` |
| `DB_PASSWORD` | Database password | `secret` |
| `DB_NAME` | Database name | `keycloak` |
| `SELENIUM_HEADLESS` | Run Selenium Headless | `true` |

## Manually use helper function to delete a user/institution from the database

```bash
python3 -i lib/db_helpers.py
delete_user_from_db('6b19e3e3-c11e-4308-8f27-8f090d3b5fd5')
delete_institution_from_db(4)
delete_institution_from_db(institution_facil_name='test_5owza6aa')
```

## CI/CD Integration

### GitLab CI Example

See `.gitlab-ci.yml`.

Requires a shell executor.
The default `docker` executor can't start docker containers.

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd tests
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd tests
          ./run_tests.py
```
