# Lab 04: Continuous Integration

## Project Overview

This laboratory focuses on setting up continuous integration for a full-stack Wishlist application.

The application consists of two repositories:

- **wishlist-api:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis.
- **wishlist-ui:** Vue 3, Vite, TypeScript, ESLint, Tailwind CSS.

## Team Repositories

- API: [Add team fork URL]
- UI: [Add team fork URL]

## My Contribution

[Describe the CI configuration, tests, documentation, and pull requests personally completed.]

## Local Development Setup

### Prerequisites

- Git
- Docker Desktop
- Python
- Node.js and npm

### Clone Repositories

```bash
git clone <API_FORK_URL>
git clone <UI_FORK_URL>
```

### Backend Setup

[Add verified commands for PostgreSQL, Redis, Python dependencies, environment variables, database migrations, and starting FastAPI.]

### Frontend Setup

[Add verified commands for installing dependencies, configuring the API URL, and starting Vite.]

### Verification

- [ ] PostgreSQL is running.
- [ ] Redis is running.
- [ ] FastAPI documentation is accessible at `/docs`.
- [ ] An API endpoint returns actual database data.
- [ ] The frontend successfully fetches data from the API.

## CI Pipelines

### API

- Ruff linting
- Pytest
- PostgreSQL and Redis services
- Dependency caching

### UI

- ESLint
- TypeScript checking
- Production build
- Build artifact upload

## Branch Protection

Both repositories must require successful CI checks before merging pull requests into `main`.

## Pull Requests

[Add links to personal pull requests.]
