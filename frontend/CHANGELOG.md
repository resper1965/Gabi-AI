# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.7] - 2025-05-15

### Added

- Add Task agents
- Add file support for A2A protocol (Agent-to-Agent) endpoints
- Add entrypoint script for dynamic environment variable handling
- Add agent card URL input and copy functionality

## [0.0.6] - 2025-05-13

### Added

- Agent sharing functionality with third parties via API keys
- Dedicated shared-chat page for accessing shared agents
- Local storage mechanism to save recently used shared agents
- Public access to shared agents without full authentication

### Changed

- Add example environment file and update .gitignore
- Add clientId prop to agent-related components and improve agent data processing
- Refactor middleware to handle shared agent routes as public paths
- Update API interceptors to prevent forced logout on shared chat pages

### security

- Implement force logout functionality on 401 Unauthorized responses

## [0.0.5] - 2025-05-13

### Changed

- Update author information in multiple files

## [0.0.4] - 2025-05-13

### Added
- Initial public release
- User-friendly interface for creating and managing AI agents
- Integration with multiple language models (e.g., GPT-4, Claude)
- Client management interface
- Visual configuration for MCP servers
- Custom tools management
- JWT authentication with email verification
- Agent 2 Agent (A2A) protocol support (Google's A2A spec)
- Workflow Agent with ReactFlow for visual workflow creation
- Secure API key management (encrypted storage)
- Agent organization with folders and categories
- Dashboard with agent overview, usage stats, and recent activities
- Agent editor for creating, editing, and configuring agents
- Workflow editor for building and visualizing agent flows
- API key manager for adding, encrypting, and rotating keys
- RESTful API and WebSocket backend integration
- Docker support for containerized deployment
- Complete documentation and contribution guidelines

---

Older versions and future releases will be listed here.
