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
