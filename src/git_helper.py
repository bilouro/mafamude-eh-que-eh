"""
git_helper.py
Git operations for the mafamude repository.
"""
import subprocess
import os


def _run(cmd: list, cwd: str):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(cmd[1:])} falhou:\n{result.stderr.strip()}")
    return result.stdout.strip()


def pull(repo_path: str):
    """Pulls latest changes from remote."""
    _run(["git", "pull", "--rebase"], cwd=repo_path)


def commit_and_push(repo_path: str, message: str, files: list):
    """Stages specific files, commits and pushes."""
    # Stage only the specified files (use relative paths)
    for f in files:
        rel = os.path.relpath(f, repo_path)
        _run(["git", "add", rel], cwd=repo_path)

    # Check if there's anything to commit
    status = _run(["git", "status", "--porcelain"], cwd=repo_path)
    if not status:
        return  # nothing to commit

    _run(["git", "commit", "-m", message], cwd=repo_path)
    _run(["git", "push"], cwd=repo_path)
