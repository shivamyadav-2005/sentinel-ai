# SentinelAI

AI-powered personal assistant and cloud security platform.

SentinelAI combines a general-purpose AI assistant with specialized cloud security capabilities, including AWS security auditing, threat analysis, incident investigation, and controlled remediation.

## Project Goals

- Build a conversational AI assistant.
- Add retrieval-augmented generation (RAG) for document-based answers.
- Create an AI agent with controlled tool access.
- Audit AWS IAM, S3, EC2, and security group configurations.
- Analyze security findings and prioritize risks.
- Implement approval-based remediation.
- Apply secure development and DevOps practices.

## Planned Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** React
- **AI:** Large language model (LLM), tool calling, RAG
- **Database:** PostgreSQL, with pgvector planned
- **Cloud:** AWS, Boto3
- **Infrastructure:** Terraform
- **DevOps:** Docker, GitHub Actions
- **Testing:** pytest and frontend testing tools

## Project Status

Currently in the initial environment and repository setup phase.

Features listed above are planned and are not yet implemented.

## Security

- Never commit API keys, AWS credentials, passwords, or `.env` files.
- Use least-privilege permissions for cloud access.
- Require authorization for sensitive operations.
- Keep security actions auditable.

## Development

Development instructions will be added as the backend and frontend are implemented.

## License

License to be decided before public release.
