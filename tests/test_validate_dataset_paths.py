import hashlib
import json
import struct
import subprocess
import sys
import unittest
import zlib
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import validate_dataset as validator

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_dataset.py"
SUPPLEMENTARY = {("humaneval_x", "javascript"): 164}
REFERENCE = "synthetic reference text\n"


def tiny_png():
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00")) + chunk(b"IEND", b""))


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def build_bundle(root, bundle, task_counts, write_assets):
    base = root / validator.BASES[bundle]
    records_dir = base / "records" / "nested records"
    records_dir.mkdir(parents=True)
    manifest = []
    dataset_counts = Counter()
    language_counts = Counter()
    png = tiny_png()
    for (dataset, language), count in task_counts.items():
        dataset_counts[dataset] += count
        language_counts[language] += count
        record_file = records_dir / f"{dataset}-{language}.jsonl"
        record_key = "/".join(record_file.relative_to(root).parts)
        records = []
        for index in range(count):
            assets = {}
            asset_dir = base / "assets" / "nested assets" / f"{dataset}-{language}" / str(index)
            if write_assets:
                asset_dir.mkdir(parents=True)
            for kind in sorted(validator.ASSETS):
                is_image = kind in {"flowchart", "uml", "pseudocode"}
                path = asset_dir / (f"{kind}.png" if is_image else f"{kind}.txt")
                data = png if is_image else REFERENCE.encode("utf-8")
                if write_assets:
                    path.write_bytes(data)
                assets[kind] = {"path": "/".join(path.relative_to(root).parts), "bytes": len(data),
                                "sha256": hashlib.sha256(data).hexdigest()}
            row = {"uid": f"{dataset}/{language}/{index}", "task_id": f"{language}/{index}",
                   "bundle": bundle, "dataset": dataset, "language": language, "assets": assets,
                   "license": validator.LICENSES[dataset], "split": "unspecified"}
            records.append(dict(row, source_record={"task_id": row["task_id"]}, reference_code=REFERENCE))
            manifest.append(dict(row, record_file=record_key, record_line=index + 1))
        write_jsonl(record_file, records)
    write_jsonl(base / "manifest.jsonl", manifest)
    summary = {"schema_version": "1.0", "bundle": bundle, "tasks": len(manifest),
               "images": len(manifest) * 3, "assets": len(manifest) * 6, "counts": dict(dataset_counts),
               "language_counts": dict(language_counts), "split": "unspecified"}
    (base / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return base


class SupplementaryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.root = Path(tmp.name) / "bundle root"
        cls.base = build_bundle(cls.root, "supplementary", SUPPLEMENTARY, write_assets=True)
        cls.manifest = cls.base / "manifest.jsonl"
        cls.first = validator.read_jsonl(cls.manifest)[0]
        cls.record_file = cls.root / cls.first["record_file"]

    def expected(self, metadata_only):
        return {"bundle": "supplementary", "tasks": 164, "images": 492, "assets": 984,
                "sha256_checked": not metadata_only, "ok": True}

    def run_cli(self, metadata_only=False):
        command = [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), "--bundle", "supplementary"]
        if metadata_only:
            command.append("--metadata-only")
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def assert_cli_success(self, metadata_only):
        result = self.run_cli(metadata_only)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), [self.expected(metadata_only)])

    def edit_rows(self, path, edit):
        self.addCleanup(path.write_bytes, path.read_bytes())
        rows = validator.read_jsonl(path)
        edit(rows)
        write_jsonl(path, rows)

    def first_asset(self, kind):
        return self.root / self.first["assets"][kind]["path"]

    def change_asset_metadata(self, kind, **changes):
        for path in (self.manifest, self.record_file):
            self.edit_rows(path, lambda rows: rows[0]["assets"][kind].update(changes))

    def test_metadata_only_accepts_manifest_paths(self):
        self.assertIn("/nested records/", self.first["record_file"])
        self.assertEqual(validator.validate(self.root, "supplementary", True), self.expected(True))

    def test_full_validation_accepts_manifest_paths(self):
        self.assertIn("/nested assets/", self.first["assets"]["flowchart"]["path"])
        self.assertEqual(validator.validate(self.root, "supplementary"), self.expected(False))

    def test_metadata_only_cli(self):
        self.assert_cli_success(metadata_only=True)

    def test_full_validation_cli(self):
        self.assert_cli_success(metadata_only=False)

    def test_extra_record_is_rejected(self):
        extra = self.record_file.with_name("extra.jsonl")
        extra.write_text("{}\n", encoding="utf-8")
        self.addCleanup(extra.unlink)
        with self.assertRaisesRegex(ValueError, "^Unreferenced record files$"):
            validator.validate(self.root, "supplementary", True)

    def test_extra_asset_is_rejected_by_cli(self):
        extra = self.first_asset("code").with_name("extra.txt")
        extra.write_bytes(b"unreferenced asset")
        self.addCleanup(extra.unlink)
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.strip(), "Validation failed: Unreferenced asset files")

    def test_missing_record_is_rejected(self):
        self.addCleanup(self.record_file.write_bytes, self.record_file.read_bytes())
        self.record_file.unlink()
        with self.assertRaises(FileNotFoundError):
            validator.validate(self.root, "supplementary", True)

    def test_missing_asset_is_rejected(self):
        path = self.first_asset("code")
        self.addCleanup(path.write_bytes, path.read_bytes())
        path.unlink()
        with self.assertRaisesRegex(ValueError, "^Missing .*code.txt"):
            validator.validate(self.root, "supplementary")

    def test_same_size_asset_change_is_rejected(self):
        path = self.first_asset("code")
        existing = path.read_bytes()
        self.addCleanup(path.write_bytes, existing)
        path.write_bytes(b"X" + existing[1:])
        with self.assertRaisesRegex(ValueError, "^File checksum mismatch:"):
            validator.validate(self.root, "supplementary")

    def test_incorrect_asset_size_is_rejected(self):
        self.change_asset_metadata("code", bytes=len(REFERENCE) + 1)
        with self.assertRaisesRegex(ValueError, "^File checksum mismatch:"):
            validator.validate(self.root, "supplementary")

    def test_invalid_sha256_is_rejected(self):
        self.change_asset_metadata("code", sha256="invalid")
        with self.assertRaisesRegex(ValueError, "^Invalid SHA-256:"):
            validator.validate(self.root, "supplementary", True)

    def test_invalid_png_header_is_rejected_even_with_matching_hash(self):
        path = self.first_asset("flowchart")
        self.addCleanup(path.write_bytes, path.read_bytes())
        data = b"synthetic non-PNG content"
        path.write_bytes(data)
        self.change_asset_metadata("flowchart", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        with self.assertRaisesRegex(ValueError, "^Invalid PNG:"):
            validator.validate(self.root, "supplementary")

    def test_reference_code_mismatch_is_rejected(self):
        self.edit_rows(self.record_file, lambda rows: rows[0].update(reference_code="different text"))
        with self.assertRaisesRegex(ValueError, "^Reference code mismatch:"):
            validator.validate(self.root, "supplementary")

    def test_absolute_and_outside_bundle_paths_are_rejected(self):
        base = validator.BASES["supplementary"] / "records"
        cases = [(str(self.record_file), "Invalid path:"), ("../outside.jsonl", "Invalid path:"),
                 ("data/records/tasks.jsonl", "Path outside bundle:")]
        for path, message in cases:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, message):
                validator.checked_path(self.root, path, base)

    def test_wrong_bundle_membership_is_rejected(self):
        self.edit_rows(self.manifest, lambda rows: rows[0].update(bundle="main"))
        with self.assertRaisesRegex(ValueError, "^Wrong bundle membership:"):
            validator.validate(self.root, "supplementary", True)

    def test_duplicate_record_reference_is_rejected(self):
        self.edit_rows(self.manifest, lambda rows: rows[1].update(record_line=rows[0]["record_line"]))
        with self.assertRaisesRegex(ValueError, "^Duplicate record reference:"):
            validator.validate(self.root, "supplementary", True)


class MainMetadataTests(unittest.TestCase):
    def test_main_bundle_manifest_paths(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_bundle(root, "main", validator.EXPECTED, write_assets=False)
            self.assertEqual(validator.validate(root, "main", True), {
                "bundle": "main", "tasks": 5622, "images": 16866, "assets": 33732,
                "sha256_checked": False, "ok": True,
            })
