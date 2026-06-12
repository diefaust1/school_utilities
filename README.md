# School Utilities

Initial Django setup for the Auto Grader project.

The development stack uses PostgreSQL. Its data is stored in a Docker volume so it remains available when the containers stop.

## Run with Docker

```console
docker compose up --build
```

Open <http://localhost:8000>.

The same command works from PowerShell on Windows and from a terminal on Linux. Run it from the repository root so Compose can find `compose.yaml`. The source directory is mounted using a relative path, and PostgreSQL data is stored in a Docker-managed volume.

Students and teachers can create an account from the registration link on the login page. Administrative superusers can be created with:

```console
docker compose exec web python manage.py createsuperuser
```

The superuser account receives the teacher role and can access <http://localhost:8000/admin/>.

Run the test suite with:

```console
docker compose exec web python manage.py test
```
