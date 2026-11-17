# Lab 05: Containerization

## Project

This lab continues Lab 04 and uses the same Wishlist API and UI repositories:

- API: https://github.com/sarccasm/wishlist-api
- UI: https://github.com/sarccasm/wishlist-ui
- API implementation PR: https://github.com/sarccasm/wishlist-api/pull/3
- UI implementation PR: https://github.com/sarccasm/wishlist-ui/pull/2

## My contribution

The implementation is prepared on the `lab-05-containers` branches and is under review:

- Added a non-root, multi-stage API image and a Node-build/nginx-runtime UI image.
- Added Docker ignore rules so secrets, tests, local dependencies, and Git metadata stay out of the build contexts.
- Added a Compose stack for PostgreSQL, Redis, API, and UI, with health checks, startup ordering, named PostgreSQL storage, and only UI/API ports exposed.
- Extended each repository's existing CI workflow to build images after its existing checks and publish on `main` and version tags.
- Added API and stack diagnostics, setup instructions, release instructions, and measurement commands in [API container documentation](https://github.com/sarccasm/wishlist-api/blob/lab-05-containers/docs/containers.md).

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

## Measurements and remaining evidence

Image sizes and largest-layer notes are intentionally left for measurement on the machine used for the lab. Record them in [the container documentation](https://github.com/sarccasm/wishlist-api/blob/lab-05-containers/docs/containers.md) after building the builder and runtime stages. Capture a GHCR package page and the successful anonymous `docker pull` after the first release; set both GHCR packages to Public so the pull works without login.

The API/UI PRs are drafts until local Compose startup, route refresh, health checks, volume persistence, CI runs, and image measurements have been confirmed.
