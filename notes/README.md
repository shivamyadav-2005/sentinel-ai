# SentinelAI Engineering Handbook

## 1. Project Overview

SentinelAI is a planned AI-powered personal assistant with a specialized cloud security agent.

Its long-term capabilities include general conversation, document retrieval, AWS security auditing, threat analysis, incident investigation, and controlled remediation.

## 2. Development Environment

- Operating system: Windows 11
- Code editor: Visual Studio Code
- Version control: Git
- Programming language: Python 3.12.10
- Package manager: pip 25.0.1
- Repository strategy: Monorepo

## 3. Technology Stack

| Technology | Purpose | Status |
|---|---|---|
| Python | Backend and security tooling | Installed |
| FastAPI | Backend API | Planned |
| React | Web frontend | Planned |
| PostgreSQL | Application database | Planned |
| pgvector | Vector search for RAG | Planned |
| Boto3 | AWS integration | Planned |
| Terraform | Infrastructure as Code | Planned |
| Docker | Application containerization | Planned |
| GitHub Actions | CI/CD | Planned |

## 4. Git and GitHub

Git is a distributed version-control system. It records changes in commits and supports branches and collaboration.

GitHub hosts Git repositories remotely and provides collaboration, issue tracking, and pull requests.

## 5. Windows PATH Troubleshooting

### Problem

The `python` command initially opened the Microsoft Store alias or was not recognized.

### Diagnosis

The actual interpreter existed at:

`%LocalAppData%\\Programs\\Python\\Python312\\python.exe`

Running it directly confirmed Python 3.12.10 and pip 25.0.1 were installed.

### Resolution

Python's installation directory and Scripts directory were added to the user PATH. VS Code was restarted so new terminals could inherit the updated environment.

### Lesson

Successful installation, executable discovery, and environment-variable configuration are separate concerns.

## 6. Project Structure

- `backend/`: API, AI orchestration, and security logic
- `frontend/`: Web interface
- `infrastructure/terraform/`: Infrastructure definitions
- `tests/`: Automated tests
- `docs/`: Architecture and security documentation
- `notes/`: Learning notes and interview preparation

## 7. Security Principles

- Never commit secrets.
- Apply least privilege.
- Validate user input.
- Treat AI output as untrusted.
- Gate sensitive actions behind authorization.
- Log and verify security-sensitive operations.

## 8. Current Milestone

Initial repository structure and configuration files.

## 9. Next Milestone

Initialize Git, connect the GitHub remote, and create the first commit.


## 11. First Working Backend

### Technology
- FastAPI: API framework
- Uvicorn: ASGI web server

### Run the server
python -m uvicorn backend.main:app --reload

### Endpoints
- GET /: Root endpoint
- GET /health: Health check
- GET /docs: Interactive API documentation

### HTTP Status Codes
- 200 OK: Request succeeded.
- 404 Not Found: Requested resource does not exist.

### Current Status
The backend starts successfully.
Both the root endpoint and health endpoint return 200 OK.
The favicon request returns 404 because no favicon has been configured.



## 12. Automated Testing

### Tools
- pytest: Runs automated tests.
- HTTPX: Provides the HTTP client used by FastAPI's TestClient.

### Run tests
python -m pytest -v

### Current tests
- test_root_endpoint: Checks the root response.
- test_health_endpoint: Checks the health response.

### Why automated tests?
- Detect regressions after code changes.
- Verify expected status codes and response data.
- Reduce the need for repetitive manual testing.

### Current milestone
Automated tests added for the root and health endpoints.



## 13. Configuration Management

### Package
- pydantic-settings: Loads and validates application settings.

### Configuration module
- File: backend/config.py
- Settings are defined in a Settings class.
- Environment variables can override default values.
- A local .env file can provide development settings.

### Security
- Never commit real credentials or API keys.
- Keep .env private.
- Use .env.example to document required configuration keys.

### Current milestone
Centralized application configuration has been added.




## 14. Configuration Testing

### Tests implemented
- Verify the default application name.
- Verify environment-variable overrides.
- Use pytest's monkeypatch fixture to isolate environment changes.
- Set `_env_file=None` to prevent `.env` values from affecting these tests.

### Key learning
Environment-variable overrides allow application settings to change
without modifying Python source code.

