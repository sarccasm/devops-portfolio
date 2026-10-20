
# Lab 04: Continuous Integration

## Project Overview

This laboratory focuses on configuring Continuous Integration (CI) for a full-stack Wishlist application using GitHub Actions.

The application consists of two repositories:

- **wishlist-api:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis.
- **wishlist-ui:** Vue 3, Vite, TypeScript, Tailwind CSS.

## Team Repositories

- API: https://github.com/sarccasm/wishlist-api
- UI: https://github.com/sarccasm/wishlist-ui

## My Contribution

I completed the following tasks:

- Configured GitHub Actions CI for the backend.
- Configured GitHub Actions CI for the frontend.
- Added API tests using Pytest.
- Configured Ruff linting for Python.
- Configured PostgreSQL and Redis services in the API CI pipeline.
- Fixed Ruff E722 and Python module import errors.
- Verified successful CI execution.
- Created branch protection rulesets for both repositories.
- Configured required status checks before merging.
- Created and merged pull requests.
- Added CI documentation in `wishlist-api/docs/checks.md`.

## Local Development Setup

### Prerequisites

- Git
- Python 3.11
- Node.js and npm
- PostgreSQL
- Redis

Docker Desktop is optional for local development, but it requires hardware virtualization.

### Clone Repositories

```bash
git clone https://github.com/sarccasm/wishlist-api.git
git clone https://github.com/sarccasm/wishlist-ui.git
```

### Backend Setup

Install Python dependencies:

```bash
cd wishlist-api
python -m pip install -r requirements.txt
```

Configure database connection variables in `.env`:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=wishlist
DB_SSLMODE=prefer
REDIS_URL=redis://localhost:6379
```

PostgreSQL and Redis must be running and accessible.

Start FastAPI:

```bash
python run.py
```

API documentation should be available at:

http://localhost:8000/docs

These instructions describe the expected setup. A successful local database-connected launch was not verified during this lab.

### Frontend Setup

Install dependencies:

```bash
cd wishlist-ui
npm ci
```

Start the development server:

```bash
npm run dev
```

The default Vite development address is usually:

http://localhost:5173

The frontend-to-backend integration was not verified locally.

### Verification

- [ ] PostgreSQL is running locally.
- [ ] Redis is running locally.
- [ ] FastAPI documentation is accessible locally.
- [ ] An API endpoint returns actual database data locally.
- [ ] The frontend successfully fetches data from the API locally.
- [x] PostgreSQL and Redis services initialized in GitHub Actions.
- [x] API CI tests passed.
- [x] UI CI checks passed.

**Local environment limitation:** Docker Desktop could not start because CPU virtualization was disabled. Instead, PostgreSQL and Redis services were used in GitHub Actions to run automated backend checks.


## API CI Cache Comparison

The GitHub Actions API CI workflow uses pip dependency caching through `actions/setup-python@v5`.

### Cache Performance

| Metric | Cache miss (Run #1) | Cache hit (Run #10) |
|---|---|---|
| Cache status | Cache not found | Cache restored successfully |
| Set up Python | 1 second | 5 seconds |
| Install dependencies | 9 seconds | 9 seconds |
| Total job duration | 39 seconds | 48 seconds |
| Result | Failed (Ruff) | Passed |

### Analysis

The first workflow run did not find an existing pip cache, while Run #10 successfully restored the dependency cache.

Both runs spent approximately 9 seconds installing dependencies. Therefore, no measurable improvement in dependency installation time was observed.

The total workflow duration increased from 39 to 48 seconds. However, these results are not directly comparable because Run #1 failed during Ruff linting and skipped the tests, while Run #10 completed successfully.

### Conclusion

Dependency caching was successfully configured and verified using GitHub Actions.

Although the cache was restored successfully, the measured installation time did not decrease. Additional successful workflow runs would be needed to evaluate the performance benefits more accurately.

### Evidence

- [Run #1: Cache miss](https://github.com/sarccasm/wishlist-api/actions/runs/39414264533)
- [Run #10: Cache hit](https://github.com/sarccasm/wishlist-api/actions/runs/39418851161)


### API CI

Repository: https://github.com/sarccasm/wishlist-api

Workflow: `.github/workflows/ci.yml`

The pipeline includes:

- Python environment setup
- Dependency installation
- Ruff linting
- Pytest execution
- PostgreSQL 15 service
- Redis 7 service
- Pip dependency caching

**Result:** Passed successfully.

During initial runs, the pipeline failed due to:

1. Ruff E722: bare `except` statement.
2. Pytest import error: `ModuleNotFoundError: No module named 'database'`.

Both problems were corrected, and the subsequent CI checks passed.

### UI CI

Repository: https://github.com/sarccasm/wishlist-ui

Workflow: `.github/workflows/ci.yml`

The frontend pipeline includes:

- ESLint checks
- TypeScript checking
- Production build

**Result:** Passed successfully.

## Branch Protection

Branch protection rulesets named `Protect main` were configured for both repositories.

Settings:

- Target branch: `main`
- Require a pull request before merging
- Require successful status checks
- Block force pushes

Required CI checks:

| Repository | Required check |
|---|---|
| wishlist-api | `lint-and-test` |
| wishlist-ui | `lint-and-build` |

## Pull Requests

### API

1. [PR #1 — Add API CI workflow and tests](https://github.com/sarccasm/wishlist-api/pull/1)
   - Added CI workflow and tests.
   - Fixed linting and import errors.
   - Successfully merged into `main`.

2. [PR #2 — Add CI documentation](https://github.com/sarccasm/wishlist-api/pull/2)
   - Added `docs/checks.md`.
   - CI checks passed.
   - Successfully merged into `main`.

### UI

1. [PR #1 — Add UI CI workflow](https://github.com/sarccasm/wishlist-ui/pull/1)
   - Added frontend CI workflow.
   - CI checks passed.
   - Successfully merged into `main`.

## CI Caching

The API pipeline uses pip dependency caching through `actions/setup-python`.

A measured comparison of execution times with and without caching has not yet been completed.

## Conclusion

GitHub Actions CI pipelines were configured for both Wishlist repositories.

The backend pipeline successfully runs automated checks with PostgreSQL and Redis services, while the frontend pipeline validates the application build.

Pull requests, automated tests, and branch protection rulesets provide a more reliable workflow for integrating code changes.

Local full-stack integration testing remains incomplete because Docker Desktop could not start on the development machine.

## UI CI Cache Comparison

The GitHub Actions UI CI workflow uses npm dependency caching through `actions/setup-node@v4`.

| Metric | Cache miss (Run #1) | Cache hit (Run #3) |
|---|---|---|
| Cache status | Cache not found | Cache restored successfully |
| Set up Node.js | 1 second | 2 seconds |
| Install dependencies | 6 seconds | 5 seconds |
| Total job duration | 19 seconds | 20 seconds |
| Result | Passed | Passed |

**Conclusion:** npm dependency caching was successfully configured and verified. Dependency installation improved slightly from 6 to 5 seconds. However, the total workflow duration increased from 19 to 20 seconds. This indicates that caching does not always significantly reduce execution time for small projects.

**Evidence:**

- [Run #1: Cache miss](https://github.com/sarccasm/wishlist-ui/actions/runs/39416029554)
- [Run #3: Cache hit](https://github.com/sarccasm/wishlist-ui/actions/runs/39416188966)
