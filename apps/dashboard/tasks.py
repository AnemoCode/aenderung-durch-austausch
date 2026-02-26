import logging
import math
import os
import re
import shutil
import subprocess
import tempfile
import glob as _glob
from urllib.parse import urlparse, urlunparse

from celery import shared_task
from django.utils import timezone

from .models import Project, ProjectSnapshot

logger = logging.getLogger(__name__)
_CANDIDATE_NAMES = ['main.tex', 'thesis.tex', 'paper.tex', 'article.tex', 'document.tex']
_CREDENTIALS_RE = re.compile(r'(https?://)([^:]+:[^@]+@)', re.IGNORECASE)


def _redact(text: str) -> str:
    """Strip credentials from any https://user:pass@host URLs in text."""
    return _CREDENTIALS_RE.sub(r'\1<redacted>@', text)


@shared_task(name='apps.dashboard.tasks.sync_all_projects')
def sync_all_projects():
    projects = (
        Project.objects
        .select_related('owner')
        .filter(owner__overleaf_token__isnull=False)
    )
    dispatched = 0
    for p in projects:
        if p.owner.overleaf_token:          # Python-level guard (post-decryption)
            sync_project.delay(p.pk)
            dispatched += 1
    logger.info('sync_all_projects: dispatched %d tasks', dispatched)


@shared_task(name='apps.dashboard.tasks.sync_project', max_retries=0)
def sync_project(project_id: int):
    try:
        project = Project.objects.select_related('owner').get(pk=project_id)
    except Project.DoesNotExist:
        return

    token = project.owner.overleaf_token
    if not token:
        return

    # Lazy import: the `git` package requires the system git binary,
    # which is only installed in the worker image — not in the web image.
    # Importing here (inside the task function) means the web process can
    # safely import this module without triggering the git executable check.
    import git  # noqa: PLC0415

    clone_dir = None
    try:
        clone_dir = tempfile.mkdtemp(prefix='overlytics_')
        env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}

        git.Repo.clone_from(
            _build_auth_url(project.git_url, token),
            clone_dir, depth=1, env=env,
        )

        main_tex = _find_main_tex(clone_dir)
        if main_tex is None:
            _save_error(project, Project.Status.CLONE_ERROR)
            return

        tc             = _run_texcount(main_tex)
        word_count     = tc['words']
        page_count     = math.ceil(word_count / 300)
        float_count    = tc['floats']
        math_count     = tc['math']
        citation_count = _count_citations(clone_dir)

        ProjectSnapshot.objects.create(
            project=project,
            word_count=word_count, page_count=page_count,
            float_count=float_count, math_count=math_count,
            citation_count=citation_count,
        )
        project.word_count     = word_count
        project.page_count     = page_count
        project.float_count    = float_count
        project.math_count     = math_count
        project.citation_count = citation_count
        project.status         = Project.Status.OK
        project.last_synced_at = timezone.now()
        project.save(update_fields=[
            'word_count', 'page_count', 'float_count', 'math_count',
            'citation_count', 'status', 'last_synced_at',
        ])

        logger.info(
            'sync_project %d: %d words, %d pages, %d floats, %d math, %d citations',
            project_id, word_count, page_count, float_count, math_count, citation_count,
        )

    except git.exc.GitCommandError as exc:
        err = str(exc).lower()
        status = (Project.Status.AUTH_ERROR
                  if '401' in err or '403' in err or 'authentication failed' in err
                  else Project.Status.CLONE_ERROR)
        logger.warning('sync_project %d git error: %s', project_id, _redact(str(exc)))
        _save_error(project, status)
    except Exception as exc:
        logger.exception('sync_project %d unexpected: %s', project_id, exc)
        _save_error(project, Project.Status.CLONE_ERROR)
    finally:
        if clone_dir and os.path.exists(clone_dir):
            shutil.rmtree(clone_dir, ignore_errors=True)


def _build_auth_url(git_url: str, token: str) -> str:
    """https://git.overleaf.com/<id>  →  https://git:<token>@git.overleaf.com/<id>"""
    p = urlparse(git_url)
    return urlunparse(p._replace(netloc=f'git:{token}@{p.hostname}'))


def _find_main_tex(clone_dir: str) -> str | None:
    # 1. Candidate names in root first (fast path)
    for name in _CANDIDATE_NAMES:
        c = os.path.join(clone_dir, name)
        if os.path.isfile(c):
            return c
    # 2. Candidate names anywhere in the tree (depth-first by path length)
    all_tex = sorted(
        _glob.glob(os.path.join(clone_dir, '**', '*.tex'), recursive=True),
        key=lambda p: p.count(os.sep),
    )
    for name in _CANDIDATE_NAMES:
        for tex in all_tex:
            if os.path.basename(tex) == name:
                return tex
    # 3. Any .tex file with \documentclass, shallowest first
    for tex in all_tex:
        try:
            with open(tex, errors='ignore') as fh:
                if any(re.search(r'\\documentclass', ln) for ln in fh):
                    return tex
        except OSError:
            continue
    return None


def _run_texcount(main_tex_path: str) -> dict:
    """Run texcount once, return words, floats, and math counts."""
    result = {'words': 0, 'floats': 0, 'math': 0}
    try:
        r = subprocess.run(
            ['texcount', '-total', '-inc', os.path.basename(main_tex_path)],
            capture_output=True, text=True, timeout=60,
            cwd=os.path.dirname(main_tex_path),
        )
        if r.returncode != 0:
            logger.warning('texcount exited %d: %s', r.returncode, r.stderr.strip())
        for line in r.stdout.splitlines():
            if line.startswith('Words in text:'):
                result['words'] = int(line.split(':')[1].strip())
            elif line.startswith('Number of floats/tables/figures:'):
                result['floats'] = int(line.split(':')[1].strip())
            elif line.startswith('Number of math inlines:'):
                result['math'] += int(line.split(':')[1].strip())
            elif line.startswith('Number of math displayed:'):
                result['math'] += int(line.split(':')[1].strip())
    except Exception as exc:
        logger.warning('texcount failed: %s', exc)
    return result


_CITE_RE = re.compile(r'\\cite\w*\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}')


def _count_citations(clone_dir: str) -> int:
    """Count unique bibliography keys cited across all .tex files."""
    keys: set[str] = set()
    for tex in _glob.glob(os.path.join(clone_dir, '**', '*.tex'), recursive=True):
        try:
            with open(tex, errors='ignore') as fh:
                for m in _CITE_RE.finditer(fh.read()):
                    keys.update(k.strip() for k in m.group(1).split(','))
        except OSError:
            continue
    return len(keys)


def _save_error(project: Project, status: Project.Status) -> None:
    project.status = status
    project.last_synced_at = timezone.now()
    project.save(update_fields=['status', 'last_synced_at'])