### Current milestone
Automated tests cover configuration defaults and environment overrides.


## 15. Backend Structure and Error Handling

### Route organization
- `backend/routes/health.py` contains the root and health endpoints.
- `backend/routes/__init__.py` marks the routes directory as a Python package.
- `backend/main.py` creates the FastAPI application and registers the router.

### Error handling
- `backend/errors.py` defines the reusable `APIError` exception.
- `resource_not_found()` creates a standard HTTP 404 error.
- `backend/main.py` registers a custom exception handler for `APIError`.
- Custom API errors return a JSON body containing the error message and status code.

### Testing
- Tests cover the configuration defaults and environment overrides.
- Tests cover the root and health endpoints.
- Tests verify the custom error helper and its HTTP response format.

### Current milestone
Backend routes have been separated from application setup, and custom API error handling has been implemented and tested.


## 16. Request Validation with Pydantic

### Request schema
- File: `backend/schemas.py`
- `ScanRequest` defines the expected scan request fields.
- `region` must contain at least one character.
- `scan_name` must contain between 1 and 100 characters.

### Scan endpoint
- File: `backend/routes/scans.py`
- Method: POST
- Path: `/scans/`
- Validates request data using `ScanRequest`.
- Returns the validated request data.
- Does not execute an AWS scan yet.

### Application integration
- File: `backend/main.py`
- Registers the scans router with the FastAPI application.

### Testing
- File: `tests/test_schemas.py`
- Tests valid schema data and rejects empty fields.
- `tests/test_main.py` tests valid scan requests and rejects an empty region with HTTP 422.

### Current milestone
Request validation is implemented and covered by automated tests.


## 17. Advanced Request Validation

### Objective

Improve the security and reliability of SentinelAI's scan
request API by validating user input before processing it.

### 17.1 Whitespace Validation

We configured the ScanRequest Pydantic model using:

```python
model_config = ConfigDict(str_strip_whitespace=True)
```

This automatically removes leading and trailing whitespace
from string fields before validation.

Examples:

- `"  Security Audit  "` becomes `"Security Audit"`
- `"   "` is rejected by the minimum-length constraint.

### 17.2 AWS Region Format Validation

We added a custom Pydantic field validator:

```python
@field_validator("region")
@classmethod
def validate_region_format(cls, value: str) -> str:
    pattern = r"^[a-z]{2}(?:-gov)?-[a-z]+-\d+$"

    if not re.fullmatch(pattern, value):
        raise ValueError(
            "Region must follow a format such as ap-south-1"
        )

    return value
```

This checks whether the supplied region follows a common
AWS region naming pattern.

Examples:

- `ap-south-1` — accepted
- `eu-west-2` — accepted
- `abc` — rejected
- `ap-south` — rejected

Important: Format validation does not confirm that the
region exists or is enabled in an AWS account.

### 17.3 Automated Testing

We added tests covering:

- Whitespace-only region rejection
- Whitespace-only scan name rejection
- Automatic whitespace trimming
- Invalid region-format rejection
- Valid region-format acceptance

Latest test result:

16 passed, 1 non-blocking deprecation warning.

### 17.4 Engineering Concepts Learned

- Input sanitization
- Pydantic ConfigDict
- Custom field validators
- Regular expressions
- Defensive API design
- Automated validation testing

### Next Steps

- Commit and push validation improvements
- Continue developing the scan API
- Prepare the AWS security scanning service


## 18. S3 Public-Access Configuration Analysis

### Objective

Create the first cloud security analysis service for SentinelAI
without requiring an AWS account during development.

### 18.1 Service Structure

Created the following files:

- `backend/services/__init__.py`
- `backend/services/s3_scanner.py`
- `tests/test_s3_scanner.py`

The service layer separates security analysis from API routes.

### 18.2 Scanner Function

The function `analyze_bucket_public_access()` accepts a bucket
name and public-access-block configuration.

It checks these four S3 settings:

- `BlockPublicAcls`
- `IgnorePublicAcls`
- `BlockPublicPolicy`
- `RestrictPublicBuckets`

If all four settings are enabled, the result is `PASS` with
`INFO` severity.

If one or more settings are disabled, the result is `WARNING`
with `HIGH` severity.

If configuration is unavailable, the result is `WARNING`.
Missing configuration does not prove that a bucket is public.

