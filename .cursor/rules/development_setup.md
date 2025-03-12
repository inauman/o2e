# Development Setup Guide

## Current Environment Status

### Project Setup
- Root folder `O2E` already created
- Python 3.14.0a5 already installed and pinned for the project
- Virtual environment already created
- UV package manager already installed via Homebrew
- Node.js and npm already installed for React frontend development

## Environment Setup for New Developers

### Python Installation
- Install Python 3.14.0a5 (for consistency with current development)
  - On macOS: `brew install python@3.14` or download from python.org
  - On Linux: Use pyenv or compile from source
  - On Windows: Download from python.org
- Ensure pip is updated to the latest version: `python -m pip install --upgrade pip`

### Node.js and npm Installation
- Install Node.js 18+ (required for React frontend)
  - On macOS: `brew install node@18`
  - On Linux: Use nvm or download from nodejs.org
  - On Windows: Download from nodejs.org
- Ensure npm is updated to the latest version: `npm install -g npm@latest`

### Package Management with UV
- Install UV: 
  - On macOS: `brew install uv` 
  - Other platforms: `pip install uv`
- Use UV for virtual environment creation: `uv venv`
- Use UV for package installation: `uv pip install <package>`
- Use UV for dependency resolution: `uv pip compile pyproject.toml -o requirements.txt`

### Project Configuration
- Use `pyproject.toml` for project configuration (PEP 621)
- Define project metadata, dependencies, and development tools in `pyproject.toml`
- Example `pyproject.toml` structure:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "o2e"
version = "0.1.0"
description = "Bitcoin Multisig POC with Hardware Wallet Integration"
readme = "README.md"
requires-python = ">=3.14"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "python-bitcoinlib>=0.11.0",
    "yubikey-manager>=4.0.0",
    "fido2>=1.0.0",
    "pyusb>=1.2.1",
    "btchip-python>=0.1.32",
    "cryptography>=39.0.0",
    "click>=8.1.3",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.10.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "mypy>=1.3.0",
    "ruff>=0.0.262",
    "bandit>=1.7.5",
    "pre-commit>=3.3.1",
    "pip-audit>=2.5.5",
]

[tool.black]
line-length = 88
target-version = ["py314"]

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.ruff]
line-length = 88
target-version = "py314"
select = ["E", "F", "B", "I", "N", "UP", "ANN", "S", "A"]
ignore = ["ANN101"]  # Missing type annotation for `self`

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--cov=src --cov-report=term-missing"
```

## Development Tools Setup

### Backend Code Quality Tools
- Install development dependencies: `uv pip install -e ".[dev]"`
- Set up pre-commit hooks:
  1. Create `.pre-commit-config.yaml`:
  ```yaml
  repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-toml
    - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.262
    hooks:
    - id: ruff
      args: [--fix]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    - id: mypy
      additional_dependencies: [types-requests]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
    - id: bandit
      args: ["-c", "pyproject.toml"]
      additional_dependencies: ["bandit[toml]"]
  ```
  2. Install pre-commit hooks: `pre-commit install`

### Frontend Setup with React and Tailwind CSS

#### React Application Setup
- Initialize a new React application with Vite or update an existing one:
  ```bash
  # For a new application
  npm create vite@latest frontend -- --template react-ts
  cd frontend
  npm install
  ```

#### Tailwind CSS Installation
- Install Tailwind CSS and its dependencies:
  ```bash
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```

- Configure Tailwind CSS by updating `tailwind.config.js`:
  ```js
  /** @type {import('tailwindcss').Config} */
  module.exports = {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            50: '#f0fdf4',
            100: '#dcfce7',
            // Add custom colors as needed
          },
          // Additional custom colors
        },
        fontFamily: {
          sans: ['Inter var', 'sans-serif'],
          // Add custom fonts as needed
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
    ],
  }
  ```

- Add Tailwind directives to your CSS in `src/index.css`:
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  
  @layer components {
    /* Add custom component classes here */
    .btn-primary {
      @apply bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
    }
  }
  ```

#### Additional Frontend Dependencies
- Install recommended packages for the React/Tailwind stack:
  ```bash
  # Routing
  npm install react-router-dom

  # API data fetching
  npm install @tanstack/react-query

  # Form handling
  npm install react-hook-form zod @hookform/resolvers

  # UI components
  npm install @headlessui/react @heroicons/react

  # Utility libraries
  npm install clsx date-fns

  # Testing
  npm install -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom

  # Tailwind plugins
  npm install -D @tailwindcss/forms @tailwindcss/typography
  ```

#### ESLint and Prettier Setup
- Install and configure ESLint and Prettier:
  ```bash
  npm install -D eslint eslint-plugin-react eslint-plugin-react-hooks @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-import eslint-plugin-jsx-a11y prettier eslint-config-prettier eslint-plugin-prettier
  ```

