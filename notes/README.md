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
