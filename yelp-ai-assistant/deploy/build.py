"""
PyBuilder-based Deployer — Yelp-Style AI Assistant
====================================================

Automates build, test, packaging, and deployment for three environments
(dev, staging, prod) using PyBuilder as the build backbone.

Environments
------------
  dev       — local Docker Compose, no replicas, mock LLM backend
  staging   — single-node Docker, Redis + real Elasticsearch, mock LLM
  prod      — Kubernetes (kubectl apply), multi-replica, full stack

Build phases exposed as PyBuilder tasks
----------------------------------------
  clean          — remove __pycache__, dist/, build artefacts
  install_deps   — pip install -r requirements.txt
  run_tests      — pytest with coverage
  lint           — (optional) ruff/flake8 check
  build_image    — docker build → tag as yelp-ai-assistant:<env>-<version>
  deploy         — apply env-specific manifests / compose file

Usage
-----
  # Full pipeline (clean → test → build → deploy) for dev
  python deploy/build.py --env dev

  # Only build the Docker image for staging
  python deploy/build.py --env staging --task build_image

  # Deploy a pre-built image to prod (skip tests)
  python deploy/build.py --env prod --task deploy --skip-tests

  # List available tasks
  python deploy/build.py --list-tasks

PyBuilder programmatic API
--------------------------
  from deploy.build import get_project, run_task
  project = get_project("staging")
  run_task(project, "run_tests")
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Make project root importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# PyBuilder core imports
# ---------------------------------------------------------------------------
from pybuilder.core import Project, task, init, use_plugin


# ===========================================================================
# Environment Configurations
# ===========================================================================

@dataclass
class EnvConfig:
    """Per-environment build and deploy configuration."""

    name: str
    image_tag: str
    replicas: int
    redis_url: str
    use_mock_llm: bool
    log_level: str
    extra_env: Dict[str, str] = field(default_factory=dict)
    compose_file: Optional[str] = None
    k8s_manifests: Optional[str] = None


_ENVIRONMENTS: Dict[str, EnvConfig] = {
    "dev": EnvConfig(
        name="dev",
        image_tag="yelp-ai-assistant:dev-latest",
        replicas=1,
        redis_url="redis://localhost:6379/0",
        use_mock_llm=True,
        log_level="debug",
        compose_file="deploy/docker-compose.dev.yml",
    ),
    "staging": EnvConfig(
        name="staging",
        image_tag="yelp-ai-assistant:staging-latest",
        replicas=2,
        redis_url="redis://redis-staging:6379/0",
        use_mock_llm=True,
        log_level="info",
        compose_file="deploy/docker-compose.staging.yml",
    ),
    "prod": EnvConfig(
        name="prod",
        image_tag="yelp-ai-assistant:prod-latest",
        replicas=5,
        redis_url="redis://redis-prod:6379/0",
        use_mock_llm=False,
        log_level="warning",
        k8s_manifests="deploy/k8s/",
        extra_env={
            "OPENAI_API_KEY": "${OPENAI_API_KEY}",
            "SENTRY_DSN":     "${SENTRY_DSN}",
        },
    ),
}


# ===========================================================================
# PyBuilder project factory
# ===========================================================================

def get_project(env: str = "dev") -> Project:
    """
    Build and return a configured PyBuilder Project for *env*.

    The project carries the environment config as a property so that all
    tasks can read it without global state.
    """
    if env not in _ENVIRONMENTS:
        raise ValueError(
            f"Unknown environment '{env}'. "
            f"Choose from: {', '.join(_ENVIRONMENTS)}"
        )

    cfg = _ENVIRONMENTS[env]
    project = Project(
        basedir=_PROJECT_ROOT,
        name="yelp-ai-assistant",
        version="1.0.0",
    )
    project.set_property("env",            cfg.name)
    project.set_property("image_tag",      cfg.image_tag)
    project.set_property("replicas",       cfg.replicas)
    project.set_property("redis_url",      cfg.redis_url)
    project.set_property("use_mock_llm",   cfg.use_mock_llm)
    project.set_property("log_level",      cfg.log_level)
    project.set_property("compose_file",   cfg.compose_file)
    project.set_property("k8s_manifests",  cfg.k8s_manifests)
    project.set_property("env_config",     cfg)

    # Source and test directories
    project.set_property("dir_source_main_python", "src")
    project.set_property("dir_source_unittest_python", "tests")
    project.set_property("coverage_threshold_warn", 70)
    project.set_property("coverage_threshold_break", 60)

    return project


# ===========================================================================
# Task registry
# ===========================================================================

TaskFn = Callable[[Project], None]
_TASKS: Dict[str, tuple[str, TaskFn]] = {}


def _task(name: str, description: str):
    """Decorator that registers a function as a named deploy task."""
    def decorator(fn: TaskFn) -> TaskFn:
        _TASKS[name] = (description, fn)
        return fn
    return decorator


def _run(cmd: str, dry_run: bool = False) -> int:
    """Run a shell command, print it, and return the exit code."""
    print(f"  $ {cmd}")
    if dry_run:
        print("    [dry-run: skipped]")
        return 0
    result = subprocess.run(shlex.split(cmd), cwd=_PROJECT_ROOT)
    return result.returncode


# ===========================================================================
# Task implementations
# ===========================================================================

@_task("clean", "Remove __pycache__, *.pyc, dist/, and build artefacts")
def task_clean(project: Project) -> None:
    import shutil, glob as _glob

    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        ".pytest_cache",
        "dist",
        "build",
        "*.egg-info",
        ".coverage",
        "htmlcov",
    ]
    for pattern in patterns:
        for path in _glob.glob(
            os.path.join(_PROJECT_ROOT, pattern), recursive=True
        ):
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            elif os.path.isfile(path):
                os.remove(path)
    print("  ✔  Clean complete")


@_task("install_deps", "pip install -r requirements.txt")
def task_install_deps(project: Project) -> None:
    rc = _run(f"{sys.executable} -m pip install -r requirements.txt -q")
    if rc != 0:
        raise RuntimeError("Dependency installation failed")
    print("  ✔  Dependencies installed")


@_task("run_tests", "Run pytest with coverage report")
def task_run_tests(project: Project) -> None:
    rc = _run(
        f"{sys.executable} -m pytest tests/test_yelp_assistant.py "
        "--tb=short -q "
        "--cov=src --cov-report=term-missing "
        "--cov-fail-under=60"
    )
    if rc != 0:
        raise RuntimeError("Tests failed — aborting build")
    print("  ✔  Tests passed")


@_task("build_image", "Build a Docker image tagged for the target environment")
def task_build_image(project: Project) -> None:
    tag = project.get_property("image_tag")
    env = project.get_property("env")
    dockerfile = os.path.join(_PROJECT_ROOT, "deploy", "Dockerfile")

    if not os.path.exists(dockerfile):
        _generate_dockerfile(project)

    rc = _run(f"docker build -t {tag} -f {dockerfile} {_PROJECT_ROOT}")
    if rc != 0:
        raise RuntimeError(f"Docker build failed for tag '{tag}'")
    print(f"  ✔  Image built: {tag}")


@_task("deploy", "Deploy to the target environment")
def task_deploy(project: Project) -> None:
    env = project.get_property("env")
    cfg: EnvConfig = project.get_property("env_config")

    print(f"  Deploying to environment: {env}")

    if env in ("dev", "staging") and cfg.compose_file:
        compose_path = os.path.join(_PROJECT_ROOT, cfg.compose_file)
        if os.path.exists(compose_path):
            rc = _run(f"docker compose -f {compose_path} up -d")
        else:
            _generate_compose_file(project)
            print(f"  ✔  Generated compose file: {cfg.compose_file}")
            rc = 0
    elif env == "prod" and cfg.k8s_manifests:
        manifests_dir = os.path.join(_PROJECT_ROOT, cfg.k8s_manifests)
        if os.path.exists(manifests_dir):
            rc = _run(f"kubectl apply -f {manifests_dir}")
        else:
            _generate_k8s_manifests(project)
            print(f"  ✔  Generated k8s manifests in: {cfg.k8s_manifests}")
            rc = 0
    else:
        print(f"  ⚠  No deploy target configured for env '{env}'")
        rc = 0

    if rc != 0:
        raise RuntimeError(f"Deploy to '{env}' failed")
    print(f"  ✔  Deployed to {env}")


@_task("publish", "Tag and push the Docker image to a container registry")
def task_publish(project: Project) -> None:
    tag = project.get_property("image_tag")
    registry = os.environ.get("DOCKER_REGISTRY", "")
    if not registry:
        print("  ⚠  DOCKER_REGISTRY not set — skipping push")
        return
    remote_tag = f"{registry}/{tag}"
    _run(f"docker tag {tag} {remote_tag}")
    rc = _run(f"docker push {remote_tag}")
    if rc != 0:
        raise RuntimeError(f"Docker push failed for '{remote_tag}'")
    print(f"  ✔  Pushed: {remote_tag}")


# ===========================================================================
# Manifest / artefact generators
# ===========================================================================

def _generate_dockerfile(project: Project) -> None:
    """Write a production-ready Dockerfile to deploy/Dockerfile."""
    dockerfile_path = os.path.join(_PROJECT_ROOT, "deploy", "Dockerfile")
    os.makedirs(os.path.dirname(dockerfile_path), exist_ok=True)
    content = """\
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
        graphviz \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", \\
     "--workers", "4", "--log-level", "info"]
