#!/usr/bin/env python3
"""Validate Flow2Code metadata and downloaded files using only Python's standard library.

Never imports or executes dataset programs or tests.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASES = {"main": Path("data"), "supplementary": Path("supplementary/humaneval_x_javascript")}
ASSETS = {"code", "flowchart", "uml", "pseudocode", "dot", "pseudocode_dot"}
LICENSES = {"classeval": "CC-BY-NC-4.0", "humaneval_x": "Apache-2.0",
            "mbxp": "CC-BY-4.0", "mceval": "CC-BY-SA-4.0"}
EXPECTED = {("classeval", "python"): 100}
EXPECTED.update({("humaneval_x", language): 164 for language in ("cpp", "java", "python")})
EXPECTED.update({("mbxp", language): 611 for language in
                 ("cpp", "csharp", "java", "javascript", "php", "python", "ruby")})
EXPECTED.update({("mceval", language): 53 if language == "java" else 50 for language in
                 ("c", "cpp", "csharp", "fortran", "html", "java", "javascript", "pascal",
                  "perl", "php", "python", "ruby", "shell", "tcl", "vb")})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_path(root, relative, base):
    require(isinstance(relative, str), "File path must be a string")
    p = Path(relative)
    require(not p.is_absolute() and ".." not in p.parts, f"Invalid path: {relative}")
    resolved = (root / p).resolve()
    require(resolved.is_relative_to((root / base).resolve()), f"Path outside bundle: {relative}")
    return resolved


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(root, bundle="main", metadata_only=False):
    root = Path(root).resolve()
    base = BASES[bundle]
    manifest_path = root / base / "manifest.jsonl"
    require(manifest_path.is_file(), f"Missing {base}/manifest.jsonl; extract the {bundle} data archive into {root}")
    manifest = read_jsonl(manifest_path)
    expected = EXPECTED if bundle == "main" else {("humaneval_x", "javascript"): 164}
    seen, paths, record_locations = set(), set(), set()
    counts, language_counts = Counter(), Counter()
    record_cache = {}
    for item in manifest:
        uid = item["uid"]
        dataset, language = item["dataset"], item["language"]
        require(uid not in seen, f"Duplicate task: {uid}")
        seen.add(uid)
        require((dataset, language) in expected and item["bundle"] == bundle, f"Wrong bundle membership: {uid}")
        number = re.search(r"(\d+)$", item["task_id"])
        require(number is not None and uid == f"{dataset}/{language}/{number.group(1)}", f"Task ID mismatch: {uid}")
        require(item["license"] == LICENSES[dataset], f"License mismatch: {uid}")
        require(item["split"] == "unspecified", f"Unexpected split: {uid}")
        counts[dataset, language] += 1
        language_counts[language] += 1
        record_file = item["record_file"]
        record_path = checked_path(root, record_file, base / "records")
        if record_file not in record_cache:
            record_cache[record_file] = read_jsonl(record_path)
        line = item["record_line"]
        require(type(line) is int and 1 <= line <= len(record_cache[record_file]), f"Invalid record line: {uid}")
        location = (record_file, line)
        require(location not in record_locations, f"Duplicate record reference: {uid}")
        record_locations.add(location)
        record = record_cache[record_file][line - 1]
        for field in ("uid", "dataset", "language", "task_id", "bundle", "license", "split", "assets"):
            require(record[field] == item[field], f"Record/manifest mismatch: {uid}/{field}")
        require(record["source_record"]["task_id"] == item["task_id"], f"Source task mismatch: {uid}")
        require(isinstance(record["reference_code"], str) and record["reference_code"].strip(), f"Empty reference code: {uid}")
        require(set(item["assets"]) == ASSETS, f"Incomplete assets: {uid}")
        for kind, asset in item["assets"].items():
            path = checked_path(root, asset["path"], base / "assets")
            require(asset["path"] not in paths, f"Shared asset path: {asset['path']}")
            paths.add(asset["path"])
            require(type(asset["bytes"]) is int and asset["bytes"] > 0, f"Invalid asset size: {uid}/{kind}")
            require(re.fullmatch(r"[0-9a-f]{64}", asset["sha256"]) is not None, f"Invalid SHA-256: {uid}/{kind}")
            if metadata_only:
                continue
            require(path.is_file(), f"Missing {asset['path']}; extract the {bundle} archive, or use --metadata-only before downloading")
            require(path.stat().st_size == asset["bytes"] and sha256(path) == asset["sha256"], f"File checksum mismatch: {asset['path']}")
            if kind in {"flowchart", "uml", "pseudocode"}:
                with path.open("rb") as stream:
                    require(stream.read(8) == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {asset['path']}")
            if kind == "code":
                require(path.read_text(encoding="utf-8").strip() == record["reference_code"].strip(), f"Reference code mismatch: {uid}")
    require(dict(counts) == expected, f"Unexpected subset counts: {dict(counts)}")
    require(sum(map(len, record_cache.values())) == len(manifest), "Unreferenced records")
    disk_records = {str(p.relative_to(root)) for p in (root / base / "records").rglob("*.jsonl")}
    require(disk_records == set(record_cache), "Unreferenced record files")
    if bundle == "supplementary":
        require(seen == {f"humaneval_x/javascript/{i}" for i in range(164)}, "Incomplete supplementary IDs")
    if not metadata_only:
        disk_assets = {str(p.relative_to(root)) for p in (root / base / "assets").rglob("*") if p.is_file()}
        require(paths == disk_assets, "Unreferenced asset files")
    summary = json.loads((root / base / "summary.json").read_text())
    dataset_counts = Counter()
    for (dataset, _), count in counts.items():
        dataset_counts[dataset] += count
    for key, value in {"schema_version": "1.0", "bundle": bundle, "tasks": len(seen),
                       "images": len(seen)*3, "assets": len(paths), "counts": dict(dataset_counts),
                       "language_counts": dict(language_counts), "split": "unspecified"}.items():
        require(summary[key] == value, f"Summary mismatch: {key}")
    return {"bundle": bundle, "tasks": len(seen), "images": len(seen)*3,
            "assets": len(paths), "sha256_checked": not metadata_only, "ok": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository or archive extraction root")
    parser.add_argument("--bundle", choices=["main", "supplementary", "all"], default="main")
    parser.add_argument("--metadata-only", action="store_true", help="Check records without downloaded assets")
    args = parser.parse_args()
    try:
        bundles = ["main", "supplementary"] if args.bundle == "all" else [args.bundle]
        results = [validate(args.root, bundle, args.metadata_only) for bundle in bundles]
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
