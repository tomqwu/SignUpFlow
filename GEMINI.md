# Project Standards and Guidelines

## Testing Requirements
- **100% Test Coverage**: Every change MUST be accompanied by tests.
- **Test Types**:
  - **Unit Tests**: For individual functions and components.
  - **Integration Tests**: For API endpoints and database interactions.
  - **E2E Tests**: For full user flows using Playwright.
- **Verification**: All tests must pass before marking a task as complete.

## Logging Requirements
- **Clean Logs**: Application logs should be free of errors and unhandled exceptions.
- **Error Handling**: All exceptions must be caught and handled gracefully. 500 Internal Server Errors are unacceptable.

## Development Workflow
- **Reproduction Scripts**: Create reproduction scripts for reported bugs before fixing them.
- **Test Isolation**: Tests must be isolated (separate DB/port) to avoid affecting the development environment.