"""
    with open(dockerfile_path, "w") as f:
        f.write(content)
    print(f"  ✔  Generated {dockerfile_path}")


def _generate_compose_file(project: Project) -> None:
    """Write a docker-compose file for dev/staging to deploy/."""
    env = project.get_property("env")
    cfg: EnvConfig = project.get_property("env_config")
    compose_path = os.path.join(_PROJECT_ROOT, cfg.compose_file)
    os.makedirs(os.path.dirname(compose_path), exist_ok=True)
    content = f"""\
version: "3.9"
services:
  api:
    image: {cfg.image_tag}
    build:
      context: .
      dockerfile: deploy/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL={cfg.redis_url}
      - USE_MOCK_LLM={str(cfg.use_mock_llm).lower()}
      - LOG_LEVEL={cfg.log_level}
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: {cfg.replicas}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
"""
    with open(compose_path, "w") as f:
        f.write(content)
    print(f"  ✔  Generated {compose_path}")


def _generate_k8s_manifests(project: Project) -> None:
    """Write minimal Kubernetes manifests for prod to deploy/k8s/."""
    cfg: EnvConfig = project.get_property("env_config")
    k8s_dir = os.path.join(_PROJECT_ROOT, cfg.k8s_manifests)
    os.makedirs(k8s_dir, exist_ok=True)

    # Deployment
    deployment = f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yelp-ai-assistant
  labels:
    app: yelp-ai-assistant
spec:
  replicas: {cfg.replicas}
  selector:
    matchLabels:
      app: yelp-ai-assistant
  template:
    metadata:
      labels:
        app: yelp-ai-assistant
    spec:
      containers:
        - name: api
          image: {cfg.image_tag}
          ports:
            - containerPort: 8000
          env:
            - name: REDIS_URL
              value: "{cfg.redis_url}"
            - name: LOG_LEVEL
              value: "{cfg.log_level}"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 20
            periodSeconds: 30
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
"""
    service = """\
apiVersion: v1
kind: Service
metadata:
  name: yelp-ai-assistant
spec:
  selector:
    app: yelp-ai-assistant
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
"""
    hpa = f"""\
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: yelp-ai-assistant-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: yelp-ai-assistant
  minReplicas: {cfg.replicas}
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
"""
    for fname, content in [
        ("deployment.yaml", deployment),
        ("service.yaml", service),
        ("hpa.yaml", hpa),
    ]:
        path = os.path.join(k8s_dir, fname)
        with open(path, "w") as f:
            f.write(content)
    print(f"  ✔  Generated k8s manifests in {k8s_dir}")


