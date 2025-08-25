Project Development Guidelines (advanced)

Scope
- This document captures project-specific practices for building, configuring, testing, and extending this Django/DRF service in Docker. It is intentionally concise and oriented to experienced developers.

- Do not try to run the projects locally. Only through `docker compose run --rm app sh -c COMMAND_EXAMPLE`.
- Keep answers concise and direct.
- Suggest alternative solutions.
- Avoid unnecessary explanations.
- Prioritize technical details over generic advice.
- When creating new models, use drf-spectacular when appropriate and do not forget to register the model in django admin.
- Never create README files or documentation if not asked to do it. Comments are allowed.
- Always offer the alternatives before making changes.
- Include the (recommended) approach in the list.
- Remember of creating log entries when appliable.
- When creating a file that will be runned via docker, check if the file is in WORKDIR directory.
- When in need of an example for tests purposing:
    - PL 4381/2023 is an existing proposition, with sf_id `8797561` and cd_id `2386490`.
- When trying to test somethin inside django prefer to use the following syntax without escaping the slashes and counterslashes:
```
docker compose run --rm app python manage.py shell -c string_containing_script
```
- if trying to test with python scripts check if the file is in WORKDIR folder (usually /app)

Build, configuration, and runtime
- Container orchestration: docker compose with two services: db (PostgreSQL 15) and app (Django). See compose.yaml.
- Build: the Dockerfile installs dependencies into a venv at /py and sets WORKDIR=/app. Build arg DEV controls installation of dev-only packages (default false; only flake8 in requirements.dev.txt).
  - Recommended: build once before running commands that rely on the image.
    - docker compose build
  - Alternative (when you need dev deps): set DEV=true at build-time and in compose args env if needed.
    - $env:DEV="true"; docker compose build
- Runtime env:
  - app mounts the host ./app into /app, so Python code edits are reflected live inside the container.
  - Default DB settings use Postgres (DB_HOST=db), but settings automatically switch to SQLite for test runs (see below).
  - Useful environment variables (compose): DEBUG, SECRET_KEY, DB_*, ALLOWED_HOSTS, STATIC_ROOT, MEDIA_ROOT, DJANGO_SUPERUSER_*. Settings read via python-decouple.

Database behavior in tests (important)
- app/config/settings.py switches to SQLite automatically for tests: if any of ["test", "pytest"] appears in sys.argv and USE_SQLITE_FOR_TESTS is true (default). This makes test runs independent of Postgres.
- To force Postgres during tests (not recommended for speed), export USE_SQLITE_FOR_TESTS=false.

Testing: how to run, add, and structure tests
- Framework: Django’s built-in test runner (unittest-style). No pytest by default (requirements.dev.txt has only flake8). Tests are under app/apps/<app_name>/tests/
- Running the full suite (recommended):
  - docker compose run --rm app sh -c "python manage.py test"
- Running a single test module/class/case:
  - docker compose run --rm app sh -c "python manage.py test apps.pauta.tests.test_tema_api"
  - docker compose run --rm app sh -c "python manage.py test apps.pauta.tests.test_proposicao_api.ProposicaoAPITestCase"
  - docker compose run --rm app sh -c "python manage.py test apps.pauta.tests.test_models.TemaModelTest.test_criar_tema_valido"
- Creating tests:
  - Prefer Django TestCase and DRF’s APIClient for API tests (see existing tests under app/apps/pauta/tests for patterns, including reverse() with namespaced URLs like pauta:proposicao-list).
  - Keep any test helper scripts that need to be executed in /app (WORKDIR) if you intend to run them via docker. Example one-off scripts can live at repo root if guarded by if __name__ == "__main__" to avoid interfering with discovery (see test_serializer.py).
