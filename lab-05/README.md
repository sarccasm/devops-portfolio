# Lab 05: Containerization

## Project

This lab continues Lab 04 and uses the same Wishlist API and UI repositories:

- API: https://github.com/sarccasm/wishlist-api
- UI: https://github.com/sarccasm/wishlist-ui
- API implementation PR: https://github.com/sarccasm/wishlist-api/pull/3
- UI implementation PR: https://github.com/sarccasm/wishlist-ui/pull/2
- Successful CI/Compose smoke run: https://github.com/sarccasm/wishlist-api/actions/runs/44070664186

## My contribution

The implementation is prepared on the `lab-05-containers` branches and is under review:

- Added a non-root, multi-stage API image and a Node-build/nginx-runtime UI image.
- Added Docker ignore rules so secrets, tests, local dependencies, and Git metadata stay out of the build contexts.
- Added a Compose stack for PostgreSQL, Redis, API, and UI, with health checks, startup ordering, named PostgreSQL storage, and only UI/API ports exposed.
- Extended each repository's existing CI workflow to build images after its existing checks and publish on `main` and version tags.
- Added a Compose smoke check that creates a wishlist through the API, restarts the stack, confirms database persistence, checks the UI route fallback, and records image sizes and layer history.
- Recorded setup, troubleshooting, the two configuration issues discovered during the smoke check, image measurements, and release instructions in [API container documentation](https://github.com/sarccasm/wishlist-api/blob/lab-05-containers/docs/containers.md).

## Run the stack

Clone both repositories next to one another, then run:

```bash
cd wishlist-api
cp .env.example .env
```

Fill in non-empty `DB_PASSWORD` and `SECRET_KEY` values in `.env`, then:

```bash
docker compose up --build -d
docker compose ps
```

Open the UI at http://localhost:8080 and the API docs at http://localhost:8000/docs. Stop the stack with `docker compose down`; the PostgreSQL named volume remains. Use `docker compose down -v` only when you want to delete its data.

## Image measurements

Measured by `docker image inspect` on the Ubuntu 24.04 GitHub runner:

| Image | Size |
| --- | ---: |
| API builder stage | 210.9 MiB |
| API final image | 194.2 MiB |
| UI build stage | 310.6 MiB |
| UI final image | 46.1 MiB |

The API dependency layer is 78.5 MB. The final UI image has only nginx and about 160 KB of compiled `dist/`; Node and `node_modules` stay in the build stage. The workflow run includes the raw size and layer-history artifact.

## Remaining submission evidence

The full stack, API login/list creation, UI route fallback, and PostgreSQL volume persistence passed in CI. Before final submission, capture the teammate fault-injection diagnosis required by the lab. After the first main/tag publication, set both GHCR packages to Public and capture the package pages plus an anonymous `docker pull`.