# ===========================================================================
# Public API for programmatic use
# ===========================================================================

def run_task(project: Project, task_name: str) -> None:
    """Execute a named task against *project*."""
    if task_name not in _TASKS:
        raise ValueError(
            f"Unknown task '{task_name}'. "
            f"Available: {', '.join(_TASKS)}"
        )
    desc, fn = _TASKS[task_name]
    print(f"\n  ── {task_name}: {desc} ──")
    t0 = time.monotonic()
    fn(project)
    elapsed = time.monotonic() - t0
    print(f"     ({elapsed:.1f} s)")


def run_pipeline(
    env: str,
    tasks: Optional[List[str]] = None,
    skip_tests: bool = False,
) -> None:
    """
    Run the full build pipeline (or a subset) for *env*.

    Default pipeline: clean → install_deps → run_tests → build_image → deploy
    """
    default_pipeline = ["clean", "install_deps", "run_tests", "build_image", "deploy"]
    pipeline = tasks or default_pipeline
    if skip_tests and "run_tests" in pipeline:
        pipeline = [t for t in pipeline if t != "run_tests"]

    project = get_project(env)
    print(
        f"\n  ══════════════════════════════════════════════\n"
        f"  Yelp-Style AI Assistant — PyBuilder Deploy\n"
        f"  Environment : {env}\n"
        f"  Image tag   : {project.get_property('image_tag')}\n"
        f"  Tasks       : {' → '.join(pipeline)}\n"
        f"  ══════════════════════════════════════════════"
    )
    for task_name in pipeline:
        run_task(project, task_name)

    print(
        f"\n  ✅  Pipeline complete for environment '{env}'\n"
    )


# ===========================================================================
# CLI entry point
# ===========================================================================

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="PyBuilder-based deployer for the Yelp-Style AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {name:<18} {desc}"
            for name, (desc, _) in _TASKS.items()
        ),
    )
    parser.add_argument(
        "--env", "-e",
        choices=list(_ENVIRONMENTS),
        default="dev",
        help="Target environment (default: dev)",
    )
    parser.add_argument(
        "--task", "-t",
        action="append",
        dest="tasks",
        metavar="TASK",
        help="Run only the specified task(s) (repeatable; default: full pipeline)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the run_tests task",
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List available tasks and exit",
    )
    args = parser.parse_args()

    if args.list_tasks:
        print("\n  Available tasks:\n")
        for name, (desc, _) in _TASKS.items():
            print(f"    {name:<20} {desc}")
        print()
        return

    run_pipeline(
        env=args.env,
        tasks=args.tasks,
        skip_tests=args.skip_tests,
    )


if __name__ == "__main__":
    _cli()