### 18.3 Testing Strategy

Tests use sample dictionaries rather than real AWS requests.

Scenarios covered:

1. All four protections enabled.
2. A public-access protection disabled.
3. Public-access configuration unavailable.

Latest full test result: 19 passed, 1 non-blocking warning.

### 18.4 Current Limitations

- The scanner does not connect to AWS.
- It does not retrieve real bucket configurations.
- It does not inspect bucket policies or ACLs.
- A disabled protection setting does not by itself prove public exposure.
- No AWS resources are modified.

### 18.5 Next Steps

- Add the S3 scanner's API and AWS integration design.
- Test AWS responses using mocks.
- Inspect bucket policies and ACLs to assess public exposure.
- Return structured findings through the scan API.


## 19. S3 Bucket Policy Analysis

### Objective

Extend the S3 scanner to identify potentially risky bucket
policies using sample policy data, without connecting to AWS.

### 19.1 New Function

Implemented `analyze_bucket_policy()` in
`backend/services/s3_scanner.py`.

The function examines policy statements and identifies
`Allow` statements containing wildcard principals.

Supported examples include:

- `"Principal": "*"`
- `"Principal": {"AWS": "*"}`

It also handles the `AWS` principal represented as a list.

### 19.2 Findings

- A matching wildcard principal produces a `WARNING`
  with `HIGH` severity.
- A missing policy produces a `WARNING` with `MEDIUM`
  severity because exposure cannot be assessed.
- No matching wildcard principal produces `PASS` for this
  specific check.

### 19.3 Automated Tests

Added tests for:

1. Wildcard principal detection.
2. A non-wildcard AWS principal.
3. Missing bucket policy.

Latest full test result: 22 passed, 1 non-blocking warning.

### 19.4 Limitations

This is a basic policy pattern check, not a complete AWS
authorization evaluator.

It does not evaluate all policy conditions, explicit denies,
ACLs, access points, or the effective permissions created
by other AWS controls.

A wildcard principal is a potential risk indicator, not
proof that a bucket is publicly accessible.

### Next Steps

- Review and commit the policy analyzer.
- Integrate the checks with the scan API.
- Later, retrieve real AWS policy data using Boto3.


## 20. Scan API Integration with S3 Analysis

### Objective

Connect the existing S3 security analysis functions to
the FastAPI scan endpoint.

### 20.1 Updated Endpoint

The `POST /scans/` endpoint now:

1. Validates the request using `ScanRequest`.
2. Supplies sample public-access-block configuration.
3. Supplies a sample S3 bucket policy.
4. Runs both S3 analysis functions.
5. Returns the request, findings, and data source.

### 20.2 Response Structure

The response contains:

- `message`: indicates that mock analysis completed.
- `scan`: the validated scan request.
- `findings`: structured results from both checks.
- `source`: `mock_data`, identifying the sample data source.

The sample configuration produces a `PASS` finding for
public-access-block settings and a `WARNING` finding for
a policy containing a wildcard principal.

### 20.3 Testing

Updated the scan endpoint test to verify the new response
structure and both finding statuses.

Latest full test result: 22 passed, 1 non-blocking warning.

### 20.4 Current Limitations

- The endpoint uses hard-coded sample data.
- It does not connect to AWS or inspect real buckets.
- The findings are demonstrations, not real security results.
- Wildcard-principal detection is a basic policy check,
  not a complete AWS authorization evaluation.

### Next Steps

- Commit and push the API integration.
- Separate mock data from production scanning logic.
- Add a proper AWS client layer when AWS access is available.


## 21. Separating Mock Data from API Routes

### Objective

Separate sample S3 data from the scan API route to improve
code organization and prepare for future AWS integration.

### 21.1 New Module

Created `backend/services/s3_mock_data.py` with three functions:

- `get_mock_bucket_name()`
- `get_mock_public_access_block()`
- `get_mock_bucket_policy()`

These functions return fictional bucket information and
sample security configuration data for local development.

### 21.2 Updated Scan Route

Updated `backend/routes/scans.py` to import the mock-data
functions and pass their results to the existing S3 analysis
functions.

The route remains responsible for handling the API request
and returning the structured findings.

### 21.3 Separation of Responsibilities

