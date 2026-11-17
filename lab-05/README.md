# Lab 05: Containerization

## Project

This lab continues Lab 04 and uses the same Wishlist API and UI repositories:

- API: https://github.com/sarccasm/wishlist-api
- UI: https://github.com/sarccasm/wishlist-ui
- API implementation PR: https://github.com/sarccasm/wishlist-api/pull/3
- UI implementation PR: https://github.com/sarccasm/wishlist-ui/pull/2
- Successful CI/Compose smoke run: https://github.com/sarccasm/wishlist-api/actions/runs/44073819520
- API GHCR package (public): https://github.com/users/sarccasm/packages/container/wishlist-api
- UI GHCR package (public): https://github.com/users/sarccasm/packages/container/wishlist-ui
- API release: https://github.com/sarccasm/wishlist-api/releases/tag/v1.0.0
- API anonymous pull and full CI verified: https://github.com/sarccasm/wishlist-api/actions/runs/44074110848
- UI release: https://github.com/sarccasm/wishlist-ui/releases/tag/v1.0.0
- Anonymous UI image pull verified in CI: https://github.com/sarccasm/wishlist-ui/actions/runs/44073968417

## My contribution

The implementation is merged into `main` in both team repositories:

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

## Published images and verification

Both GHCR packages are public, and both repositories publish versioned images on the `v*` tag workflow. The `v1.0.0` jobs for both API and UI passed anonymous pulls, without credentials. The API run also passed the full Compose smoke check.

```bash
docker pull ghcr.io/sarccasm/wishlist-api:1.0.0
docker pull ghcr.io/sarccasm/wishlist-ui:1.0.0
```

## Remaining submission evidence

The full stack, API login/list creation, UI route fallback, PostgreSQL volume persistence, and anonymous UI pull passed in CI. The lab's human teammate fault-injection exercise still needs a real second participant and their screenshot; the CI diagnostics and checklist are recorded in the API container documentation.