- Example demo test (process used and verified)
  - File (temporary, now deleted): app/apps/pauta/tests/test_demo_example.py
  - Content:
    - from django.test import TestCase
    - class DemoExampleTest(TestCase):
        - def test_sanity_math(self):
            - self.assertEqual(2 + 2, 4)
  - Command executed and verified OK:
    - docker compose run --rm app sh -c "python manage.py test apps.pauta.tests.test_demo_example -v 2"
  - Note: The global run also succeeds: docker compose run --rm app sh -c "python manage.py test"
  - Per the issue requirement, the demo test file was removed after verification; only this guidelines file was added.

Data, fixtures, and domain specifics
- app/apps/pauta contains migrations that include data-loading steps (e.g., 0004_load_agenda_data_with_eixos). For reproducible test data, create deterministic objects within tests; don’t rely on external services.
- Example IDs for legislative propositions per .cursorrules:
  - Senado Federal: sf_id 8797561 for PL 4381/2023
  - Câmara dos Deputados: cd_id 2386490

Logging and observability
- Logging is configured in settings to write rotating log files under /app/logs (mounted from repo app/logs): debug.log, info.log, error.log, security.log, api.log (JSON formatter).
- When you implement features that interact with external services or critical flows, add explicit log entries using the per-app loggers (apps.pauta, apps.authentication, apps.core) in addition to DRF default logging.

API design and drf-spectacular integration
- drf-spectacular is configured (DEFAULT_SCHEMA_CLASS, SPECTACULAR_SETTINGS). When adding new models/endpoints:
  - Write serializers/views with proper typing and field metadata so schema generation is accurate.
  - Add extend_schema annotations where useful (request/response examples, tags, descriptions) to enhance docs.
  - Register models in Django admin as per .cursorrules.

Management commands and scripts
- Custom management commands present under apps/core/management/commands and apps/pauta/management/commands (e.g., wait_for_db, sync_proposicoes, sync_activity_history).
- Run via:
  - docker compose run --rm app sh -c "python manage.py <command> [args]"
- Interactive shell for quick checks (per .cursorrules):
  - docker compose run --rm app python manage.py shell -c "<python_one_liner>"
- If you need to run a standalone Python script, ensure it lives under /app and is compatible with DJANGO_SETTINGS_MODULE where needed.

Build/run commands cheatsheet
- Build images:
  - docker compose build
- Migrations (when using Postgres runtime):
  - docker compose up -d db
  - docker compose run --rm app sh -c "python manage.py migrate"
- Run full test suite (uses SQLite by default):
  - docker compose run --rm app sh -c "python manage.py test"
- Generate OpenAPI schema file (optional):
  - docker compose run --rm app sh -c "python manage.py spectacular --file schema.yaml"

Code style and conventions
- Python 3.12, Django 4.2, DRF. Keep imports absolute under apps.<app>.*
- Use settings via decouple config() and wire env vars through compose.
- Tests: name files test_*.py; use TestCase; use APIClient for API integration tests; prefer reverse() with named routes (see apps/pauta/urls.py). Keep tests deterministic and isolated; avoid network I/O.
- Keep scripts executable in Docker (line endings, +x); for shell scripts added in /scripts ensure dos2unix compatibility (Dockerfile already runs dos2unix /scripts/*.sh).

Alternatives and recommendations
- Test runner:
  - Recommended: Django manage.py test (fast, uses SQLite).
  - Alternative: Introduce pytest + pytest-django if you need richer fixtures/parametrization; would require adding packages to requirements.dev.txt and configuring pytest.ini.
- Database during tests:
  - Recommended: default SQLite (fast, isolated).
  - Alternative: USE_SQLITE_FOR_TESTS=false to test against Postgres when debugging DB-specific behavior.

Verification performed (timestamp 2025-08-15 16:40 local)
- Ran full suite: OK (30 tests, ~0.7s).
  - Command: docker compose run --rm app sh -c "python manage.py test"
- Created and ran a demo test module: OK (1 test). Then removed the file as required.
  - Command: docker compose run --rm app sh -c "python manage.py test apps.pauta.tests.test_demo_example -v 2"

Housekeeping
- Per the task requirements, no auxiliary files remain in the repository except this .junie/guidelines.md. If you add temporary artifacts for experimentation, delete them before committing.
