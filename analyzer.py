from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _run_quick(cmd: List[str], timeout_s: float = 1.5) -> Tuple[int, str, str]:
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_s)
        return int(cp.returncode), (cp.stdout or "").strip(), (cp.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)


def _which(bin_name: str) -> Optional[str]:
    p = shutil.which(bin_name)
    return p


def detect_runtime_signals() -> Dict[str, Any]:
    signals: Dict[str, Any] = {}

    # python
    if _which("python3"):
        rc, out, err = _run_quick(["python3", "--version"])
        signals["python_version"] = out or err or None
    elif _which("python"):
        rc, out, err = _run_quick(["python", "--version"])
        signals["python_version"] = out or err or None
    else:
        signals["python_version"] = None

    # node
    if _which("node"):
        rc, out, err = _run_quick(["node", "--version"])
        signals["node_version"] = out or err or None
    else:
        signals["node_version"] = None

    # venv/conda
    signals["virtual_env"] = os.environ.get("VIRTUAL_ENV") or None
    signals["conda_env"] = os.environ.get("CONDA_PREFIX") or None

    # docker daemon
    if _which("docker"):
        rc, out, err = _run_quick(["docker", "info"], timeout_s=2.0)
        signals["docker_daemon"] = "running" if rc == 0 else "unavailable"
    else:
        signals["docker_daemon"] = "not_installed"

    return signals


def _is_git_repo(cwd: Path) -> bool:
    if not _which("git"):
        return False
    rc, out, err = _run_quick(["git", "rev-parse", "--is-inside-work-tree"], timeout_s=1.5)
    return rc == 0 and out.strip() == "true"


def detect_git_signals(cwd: Path) -> Dict[str, Any]:
    if not _is_git_repo(cwd):
        return {"git_repo": False}

    rc, branch, _ = _run_quick(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    detached = branch.strip() == "HEAD"
    rc2, status, _ = _run_quick(["git", "status", "--porcelain"], timeout_s=1.5)

    signals: Dict[str, Any] = {
        "git_repo": True,
        "git_branch": None if detached else branch.strip(),
        "git_detached_head": detached,
        "git_dirty": bool(status.strip()),
    }

    # in-progress operations
    git_dir_rc, git_dir, _ = _run_quick(["git", "rev-parse", "--git-dir"], timeout_s=1.5)
    if git_dir_rc == 0 and git_dir:
        gd = (cwd / git_dir).resolve()
        signals["git_rebase_in_progress"] = (gd / "rebase-apply").exists() or (gd / "rebase-merge").exists()
        signals["git_merge_in_progress"] = (gd / "MERGE_HEAD").exists()
    else:
        signals["git_rebase_in_progress"] = False
        signals["git_merge_in_progress"] = False

    return signals


def detect_project_signals(cwd: Path) -> Dict[str, Any]:
    signals: Dict[str, Any] = {}
    p = cwd

    # basic project files
    signals["has_requirements_txt"] = (p / "requirements.txt").exists()
    signals["has_pyproject_toml"] = (p / "pyproject.toml").exists()
    signals["has_package_json"] = (p / "package.json").exists()

    # language detection (simple)
    lang = []
    if signals["has_pyproject_toml"] or signals["has_requirements_txt"]:
        lang.append("python")
    if signals["has_package_json"]:
        lang.append("node")
    signals["languages"] = lang

    # common port usage snapshot (best-effort)
    signals["common_ports_in_use"] = detect_common_ports_in_use()

    # git
    signals.update(detect_git_signals(cwd))

    return signals


COMMON_PORTS = [3000, 5000, 8000, 8080, 5173]


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def detect_common_ports_in_use() -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    for port in COMMON_PORTS:
        try:
            result[str(port)] = _port_in_use(port)
        except Exception:
            result[str(port)] = False
    return result


_PORT_RE = re.compile(r"\b(?P<port>[1-9][0-9]{1,4})\b")


def extract_port_from_error(stderr: str) -> Optional[int]:
    # Common patterns
    if "Address already in use" not in stderr and "EADDRINUSE" not in stderr and "bind" not in stderr.lower():
        return None
    # Many runtimes include an errno like "[Errno 98]" which is *not* a port.
    # Prefer returning None over returning an errno.
    errno_nums = set()
    for em in re.finditer(r"\bErrno\s+(?P<n>\d+)\b", stderr):
        errno_nums.add(int(em.group("n")))
    for em in re.finditer(r"\[Errno\s+(?P<n>\d+)\]", stderr):
        errno_nums.add(int(em.group("n")))

    # Heuristic: pick first port-like number in stderr, excluding errno candidates
    for m in _PORT_RE.finditer(stderr):
        port = int(m.group("port"))
        if port in errno_nums:
            continue
        if 1 <= port <= 65535:
            return port
    return None
