# Contributing to Grace Trading System

## Development Process

1. **Fork the Repository**
   - Fork the repository on GitHub
   - Clone your fork locally

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Guidelines**
   - Follow the existing code style
   - Write clear commit messages
   - Add tests for new features
   - Update documentation as needed

4. **Code Style**
   - Python: Follow PEP 8
   - TypeScript/React: Follow project ESLint configuration
   - Use meaningful variable and function names
   - Add comments for complex logic

5. **Testing**
   - Write unit tests for new features
   - Ensure all tests pass before submitting PR
   - Add integration tests for API endpoints
   - Test frontend components

6. **Documentation**
   - Update README.md if needed
   - Document new features
   - Add JSDoc comments for TypeScript/JavaScript
   - Update API documentation

7. **Submit Pull Request**
   - Push changes to your fork
   - Create PR against main repository
   - Fill out PR template completely
   - Respond to review comments

## Project Structure

### Backend (Python)
- `src/api_server.py`: Main API server
- `src/gmgn_service.py`: GMGN integration
- `src/grace_core.py`: Core business logic
- `src/memory_system.py`: Memory management

### Frontend (React/TypeScript)
- `src/ui/components/`: React components
- `src/ui/pages/`: Page components
- `src/ui/api/`: API client code
- `src/ui/utils/`: Utility functions

## Setting Up Development Environment

1. **Backend Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Frontend Setup**
   ```bash
   cd src/ui
   npm install
   ```

3. **Development Tools**
   - VSCode with Python and TypeScript extensions
   - Python debugger
   - React Developer Tools
   - Git client

## Making Changes

1. **Backend Changes**
   - Update API documentation
   - Add migration scripts if needed
   - Update tests
   - Follow error handling patterns

2. **Frontend Changes**
   - Follow component structure
   - Use TypeScript strictly
   - Add prop types
   - Follow React best practices

## Review Process

1. **Before Submitting**
   - Run all tests
   - Update documentation
   - Format code
   - Check for security issues

2. **Code Review**
   - Address review comments
   - Update PR as needed
   - Keep PR focused and small

## Release Process

1. **Version Numbers**
   - Follow semantic versioning
   - Update CHANGELOG.md
   - Tag releases

2. **Deployment**
   - Test in staging
   - Follow deployment guide
   - Monitor for issues

## Questions?

- Create an issue for discussion
- Join our development channel
- Check existing documentation
