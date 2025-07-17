# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-24

### Added

- Export and Import Agents

### Changed

- A2A implementation updated to version 0.2.1 (https://google.github.io/A2A/specification/#agent2agent-a2a-protocol-specification)
- Frontend redesign
- Fixed message order

## [0.0.11] - 2025-05-16

### Changed

- Fixes in email service and client service

## [0.0.10] - 2025-05-15

### Added

- Add Task Agent for structured single-task execution
- Improve context management in agent execution
- Add file support for A2A protocol (Agent-to-Agent) endpoints
- Implement multimodal content processing in A2A messages
- Add SMTP email provider support as alternative to SendGrid

## [0.0.9] - 2025-05-13

### Added

- Add API key sharing and flexible authentication for chat routes

### Changed

- Enhance user authentication with detailed error handling

## [0.0.8] - 2025-05-13

### Changed

- Update author information in multiple files

## [0.0.7] - 2025-05-13

### Added

- Docker image CI workflow for automated builds and pushes
- GitHub Container Registry (GHCR) integration
- Automated image tagging based on branch and commit
- Docker Buildx setup for multi-platform builds
- Cache optimization for faster builds
- Automated image publishing on push to main and develop branches

## [0.0.6] - 2025-05-13

### Added

- Initial public release of Evo AI platform
- FastAPI-based backend API
- JWT authentication with email verification
- Agent management (LLM, A2A, Sequential, Parallel, Loop, Workflow)
- Agent 2 Agent (A2A) protocol support (Google A2A spec)
- MCP server integration and management
- Custom tools management for agents
- Folder-based agent organization
- Secure API key management with encryption
- PostgreSQL and Redis integration
- Email notifications (SendGrid) with Jinja2 templates
- Audit log system for administrative actions
- LangGraph integration for workflow agents
- OpenTelemetry tracing and Langfuse integration
- Docker and Docker Compose support
- English documentation and codebase

### Changed

- N/A

### Fixed

- N/A

### Security

- JWT tokens with expiration and resource-based access control
- Secure password hashing (bcrypt)
- Account lockout after multiple failed login attempts
- Email verification and password reset flows

---

Older versions and future releases will be listed here.