- Create `.eslintrc.js`:
  ```js
  module.exports = {
    env: {
      browser: true,
      es2021: true,
      node: true,
    },
    extends: [
      'eslint:recommended',
      'plugin:react/recommended',
      'plugin:react-hooks/recommended',
      'plugin:@typescript-eslint/recommended',
      'plugin:import/recommended',
      'plugin:import/typescript',
      'plugin:jsx-a11y/recommended',
      'prettier',
    ],
    parser: '@typescript-eslint/parser',
    parserOptions: {
      ecmaFeatures: {
        jsx: true,
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    plugins: ['react', '@typescript-eslint', 'prettier'],
    rules: {
      'prettier/prettier': 'error',
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  };
  ```

- Create `.prettierrc`:
  ```json
  {
    "semi": true,
    "tabWidth": 2,
    "printWidth": 100,
    "singleQuote": true,
    "trailingComma": "es5",
    "jsxSingleQuote": false,
    "bracketSpacing": true
  }
  ```

### Security Tools
- Run security checks regularly:
  - Dependency vulnerability scanning: 
    - Backend: `pip-audit`
    - Frontend: `npm audit`
  - Static security analysis: 
    - Backend: `bandit -r src/`
    - Frontend: `npm run lint`
  - Secret scanning: `detect-secrets scan`

### Testing Setup
- Backend tests:
  - Run tests with pytest: `pytest`
  - Generate coverage reports: `pytest --cov=src --cov-report=html`
  - Run specific test categories:
    - Unit tests: `pytest tests/unit/`
    - Integration tests: `pytest tests/integration/`
    - Security tests: `pytest tests/security/`

- Frontend tests:
  - Run tests with Vitest: `npm test`
  - Run tests in watch mode: `npm test -- --watch`
  - Generate coverage reports: `npm test -- --coverage`

## Project Structure Setup

```
O2E/  # Root folder (already created)
├── .cursor/                  # Cursor IDE configuration
│   └── rules/                # Development rules and guidelines
├── .github/                  # GitHub workflows and templates
│   └── workflows/            # CI/CD workflows
├── backend/                  # Flask backend
│   ├── app.py                # Main Flask application
│   ├── api/                  # API endpoints
│   ├── services/             # Business logic services
│   ├── models/               # Data models
│   ├── utils/                # Utility functions
│   ├── templates/            # Legacy Flask templates (if needed)
│   ├── static/               # Static assets
│   └── tests/                # Backend tests
├── frontend/                 # React frontend
│   ├── public/               # Static assets
│   ├── src/                  # React source code
│   │   ├── assets/           # Frontend assets (images, etc.)
│   │   ├── components/       # Reusable UI components
│   │   │   ├── atoms/        # Atomic UI components
│   │   │   ├── molecules/    # Composite components
│   │   │   └── organisms/    # Complex components
│   │   ├── context/          # React context providers
│   │   ├── features/         # Feature-based modules
│   │   ├── hooks/            # Custom React hooks
│   │   ├── layouts/          # Page layout components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service modules
│   │   ├── types/            # TypeScript types/interfaces
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main App component
│   │   └── main.tsx          # Entry point
│   ├── tests/                # Frontend tests
│   ├── .eslintrc.js          # ESLint configuration
│   ├── .prettierrc           # Prettier configuration
│   ├── index.html            # HTML template
│   ├── package.json          # Frontend dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── tsconfig.json         # TypeScript configuration
│   └── vite.config.ts        # Vite configuration
├── config/                   # Configuration files
│   ├── .env.example          # Example environment variables
│   └── config.json           # Application configuration
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── guides/               # User and developer guides
│   └── spec.md               # Project specification
├── data/                     # Data storage directory
├── scripts/                  # Helper scripts
│   └── dev.sh                # Development startup script
├── .gitignore                # Git ignore file
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── pyproject.toml            # Python project configuration
└── README.md                 # Project overview
```

## Development Workflow

### Initial Setup for New Developers
1. Clone the repository
2. Set up the backend:
   - Activate the existing virtual environment:
     - Unix/MacOS: `source venv/bin/activate`
     - Windows: `venv\Scripts\activate`
   - Install dependencies: `uv pip install -e ".[dev]"`
   - Install pre-commit hooks: `pre-commit install`

3. Set up the frontend:
   - Navigate to the frontend directory: `cd frontend`
   - Install dependencies: `npm install`

### Development Cycle
1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make changes
3. Run tests:
   - Backend: `pytest`
   - Frontend: `npm test`
4. Run linters and formatters:
   - Backend: `pre-commit run --all-files`
   - Frontend: `npm run lint && npm run format`
5. Start development servers:
   - Backend: `python backend/app.py`
   - Frontend: `cd frontend && npm run dev`
   - Or use the development script: `./scripts/dev.sh`
6. Commit changes: `git commit -m "feat: add feature"`
7. Push changes: `git push origin feature/feature-name`
8. Create a pull request

### Code Review Process
1. Automated checks must pass
2. At least one reviewer must approve
3. All comments must be addressed
4. Changes must be squashed before merging

## Updates
This document should be reviewed and updated when new tools or practices are adopted. 