"""Manifest bookkeeping for committed public demo (T2) data artifacts.

PURPOSE
-------
Maintains `project_nurture/public/demo/data-manifest.json`, a small ledger
that records, for every T2 artifact under `project_nurture/public/demo/`,
its sha256 digest and the generator (script + args) that produced it. This
is the sole responsibility of this module; it does not read or write any
restricted data under `dhs_data/`, `project_nurture/public/generated/`, or
`python_backend/outputs/`.

DATA TIER
---------
T2 -- this module only ever describes committed, public demo artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "project_nurture" / "public" / "demo"
MANIFEST_PATH = DEMO_DIR / "data-manifest.json"


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_version_of(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return "unknown"
    if isinstance(payload, dict) and "schema_version" in payload:
        return str(payload["schema_version"])
    metadata = payload.get("metadata") if isinstance(payload, dict) else None
    if isinstance(metadata, dict) and "schema_version" in metadata:
        return metadata["schema_version"]
    return "unknown"


def _built_at() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.fromtimestamp(int(epoch), timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def update_manifest(artifact_path: Path, generator: str, args: object) -> None:
    """Update-or-insert the manifest entry for `artifact_path`.

    `artifact_path` must live under `project_nurture/public/demo/`.
    """
    artifact_path = Path(artifact_path).resolve()
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    relative = artifact_path.relative_to(DEMO_DIR)
    file_key = relative.as_posix()

    entry = {
        "file": file_key,
        "sha256": _sha256_of_file(artifact_path),
        "generator": generator,
        "generator_args": args,
        "schema_version": _schema_version_of(artifact_path),
        "built_at": _built_at(),
    }

    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    else:
        manifest = {"artifacts": []}

    artifacts = [a for a in manifest.get("artifacts", []) if a.get("file") != file_key]
    artifacts.append(entry)
    artifacts.sort(key=lambda a: a["file"])
    manifest["artifacts"] = artifacts

    MANIFEST_PATH.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