- `s3_mock_data.py` provides sample data.
- `s3_scanner.py` analyzes the supplied data.
- `scans.py` handles the API request and response.

### 21.4 Testing

The complete test suite passed after the refactoring.

Latest result: 22 passed, 1 non-blocking warning.

### 21.5 Current Limitations

The endpoint still uses mock data. It does not connect to AWS,
retrieve real bucket configurations, or perform a live scan.

### Next Steps

- Commit and push the refactoring.
- Introduce an AWS client layer when AWS access is available.
- Keep mock-based tests so development can continue locally.

## 22. Expanded S3 Scanner Test Coverage

### Objective

Improve confidence in the S3 security analysis logic by testing additional bucket policy scenarios.

### 22.1 Public Access Block Tests

Tested configurations where all four public-access protections are enabled, where a protection is disabled, and where the configuration is missing.

### 22.2 Bucket Policy Tests

Added coverage for:
- A wildcard `Principal` set to `"*"`.
- A wildcard AWS principal represented as a dictionary.
- A wildcard AWS principal included in a list.
- A non-wildcard AWS principal.
- A wildcard principal in an explicit `Deny` statement.
- Multiple policy statements with different principals.
- A missing bucket policy.

### 22.3 Test Results

Latest test result: **26 passed, 0 failed, 1 warning.**

The warning concerns deprecated `httpx` integration in the installed Starlette test client. It does not prevent the test suite from passing.

### 22.4 Security Limitations

These tests validate the behavior of SentinelAI's basic policy-pattern checks. They do not prove whether an S3 bucket is publicly accessible in every possible AWS configuration. Full access evaluation requires considering policy conditions, explicit denies, ACLs, access points, and other applicable controls.

### Next Steps

- Review the scanner's handling of malformed or unexpected policy data.
- Add more edge-case tests.
- Commit and push the verified changes after reviewing Git status.

## 23. S3 Scanner Input Validation and Hardening

### Objective

Improve the scanner's handling of missing, malformed, or unexpected S3 security configuration data.

### 23.1 Public Access Block Validation

The scanner now checks whether the public-access configuration and its settings are dictionaries. Missing or invalid settings return a warning rather than a passing result.

Each of the four public-access protection settings must be explicitly set to `True` for the check to pass.

### 23.2 Bucket Policy Validation

The scanner validates the policy structure before analyzing statements. It handles:
- Missing policy data.
- Missing `Statement` fields.
- Invalid `Statement` types.
- Invalid individual statements.
- Statements with missing or unsupported `Effect` values.

Malformed or incomplete policy data produces a warning instead of being silently treated as safe.

### 23.3 Test Results

Latest test result: **33 passed, 0 failed, 1 warning.**

The remaining warning concerns deprecated `httpx` integration in the installed Starlette test client. It does not prevent the test suite from passing.

### 23.4 Security Limitations

The scanner detects selected wildcard-principal patterns and validates basic input structure. It does not calculate effective AWS permissions or guarantee that a bucket is private.

Further improvements should consider policy conditions, explicit denies, ACLs, access points, and other AWS authorization controls.

### Next Steps

- Review the API response for malformed input scenarios.
- Add dedicated tests for any newly identified edge cases.
- Commit and push the verified changes after checking Git status.

## 24. Scan API Request Validation Tests

### Objective

Expand API test coverage to verify that invalid scan requests are rejected before reaching the scanner.

### 24.1 Valid Request

Verified that a valid scan request returns HTTP 200 and includes the expected scan details, mock-data source, and security findings.

### 24.2 Invalid Request Scenarios

Added tests for:
- Missing `region`.
- Missing `scan_name`.
- Empty region.
- Empty scan name.
- Whitespace-only values.
- Invalid region format.
- JSON arrays instead of JSON objects.
- Malformed JSON request bodies.

These invalid requests are expected to return HTTP 422.

### 24.3 Test Results

Latest test result: **40 passed, 0 failed, 1 warning.**

The warning concerns deprecated `httpx` integration in the installed Starlette test client and does not prevent the tests from passing.

### 24.4 Scope

This milestone improves automated verification of request validation. It does not introduce new application behavior or connect the API to AWS.

### Next Steps

- Review the current API and error-handling implementation.
- Identify any remaining validation or response-handling gaps.
- Commit and push the verified changes after checking Git status.