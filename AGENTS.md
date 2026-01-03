# Development Guidelines

## Python Environment Setup

### Prerequisites

- Verify `.venv` directory exists (indicates `uv venv` has been run)
- Package manager: `uv`

### Environment Activation

```bash
source .venv/bin/activate
```

**Note:** Only needs to be run once per session

### Dependency Management

```bash
uv pip install -r /path/to/requirements.txt
```

### Testing

- Ensure virtual environment is activated
- Run tests using `pytest [OPTIONS|FLAGS]` directly
