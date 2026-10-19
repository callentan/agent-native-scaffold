"""Task12 / ENH-13: explicit file ownership and isolated candidate regression."""

from __future__ import annotations

import hashlib
import io
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import stat
import sys
import tempfile
import threading
import unittest
from urllib.parse import unquote, urlsplit
from contextlib import redirect_stdout
from unittest.mock import patch

import distribute_candidate as candidate_copier
from tests.helpers import (
    WORKTREE, criterion_block, git, metadata, seed_git_repo, seed_implementation_fixture,
    source_bytes, write_delivery_fixture, write_metadata,
)


MANIFEST = WORKTREE / "docs" / "distribution-manifest.json"
COPY_TOOL = WORKTREE / ".github" / "utilities" / "distribute_candidate.py"
UTILITIES = ".github/utilities"
SCOPE = "sample/CTX-001"
DELIVERY = (
    "sample/CTX-001/REQ-001#req-001-ac-01",
    "sample/CTX-001/REQ-001#req-001-ac-02",
    "sample/CTX-001/SR-001#sr-001-ac-01",
    "sample/CTX-001/SR-001#sr-001-ac-02",
)
RUNTIME_MODULES = (
    "artifact_io", "check_artifacts", "check_traceability",
    "collect_implementation_report", "export_model", "extract_source",
    "hook_checks", "install_hooks", "log_interaction", "plan_template_update",
    "render_architecture", "render_presentation", "render_traceability",
    "score_candidates", "setup_domain_source", "source_baseline",
    "summarize_usage", "transcribe_audio", "vt_records",
)
REQUIRED_RESOURCES = (
    ".github/contracts/artifact.schema.json",
    ".github/contracts/bc-config.schema.json",
    ".github/contracts/implementation-report.schema.json",
    ".github/contracts/model-sources.schema.json",
    ".github/contracts/model.schema.json",
    ".github/utilities/requirements.txt",
    ".github/utilities/requirements.lock",
    ".github/utilities/requirements-media.txt",
    ".github/utilities/requirements-rendering.txt",
    ".github/hooks/README.md",
    ".github/hooks/commit-msg",
    ".github/hooks/pre-commit",
    ".github/workflows/validate-artifacts.yml",
    "_templates/reports/ai-interaction-log.csv",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _slug_heading(value: str, used: set[str]) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    slug = "".join(
        character.lower() if character.isalnum() or character in "-_" else
        "-" if character.isspace() else ""
        for character in value
    ).strip("-")
    candidate = slug
    suffix = 0
    while candidate in used:
        suffix += 1
        candidate = f"{slug}-{suffix}"
    used.add(candidate)
    return candidate


def _visible_markdown_lines(text: str):
    """A small independent link scanner; it never imports the candidate parser."""
    fence_char = None
    fence_size = 0
    in_comment = False
    for number, original in enumerate(text.splitlines(), 1):
        line = original
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            token = fence[1]
            if fence_char is None:
                fence_char, fence_size = token[0], len(token)
            elif token[0] == fence_char and len(token) >= fence_size:
                fence_char, fence_size = None, 0
            continue
        if fence_char is not None:
            continue
        output = []
        index = 0
        while index < len(line):
            if in_comment:
                end = line.find("-->", index)
                if end < 0:
                    index = len(line)
                    continue
                in_comment = False
                index = end + 3
                continue
            start = line.find("<!--", index)
            if start < 0:
                output.append(line[index:])
                break
            output.append(line[index:start])
            in_comment = True
            index = start + 4
        visible = "".join(output)
        visible = re.sub(r"(`+).*?\1", "", visible)
        yield number, visible


def _anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig")
    anchors = set(re.findall(r'<a\s+id=["\']([^"\']+)["\']\s*>\s*</a>', text, flags=re.I))
    used: set[str] = set()
    for _, line in _visible_markdown_lines(text):
        heading = re.match(r"^\s{0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", line)
        if heading:
            anchors.add(_slug_heading(heading[1], used))
    return anchors


def _local_markdown_links(root: Path):
    pattern = re.compile(
        r"(?<!!)\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)"
    )
    for markdown in sorted(root.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8-sig")
        definitions = []
        for number, line in _visible_markdown_lines(text):
            reference = re.match(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", line)
            if reference:
                destination = reference[1]
                definitions.append((number, destination[1:-1] if destination.startswith("<") else destination))
            for match in pattern.finditer(line):
                destination = match[1]
                definitions.append((number, destination[1:-1] if destination.startswith("<") else destination))
        for number, destination in definitions:
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            decoded_path = unquote(parsed.path)
            target = markdown if not decoded_path else markdown.parent.joinpath(*PurePosixPath(decoded_path).parts)
            try:
                resolved = target.resolve(strict=True)
                resolved.relative_to(root.resolve())
            except (OSError, ValueError):
                yield markdown.relative_to(root).as_posix(), number, destination, "missing or outside candidate"
                continue
            if resolved.is_dir():
                resolved = resolved / "README.md"
            if not resolved.is_file():
                yield markdown.relative_to(root).as_posix(), number, destination, "not a file"
                continue
            fragment = unquote(parsed.fragment)
            if fragment and fragment not in _anchors(resolved):
                yield markdown.relative_to(root).as_posix(), number, destination, f"missing anchor #{fragment}"


class DistributionTests(unittest.TestCase):
    def setUp(self):
        fixture_root = WORKTREE / ".venv" / "task12-fixtures"
        fixture_root.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="run-", dir=fixture_root)
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        report_temporary = tempfile.TemporaryDirectory(prefix="task12-reports-")
        self.addCleanup(report_temporary.cleanup)
        self.report_workspace = Path(report_temporary.name)

    def manifest(self):
        self.assertTrue(MANIFEST.is_file(), "DIST-01 requires the exact delivered-file manifest")
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def copy_candidate(self, name="candidate", *, target_root=None):
        self.assertTrue(COPY_TOOL.is_file(), "DIST-01 requires the maker-side local candidate copier")
        target_root = Path(target_root) if target_root is not None else self.workspace
        target = target_root / name
        receipt_path = self.report_workspace / f"{name}-receipt.json"
        command = [
            sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
            "--root", str(WORKTREE),
            "--target", str(target),
            "--allow-output-root", str(self.workspace),
            "--allow-output-root", str(target_root),
            "--allow-output-root", str(self.report_workspace),
            "--report", str(receipt_path),
        ]
        return target, receipt_path, subprocess.run(
            command, cwd=WORKTREE, shell=False, capture_output=True, text=True,
            encoding="utf-8", timeout=120,
        )

    def candidate_cli(self, candidate: Path, script: str, *arguments: str):
        path = candidate / UTILITIES / f"{script}.py"
        self.assertTrue(path.is_file(), f"DIST-06 expected copied runtime entry {path.relative_to(candidate)}")
        code = (
            "import runpy,sys; from pathlib import Path; "
            "candidate=Path(sys.argv[1]).resolve(); script=candidate/'.github/utilities'/sys.argv[2]; "
            "assert script.is_file() and script.resolve().is_relative_to(candidate); "
            "sys.path.insert(0,str(script.parent)); "
            "sys.argv=[str(script),*sys.argv[3:]]; runpy.run_path(str(script),run_name='__main__')"
        )
        environment = {
            key: value for key, value in os.environ.items()
            if key not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE"}
        }
        return subprocess.run(
            [sys.executable, "-I", "-B", "-X", "utf8", "-c", code,
             str(candidate), f"{script}.py", *map(str, arguments)],
            cwd=candidate, env=environment, shell=False, capture_output=True,
            text=True, encoding="utf-8", timeout=120,
        )

    def copied_candidate(self, name="candidate", *, target_root=None):
        target, receipt_path, run = self.copy_candidate(name, target_root=target_root)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        self.assertTrue(receipt_path.is_file(), run.stdout)
        return target, json.loads(receipt_path.read_text(encoding="utf-8"))

    def seed_copy_fixture(self, name="copy-source", payload=b"synthetic source bytes"):
        root = self.workspace / name
        root.mkdir()
        manifest = {
            "schemaVersion": 1,
            "components": {"fixture": "Synthetic local test input"},
            "files": [
                {"path": "assets/payload.txt", "component": "fixture"},
                {"path": "docs/distribution-manifest.json", "component": "fixture"},
            ],
            "excluded": [],
        }
        (root / "assets").mkdir()
        (root / "docs").mkdir()
        (root / "assets/payload.txt").write_bytes(payload)
        (root / "docs/distribution-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        git(root, "init", "--quiet", "--template=")
        git(root, "add", "--", "assets/payload.txt", "docs/distribution-manifest.json")
        git(root, "commit", "--quiet", "-m", "Seed synthetic distribution fixture")
        return root

    def run_copier_main(self, arguments):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = candidate_copier.main(arguments)
        return exit_code, json.loads(output.getvalue())

    def make_directory_reparse(self, link: Path, target: Path):
        if os.name != "nt":
            os.symlink(target, link, target_is_directory=True)
            return
        powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        quote = lambda value: "'" + str(value).replace("'", "''") + "'"
        script = (
            f"New-Item -ItemType Junction -Path {quote(link)} -Target {quote(target)} | Out-Null; "
            f"if ((Get-Item -LiteralPath {quote(link)} -Force).Target -ne {quote(target)}) {{ exit 3 }}"
        )
        run = subprocess.run(
            [str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
            cwd=self.workspace, shell=False, capture_output=True, text=True,
            encoding="utf-8", timeout=15,
        )
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def swap_directory_for_reparse(self, directory: Path, moved: Path, target: Path,
                                    checked: threading.Event, release: threading.Event,
                                    errors: list[BaseException]):
        if not checked.wait(timeout=15):
            errors.append(TimeoutError("filesystem boundary was not reached"))
            release.set()
            return
        try:
            os.replace(directory, moved)
            self.make_directory_reparse(directory, target)
        except BaseException as error:
            errors.append(error)
        finally:
            release.set()

    def remove_reparse_and_restore(self, link: Path, moved: Path):
        try:
            info = os.lstat(link)
        except FileNotFoundError:
            info = None
        if info is not None:
            attributes = getattr(info, "st_file_attributes", 0)
            if stat.S_ISLNK(info.st_mode) or attributes & 0x400:
                if stat.S_ISDIR(info.st_mode) or attributes & 0x10:
                    os.rmdir(link)
                else:
                    link.unlink()
        if moved.exists() and not os.path.lexists(link):
            os.replace(moved, link)

    def run_race_copy(self, source: Path, target: Path, gate_path: Path,
                      outside: Path, moved: Path, checked_path: Path):
        checked = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        actor = threading.Thread(
            target=self.swap_directory_for_reparse,
            args=(gate_path, moved, outside, checked, release, errors),
            daemon=True,
        )
        original = candidate_copier._assert_no_reparse_components

        def gate(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if Path(path) == checked_path:
                checked.set()
                if not release.wait(timeout=15):
                    raise TimeoutError("copy boundary race did not complete")
            return result

        actor.start()
        try:
            with patch.object(candidate_copier, "_assert_no_reparse_components", gate):
                exit_code, result = self.run_copier_main([
                    "--root", str(source), "--target", str(target),
                    "--allow-output-root", str(self.workspace),
                ])
        finally:
            release.set()
            actor.join(timeout=15)
            self.remove_reparse_and_restore(gate_path, moved)
        self.assertFalse(actor.is_alive(), "source race worker did not terminate")
        return exit_code, result, errors

    def test_fix1_dist_02_verify_report_inside_candidate_is_refused_without_tree_change(self):
        candidate, _ = self.copied_candidate("verify-report-overlap", target_root=self.report_workspace)
        before = source_bytes(candidate)
        report = candidate / "verify-report.json"
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(WORKTREE), "--verify", str(candidate),
             "--allow-output-root", str(self.workspace),
             "--allow-output-root", str(self.report_workspace), "--report", str(report)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        after = source_bytes(candidate)
        result = json.loads(run.stdout)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual("OUTPUT_OVERLAP", result["findings"][0]["code"])
        self.assertFalse(report.exists())
        self.assertEqual(before, after)

    def test_fix1_dist_02_copy_report_at_candidate_path_is_refused_without_creation(self):
        source = self.seed_copy_fixture("copy-report-overlap-source")
        before = source_bytes(source)
        target = self.report_workspace / "candidate.json"
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(source), "--target", str(target),
             "--allow-output-root", str(self.workspace),
             "--allow-output-root", str(self.report_workspace), "--report", str(target)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        result = json.loads(run.stdout)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual("OUTPUT_OVERLAP", result["findings"][0]["code"])
        self.assertFalse(target.exists())
        self.assertEqual(before, source_bytes(source))

    def test_fix1_dist_02_copy_report_inside_source_inventory_is_refused_without_change(self):
        source = self.seed_copy_fixture("copy-report-source-overlap")
        before = source_bytes(source)
        report = source / "docs" / "verification.json"
        target = self.workspace / "source-report-candidate"
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(source), "--target", str(target),
             "--allow-output-root", str(source), "--allow-output-root", str(self.workspace),
             "--report", str(report)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        result = json.loads(run.stdout)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertEqual("OUTPUT_OVERLAP", result["findings"][0]["code"])
        self.assertFalse(report.exists())
        self.assertFalse(target.exists())
        self.assertEqual(before, source_bytes(source))

    def test_fix1_dist_06_source_hardlink_is_refused_before_candidate_creation(self):
        source = self.seed_copy_fixture()
        marker = self.workspace / "synthetic-outside-marker.bin"
        marker.write_bytes(b"synthetic marker; not private data")
        source_file = source / "assets" / "payload.txt"
        source_file.unlink()
        os.link(marker, source_file)
        marker_before = marker.read_bytes()
        target = self.workspace / "hardlinked-source-candidate"
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(source), "--target", str(target),
             "--allow-output-root", str(self.workspace)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        result = json.loads(run.stdout)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertIn("HARDLINK_REFUSED", {item["code"] for item in result["findings"]})
        self.assertFalse(target.exists())
        self.assertEqual(marker_before, marker.read_bytes())

    def test_fix1_dist_19_candidate_hardlink_is_refused_without_reading_external_marker(self):
        source = self.seed_copy_fixture()
        candidate = self.workspace / "hardlinked-candidate"
        report = self.report_workspace / "hardlinked-verification.json"
        copied, receipt = self.run_copier_main([
            "--root", str(source), "--target", str(candidate),
            "--allow-output-root", str(self.workspace),
        ])
        self.assertEqual(0, copied, receipt)
        marker = self.workspace / "candidate-synthetic-marker.bin"
        marker.write_bytes(b"synthetic candidate marker; not private data")
        marker_before = marker.read_bytes()
        candidate_file = candidate / "assets" / "payload.txt"
        candidate_file.unlink()
        os.link(marker, candidate_file)

        verified, result = self.run_copier_main([
            "--root", str(source), "--verify", str(candidate),
            "--allow-output-root", str(self.workspace),
            "--allow-output-root", str(self.report_workspace), "--report", str(report),
        ])
        self.assertEqual(1, verified, result)
        self.assertEqual("invalid", result["status"])
        self.assertIn("HARDLINK_REFUSED", {item["code"] for item in result["findings"]})
        self.assertEqual(marker_before, marker.read_bytes())
        self.assertNotIn(marker_before.decode("ascii"), report.read_text(encoding="utf-8"))
        verification = json.loads(report.read_text(encoding="utf-8"))
        payload_row = next(item for item in verification["files"] if item["path"] == "assets/payload.txt")
        self.assertIsNone(payload_row["candidate_sha256"])
        self.assertEqual(1, verification["verified_count"])

    def test_fix1_dist_06_source_reparse_race_is_rejected_before_external_bytes_are_copied(self):
        source = self.seed_copy_fixture("source-race", b"approved synthetic source")
        outside = self.workspace / "outside-source"
        outside.mkdir()
        outside_payload = outside / "payload.txt"
        outside_payload.write_bytes(b"SYNTHETIC-OUTSIDE-MARKER")
        target = self.workspace / "source-race-candidate"
        exit_code, result, errors = self.run_race_copy(
            source, target, source / "assets", outside, source / "assets-moved",
            source / "assets" / "payload.txt",
        )
        self.assertEqual([], errors, repr(errors))
        self.assertNotEqual(0, exit_code, result)
        self.assertEqual(b"SYNTHETIC-OUTSIDE-MARKER", outside_payload.read_bytes())
        copied_bytes = b"".join(
            path.read_bytes() for path in target.rglob("*") if path.is_file()
        ) if target.exists() else b""
        self.assertNotIn(b"SYNTHETIC-OUTSIDE-MARKER", copied_bytes)
        self.assertIn("UNSAFE_PATH", {item["code"] for item in result["findings"]})
        self.assertFalse(target.exists(), "source must be validated before candidate creation")

    def test_fix1_dist_19_destination_reparse_race_never_creates_output_outside_allowed_root(self):
        source = self.seed_copy_fixture("destination-race", b"SYNTHETIC-CANDIDATE-PAYLOAD")
        outside = self.workspace / "outside-destination"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_bytes(b"synthetic sentinel remains unchanged")
        target = self.workspace / "destination-race-candidate"
        exit_code, result, errors = self.run_race_copy(
            source, target, target / "assets", outside, target / "assets-moved",
            target / "assets",
        )
        self.assertEqual([], errors, repr(errors))
        self.assertNotEqual(0, exit_code, result)
        self.assertIn("UNSAFE_PATH", {item["code"] for item in result["findings"]})
        self.assertFalse((outside / "payload.txt").exists())
        self.assertEqual(b"synthetic sentinel remains unchanged", sentinel.read_bytes())

    def test_fix1_dist_19_candidate_verify_reparse_race_never_reads_outside_marker(self):
        source = self.seed_copy_fixture("verify-race-source", b"approved synthetic source")
        candidate = self.workspace / "verify-reparse-race-candidate"
        copied, receipt = self.run_copier_main([
            "--root", str(source), "--target", str(candidate),
            "--allow-output-root", str(self.workspace),
        ])
        self.assertEqual(0, copied, receipt)
        assets = candidate / "assets"
        outside = self.workspace / "outside-verification"
        outside.mkdir()
        outside_payload = outside / "payload.txt"
        outside_payload.write_bytes(b"SYNTHETIC-OUTSIDE-MARKER")
        outside_before = outside_payload.read_bytes()
        moved = candidate / "assets-moved"
        report = self.report_workspace / "verify-reparse-race.json"
        checked = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original = candidate_copier._walk_candidate

        def gate(root):
            result = original(root)
            checked.set()
            if not release.wait(timeout=15):
                raise TimeoutError("candidate verification race did not complete")
            return result

        actor = threading.Thread(
            target=self.swap_directory_for_reparse,
            args=(assets, moved, outside, checked, release, errors),
            daemon=True,
        )
        actor.start()
        try:
            with patch.object(candidate_copier, "_walk_candidate", gate):
                exit_code, result = self.run_copier_main([
                    "--root", str(source), "--verify", str(candidate),
                    "--allow-output-root", str(self.workspace),
                    "--allow-output-root", str(self.report_workspace), "--report", str(report),
                ])
        finally:
            release.set()
            actor.join(timeout=15)
            self.remove_reparse_and_restore(assets, moved)
        self.assertFalse(actor.is_alive(), "candidate verification race worker did not terminate")
        self.assertEqual([], errors, repr(errors))
        self.assertNotEqual(0, exit_code, result)
        self.assertEqual(outside_before, outside_payload.read_bytes())
        self.assertNotIn("SYNTHETIC-OUTSIDE-MARKER", report.read_text(encoding="utf-8"))
        record = json.loads(report.read_text(encoding="utf-8"))
        payload_row = next(item for item in record["files"]
                           if item["path"] == "assets/payload.txt")
        self.assertIsNone(payload_row["candidate_sha256"])
        self.assertEqual(1, record["verified_count"])
        self.assertIn("UNSAFE_ENTRY", {item["code"] for item in result["findings"]})

    def add_swas(self, root: Path) -> Path:
        body = (
            "# SWAS-001：参数化导出演示输入\n\n"
            '<a id="basis"></a>\n## Selected basis\n\n'
            "A source-owned local document fixture; not an approval.\n\n"
            '<a id="business"></a>\n## Owned business\n\n'
            "This section is the supplied source, not a hard-coded slide.\n\n"
            '<a id="logical"></a>\n## Logical boundary\n\n'
            "Only the selected source is presented.\n\n"
            '<a id="runtime"></a>\n## Runtime boundary\n\n'
            "No application runtime has been selected.\n"
        )
        return write_metadata(
            root, metadata(id="SWAS-001", kind="architecture-specification", scope=SCOPE),
            body, "architecture/SWAS-001.md",
        )

    def test_dist_01_manifest_is_explicit_and_uses_actual_delivered_files(self):
        manifest = self.manifest()
        self.assertEqual(1, manifest["schemaVersion"])
        self.assertIsInstance(manifest["components"], dict)
        files = manifest["files"]
        self.assertTrue(files)
        paths = [entry["path"] for entry in files]
        self.assertEqual(len(paths), len(set(paths)))
        for entry in files:
            self.assertEqual({"path", "component"}, set(entry))
            path = PurePosixPath(entry["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
            self.assertNotIn("\\", entry["path"])
            self.assertFalse(any(char in entry["path"] for char in "*?[]{}"))
            self.assertIn(entry["component"], manifest["components"])
            source = WORKTREE.joinpath(*path.parts)
            self.assertTrue(source.is_file(), entry["path"])
            self.assertFalse(source.is_symlink(), entry["path"])

        required = {
            "README.md", "AGENTS.md", ".gitignore",
            "docs/distribution.md", "docs/distribution-manifest.json",
            "docs/development.md", "logs/README.md", "verification/README.md",
            "src/README.md", "_templates/items/stakeholder-requirement.md",
            "_templates/items/verification-test.md", "_templates/items/verification-test.feature",
            ".github/skills/implement-task/SKILL.md",
            ".github/skills/verify-change/SKILL.md",
            ".github/utilities/render_presentation.py",
            ".github/utilities/log_interaction.py",
            ".github/contracts/artifact.schema.json",
            ".github/utilities/requirements.lock",
            ".github/workflows/validate-artifacts.yml",
        }
        self.assertTrue(required.issubset(set(paths)), sorted(required - set(paths)))
        self.assertNotIn("docs/agent-support.md", paths, "That file contains historical client results")
        self.assertFalse(any(path.startswith((
            ".github/utilities/tests/", "docs/design/", "docs/plan/", "docs/research/",
        )) for path in paths))
        self.assertFalse(any(path.startswith("logs/") and path != "logs/README.md" for path in paths))

        excluded = {entry["path"]: entry["reason"] for entry in manifest["excluded"]}
        for path in (
            ".github/utilities/tests/", ".github/utilities/distribute_candidate.py",
            ".github/workflows/tooling-tests.yml", ".github/workflows/propose-template-updates.yml",
            "docs/design/", "docs/plan/", "docs/research/", "docs/agent-support.md",
            "logs/", "verification/ddd-alignment.md", ".git/", ".venv/",
        ):
            self.assertIn(path, excluded)

    def test_dist_01_receipt_matches_manifest_files_and_raw_bytes(self):
        manifest = self.manifest()
        target, receipt = self.copied_candidate("receipt-check")
        expected = {item["path"]: item["component"] for item in manifest["files"]}
        actual = {item["path"]: item["component"] for item in receipt["files"]}
        self.assertEqual(expected, actual)
        self.assertEqual("copied", receipt["status"])
        self.assertEqual(0, receipt["exit_code"])
        for item in receipt["files"]:
            source = WORKTREE.joinpath(*PurePosixPath(item["path"]).parts)
            copied = target.joinpath(*PurePosixPath(item["path"]).parts)
            source_bytes_now = source.read_bytes()
            candidate_bytes = copied.read_bytes()
            self.assertEqual(sha256(source_bytes_now), item["source_sha256"], item["path"])
            self.assertEqual(item["source_sha256"], item["candidate_sha256"], item["path"])
            self.assertEqual(source_bytes_now, candidate_bytes, item["path"])
            self.assertEqual(len(source_bytes_now), item["size"], item["path"])
        self.assertEqual(
            (git(WORKTREE, "rev-parse", "HEAD")),
            receipt["provenance"]["source_commit"],
        )
        self.assertIsInstance(receipt["provenance"]["dirty_scope"], list)
        self.assertTrue(receipt["allowed_output_roots"])
        self.assertTrue(any(value.startswith(".venv/task12-fixtures") for value in receipt["allowed_output_roots"]))
        self.assertNotIn(".git", {path.split("/")[0] for path in actual})
        excluded = {item["path"]: item["reason"] for item in receipt["excluded_files"]}
        for path in (
            ".github/utilities/tests/test_distribution.py",
            ".github/utilities/distribute_candidate.py",
            "docs/agent-support.md",
            "logs/2026-10-19-task12-candidate.md",
            "verification/ddd-alignment.md",
        ):
            self.assertIn(path, excluded)

    def test_dist_02_existing_nonempty_target_conflicts_without_owner_byte_change(self):
        self.assertTrue(COPY_TOOL.is_file(), "DIST-02 requires the real candidate copy boundary")
        target = self.workspace / "owner-target"
        target.mkdir()
        marker = target / "owner.txt"
        marker.write_bytes(b"owner bytes must survive")
        before = source_bytes(target)
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(WORKTREE), "--target", str(target),
             "--allow-output-root", str(self.workspace)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(1, run.returncode, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual("conflict", result["status"])
        self.assertIn("TARGET_CONFLICT", {item["code"] for item in result["findings"]})
        self.assertEqual(before, source_bytes(target))

    def test_dist_03_plain_guidance_is_readable_without_candidate_runtime_imports(self):
        candidate, _ = self.copied_candidate("docs-only")
        for relative in ("README.md", "AGENTS.md", "docs/distribution.md",
                         "domain-model/README.md", "src/README.md"):
            self.assertTrue((candidate / relative).is_file(), relative)
        code = (
            "from pathlib import Path; import sys; root=Path(sys.argv[1]); "
            "text=(root/'README.md').read_text(encoding='utf-8'); "
            "assert 'README' in text; "
            "assert 'yaml' not in sys.modules and 'jsonschema' not in sys.modules"
        )
        run = subprocess.run(
            [sys.executable, "-I", "-c", code, str(candidate)],
            cwd=candidate, env={k: v for k, v in os.environ.items()
                                if k not in {"PYTHONPATH", "PYTHONHOME"}},
            shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def test_dist_04_registration_stays_unknown_and_src_is_only_a_guide(self):
        candidate, _ = self.copied_candidate("registration-boundary")
        readme = (candidate / "README.md").read_text(encoding="utf-8")
        development = (candidate / "docs/development.md").read_text(encoding="utf-8")
        self.assertIn("待填写", readme)
        self.assertIn("未配置", development)
        self.assertIn("技术栈", development)
        source_files = sorted(path.relative_to(candidate / "src").as_posix()
                              for path in (candidate / "src").rglob("*") if path.is_file())
        self.assertEqual(["README.md"], source_files)
        for relative in ("bc-config.yaml", "model-sources.yaml", "model.yaml", "model.json"):
            self.assertFalse((candidate / relative).exists(), relative)
        for directory in ("domain-model", "stakeholder-requirements",
                          "software-requirements", "verification"):
            contents = [path.name for path in (candidate / directory).iterdir() if path.is_file()]
            self.assertEqual(["README.md"], contents, directory)
        templates = [path for path in (candidate / "_templates").rglob("*") if path.is_file()]
        self.assertTrue(templates)
        for path in templates:
            content = path.read_text(encoding="utf-8-sig")
            self.assertIsNone(
                re.search(r"(?im)^(?:contentState:\s*(?:confirmed|retired)|(?:status|result):\s*(?:pass|fail|approved)\b)",
                          content),
                path.relative_to(candidate).as_posix(),
            )
            self.assertIsNone(
                re.search(r"\b(?:REQ|SR|VT)-001\b", content),
                path.relative_to(candidate).as_posix(),
            )

    def test_dist_05_every_shipped_markdown_link_and_anchor_resolves_inside_candidate(self):
        candidate, _ = self.copied_candidate("markdown-closure")
        problems = list(_local_markdown_links(candidate))
        self.assertEqual([], problems, problems[:20])
        self.assertTrue((candidate / "docs/distribution-manifest.json").is_file())

    def test_dist_06_runtime_imports_are_from_copied_modules_only(self):
        candidate, _ = self.copied_candidate("runtime-closure")
        utilities = candidate / UTILITIES
        code = (
            "import importlib,json,sys\n"
            "from pathlib import Path\n"
            "root=Path(sys.argv[1]).resolve()\n"
            "names=sys.argv[2:]\n"
            "sys.path.insert(0,str(root/'.github/utilities'))\n"
            "found={}\n"
            "for name in names:\n"
            "    module=importlib.import_module(name)\n"
            "    path=Path(module.__file__).resolve()\n"
            "    assert path == (root/'.github/utilities'/(name+'.py')).resolve(), (name,path)\n"
            "    found[name]=str(path)\n"
            "print(json.dumps(found,sort_keys=True))\n"
        )
        run = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "utf8", "-c", code,
             str(candidate), *RUNTIME_MODULES],
            cwd=candidate, env={k: v for k, v in os.environ.items()
                                if k not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"}},
            shell=False, capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        origins = json.loads(run.stdout)
        self.assertEqual(set(RUNTIME_MODULES), set(origins))
        for relative in REQUIRED_RESOURCES:
            self.assertTrue((candidate / relative).is_file(), relative)
        self.assertFalse((candidate / UTILITIES / "tests").exists())
        self.assertFalse((candidate / "docs/research").exists())

    def test_dist_06_missing_copied_schema_fails_instead_of_falling_back_to_maker_tree(self):
        candidate, _ = self.copied_candidate("missing-resource-parent")
        incomplete = self.workspace / "candidate-missing-schema"
        for relative in (f"{UTILITIES}/artifact_io.py", f"{UTILITIES}/check_artifacts.py"):
            destination = incomplete / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((candidate / relative).read_bytes())
        (incomplete / "REQ-001.md").write_text(
            "---\nschemaVersion: 1\nid: REQ-001\nkind: stakeholder-requirement\n"
            "scope: sample/CTX-001\ncontentState: draft\n---\n# REQ-001 fixture\n",
            encoding="utf-8", newline="\n",
        )
        run = self.candidate_cli(incomplete, "check_artifacts", "--root", str(incomplete))
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual("input-error", result["status"])
        self.assertEqual("CONTRACT_ERROR", result["findings"][0]["code"])
        self.assertEqual(".github/contracts/artifact.schema.json",
                         Path(result["findings"][0]["path"]).relative_to(incomplete).as_posix())

    def test_dist_07_downstream_workflow_references_only_candidate_runtime_and_lock(self):
        candidate, _ = self.copied_candidate("workflow-closure")
        workflow = (candidate / ".github/workflows/validate-artifacts.yml").read_text(encoding="utf-8")
        self.assertIn(".github/utilities/requirements.lock", workflow)
        self.assertIn(".github/utilities/hook_checks.py", workflow)
        self.assertTrue((candidate / ".github/contracts/artifact.schema.json").is_file())
        self.assertNotIn("run_tooling_tests.py", workflow)
        self.assertNotIn(".github/utilities/tests", workflow)
        self.assertFalse((candidate / ".github/workflows/tooling-tests.yml").exists())
        self.assertFalse((candidate / ".github/workflows/propose-template-updates.yml").exists())
        result = self.candidate_cli(candidate, "check_artifacts", "--root", str(candidate))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("empty", json.loads(result.stdout)["status"])
        self.assertEqual(0, json.loads(result.stdout)["checked_count"])

    def test_dist_08_maker_tests_and_candidate_copier_stay_outside_candidate(self):
        candidate, _ = self.copied_candidate("maintainer-separation")
        self.assertTrue((WORKTREE / ".github/utilities/tests/test_distribution.py").is_file())
        self.assertTrue(COPY_TOOL.is_file())
        for relative in (
            ".github/utilities/tests", ".github/utilities/distribute_candidate.py",
            ".github/workflows/tooling-tests.yml", ".github/workflows/propose-template-updates.yml",
        ):
            self.assertFalse((candidate / relative).exists(), relative)

    def test_dist_09_optional_hooks_are_present_but_copy_does_not_install_them(self):
        before_config = git(WORKTREE, "config", "--local", "--list")
        candidate, _ = self.copied_candidate("hooks-remain-optional")
        self.assertTrue((candidate / ".github/hooks/pre-commit").is_file())
        self.assertTrue((candidate / ".github/hooks/commit-msg").is_file())
        self.assertTrue((candidate / ".github/utilities/install_hooks.py").is_file())
        self.assertFalse((candidate / ".git").exists())
        self.assertFalse((candidate / ".git/hooks").exists())
        self.assertFalse(any(candidate.rglob("*.artifact-maintenance.json")))
        self.assertEqual(before_config, git(WORKTREE, "config", "--local", "--list"))

    def test_dist_10_runtime_prerequisites_are_the_existing_lock_not_installed_by_copy(self):
        candidate, _ = self.copied_candidate("runtime-lock")
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))
        self.assertEqual("6.0.2", importlib.metadata.version("PyYAML"))
        self.assertEqual("4.23.0", importlib.metadata.version("jsonschema"))
        requirements = (candidate / f"{UTILITIES}/requirements.txt").read_text(encoding="utf-8")
        lock = (candidate / f"{UTILITIES}/requirements.lock").read_text(encoding="utf-8")
        self.assertIn("PyYAML==6.0.2", requirements)
        self.assertIn("jsonschema==4.23.0", requirements)
        self.assertIn("typing-extensions==4.16.0 ; python_version < \"3.13\"", lock)
        self.assertIn("Python 3.11+", (candidate / "docs/development.md").read_text(encoding="utf-8"))
        self.assertFalse((candidate / "requirements.txt").exists(), "No business application dependency manifest")

    def test_dist_11_audio_and_pdf_pptx_keep_real_unavailable_refusal(self):
        candidate, _ = self.copied_candidate("unavailable-formats")
        fixture = self.workspace / "render-inputs"
        fixture.mkdir()
        write_delivery_fixture(fixture)
        swas = self.add_swas(fixture)
        baseline = "sha256:" + sha256(swas.read_bytes())

        audio = self.candidate_cli(candidate, "transcribe_audio", "--source",
                                   str(self.workspace / "missing-audio.wav"))
        self.assertEqual(2, audio.returncode, audio.stdout + audio.stderr)
        self.assertIn("AUDIO_AUTHORIZATION_REQUIRED", audio.stdout)
        self.assertFalse((self.workspace / "missing-audio.wav").exists())

        for output_format in ("pdf", "pptx"):
            with self.subTest(output_format=output_format):
                output = fixture / f"not-created.{output_format}"
                run = self.candidate_cli(
                    candidate, "render_presentation", "--root", str(fixture),
                    "--scope", SCOPE, "--format", output_format,
                    "--source", "architecture/SWAS-001.md", "--baseline", baseline,
                    "--output", output.name,
                )
                self.assertEqual(2, run.returncode, run.stdout + run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual("unavailable", result["status"])
                self.assertFalse(output.exists())
        self.assertIn("No package or version has been selected",
                      (candidate / f"{UTILITIES}/requirements-media.txt").read_text(encoding="utf-8"))
        self.assertIn("PDF/PPTX", (candidate / f"{UTILITIES}/requirements-rendering.txt").read_text(encoding="utf-8"))

    def test_dist_12_inventory_cli_distinguishes_empty_and_positive(self):
        candidate, _ = self.copied_candidate("inventory-states")
        empty = self.workspace / "empty-inventory"
        empty.mkdir()
        empty_run = self.candidate_cli(candidate, "check_artifacts", "--root", str(empty))
        self.assertEqual(0, empty_run.returncode, empty_run.stdout + empty_run.stderr)
        self.assertEqual("empty", json.loads(empty_run.stdout)["status"])
        self.assertEqual(0, json.loads(empty_run.stdout)["checked_count"])

        valid = self.workspace / "valid-inventory"
        valid.mkdir()
        write_metadata(valid, metadata(id="REQ-001", kind="stakeholder-requirement"),
                       "# REQ-001\n", "stakeholder-requirements/REQ-001.md")
        clean = self.candidate_cli(candidate, "check_artifacts", "--root", str(valid))
        self.assertEqual(0, clean.returncode, clean.stdout + clean.stderr)
        self.assertEqual("clean", json.loads(clean.stdout)["status"])
        self.assertGreater(json.loads(clean.stdout)["checked_count"], 0)

    def test_dist_12_invalid_inventory_is_not_empty_or_success(self):
        candidate, _ = self.copied_candidate("invalid-inventory")
        invalid = self.workspace / "invalid-inventory-root"
        invalid.mkdir()
        (invalid / "REQ-001.md").write_text(
            "---\nschemaVersion: 1\nid: REQ-001\nkind: unknown-kind\n"
            "scope: sample/CTX-001\ncontentState: draft\n---\n# Invalid\n",
            encoding="utf-8", newline="\n",
        )
        run = self.candidate_cli(candidate, "check_artifacts", "--root", str(invalid))
        self.assertIn(run.returncode, (1, 2), run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertIn(result["status"], ("invalid", "input-error"))
        self.assertNotEqual("empty", result["status"])

    def test_dist_12_exact_commit_is_checked_and_bad_base_never_falls_back(self):
        candidate, _ = self.copied_candidate("exact-base")
        fixture = self.workspace / "git-inventory"
        base = seed_git_repo(fixture)
        write_metadata(fixture, metadata(id="REQ-001", kind="stakeholder-requirement"),
                       "# REQ-001\n", "stakeholder-requirements/REQ-001.md")
        git(fixture, "add", "--", "stakeholder-requirements/REQ-001.md")
        git(fixture, "commit", "--quiet", "-m", "Add exact formal input")
        exact = git(fixture, "rev-parse", "HEAD")
        self.assertNotEqual(base, exact)
        accepted = self.candidate_cli(candidate, "check_artifacts", "--root", str(fixture), "--base", exact)
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        self.assertEqual(exact, json.loads(accepted.stdout)["baseline"]["base_sha"])

        rejected = self.candidate_cli(candidate, "check_artifacts", "--root", str(fixture),
                                       "--base", exact[:12])
        self.assertEqual(2, rejected.returncode, rejected.stdout + rejected.stderr)
        rejected_report = json.loads(rejected.stdout)
        self.assertEqual("input-error", rejected_report["status"])
        self.assertIn(rejected_report["findings"][0]["code"], ("INVALID_BASE", "BASE_UNAVAILABLE"))
        self.assertNotEqual(exact, (rejected_report.get("baseline") or {}).get("base_sha"))

    def test_dist_13_four_owner_acceptances_have_full_layered_coverage(self):
        candidate, _ = self.copied_candidate("four-targets")
        fixture = self.workspace / "four-owner-fixture"
        fixture.mkdir()
        write_delivery_fixture(fixture)
        args = ["--root", str(fixture)]
        for target in DELIVERY:
            args.extend(("--delivery", target))
        result = self.candidate_cli(candidate, "check_traceability", *args)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("clean", report["status"])
        self.assertEqual((), tuple(report["findings"]))
        self.assertIn("verification/VT-001.md", source_bytes(fixture))
        self.assertIn("verification/VT-002.md", source_bytes(fixture))
        self.assertFalse((fixture / "user-stories").exists(), "US is not a required bridge")
        self.assertIn("not-run", (fixture / "verification/VT-001.md").read_text(encoding="utf-8"))
        self.assertIn("not-run", (fixture / "verification/VT-002.md").read_text(encoding="utf-8"))

    def test_dist_13_missing_software_reject_and_dangling_target_are_exact_findings(self):
        candidate, _ = self.copied_candidate("coverage-defects")
        omitted = self.workspace / "omitted-target"
        omitted.mkdir()
        write_delivery_fixture(omitted, omit_software_reject=True)
        args = ["--root", str(omitted)]
        for target in DELIVERY:
            args.extend(("--delivery", target))
        result = self.candidate_cli(candidate, "check_traceability", *args)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        uncovered = [finding["target"] for finding in report["findings"]
                     if finding["code"] == "UNCOVERED_ACCEPTANCE"]
        self.assertEqual([DELIVERY[3]], uncovered)
        self.assertIn(
            "SR-001-AC-02",
            (omitted / "software-requirements/SR-001.md").read_text(encoding="utf-8"),
        )

        dangling = self.workspace / "dangling-target"
        dangling.mkdir()
        write_delivery_fixture(dangling)
        write_metadata(
            dangling, metadata(id="VT-003", kind="verification-test", targets=[{
                "target": "sample/CTX-001/REQ-999#req-999-ac-01",
                "criterionAnchor": "extra",
            }]),
            "# VT-003 fixture\n<a id=\"plan\"></a>\n## Plan\n\n"
            "| 验证层次 | 业务验收 |\n\n"
            + criterion_block("extra", "No target record is created.",
                              "Compare the local fixture inventory.",
                              "No application execution."),
            "verification/VT-003.md",
        )
        args = ["--root", str(dangling)]
        for target in DELIVERY:
            args.extend(("--delivery", target))
        result = self.candidate_cli(candidate, "check_traceability", *args)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        findings = json.loads(result.stdout)["findings"]
        self.assertIn(("DANGLING_TARGET", "sample/CTX-001/REQ-999#req-999-ac-01"),
                      [(item["code"], item["target"]) for item in findings])

    def test_dist_14_candidate_model_and_report_preserve_gaps_and_not_run(self):
        candidate, _ = self.copied_candidate("model-report")
        fixture = self.workspace / "model-report-fixture"
        object_sha = seed_implementation_fixture(fixture)

        report_path = fixture / "implementation-report.json"
        collected = self.candidate_cli(
            candidate, "collect_implementation_report", "--root", str(fixture),
            "--object", object_sha, "--scope", SCOPE, "--output", "implementation-report.json",
        )
        self.assertEqual(0, collected.returncode, collected.stdout + collected.stderr)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(object_sha, report["object"]["baseline"])
        self.assertEqual(list(DELIVERY), [entry["target"] for entry in report["entries"]])
        self.assertTrue(all(entry["execution"]["status"] == "not-run" for entry in report["entries"]))
        self.assertTrue(all(entry["applicability"]["state"] == "unverified" for entry in report["entries"]))

        requirements = fixture / "stakeholder-requirements/REQ-001.md"
        software = fixture / "software-requirements/SR-001.md"
        model_sources = (
            "schemaVersion: 1\n"
            "scopes:\n"
            "  sample/CTX-001:\n"
            "    requirements:\n"
            "      - path: stakeholder-requirements/REQ-001.md\n"
            f"        baseline: sha256:{sha256(requirements.read_bytes())}\n"
            "      - path: software-requirements/SR-001.md\n"
            f"        baseline: sha256:{sha256(software.read_bytes())}\n"
            "    verification:\n"
            "      - path: implementation-report.json\n"
            f"        baseline: sha256:{sha256(report_path.read_bytes())}\n"
            "    risk:\n"
            "      - path: absent-risk-source.yaml\n"
            f"        baseline: sha256:{'0' * 64}\n"
        )
        (fixture / "model-sources.yaml").write_text(
            model_sources, encoding="utf-8", newline="\n",
        )
        model_path = fixture / "model.json"
        exported = self.candidate_cli(
            candidate, "export_model", "--root", str(fixture), "--scope", SCOPE,
            "--output", "model.json",
        )
        self.assertEqual(0, exported.returncode, exported.stdout + exported.stderr)
        model = json.loads(model_path.read_text(encoding="utf-8"))
        self.assertEqual(SCOPE, model["scope"])
        self.assertEqual({"requirements", "stories", "architecture", "sequences", "verification",
                          "quality", "governance", "risk", "release"}, set(model["views"]))
        self.assertEqual("available", model["views"]["verification"]["state"])
        self.assertIn("absent-risk-source.yaml", " ".join(model["views"]["risk"]["gaps"]))
        pointer = {"reference": "implementation-report.json",
                   "baseline": "sha256:" + sha256(report_path.read_bytes())}
        self.assertEqual([pointer], model["implementationReports"])
        self.assertIn(pointer, model["views"]["verification"]["evidenceRefs"])
        self.assertNotIn('"entries"', json.dumps(model))
        checked = self.candidate_cli(
            candidate, "export_model", "--root", str(fixture), "--scope", SCOPE,
            "--check", "model.json",
        )
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)

        before = source_bytes(fixture)
        conflict = self.candidate_cli(
            candidate, "export_model", "--root", str(fixture), "--scope", SCOPE,
            "--output", "model.json",
        )
        self.assertEqual(2, conflict.returncode, conflict.stdout + conflict.stderr)
        self.assertIn("REPORT_CONFLICT", conflict.stdout)
        self.assertEqual(before, source_bytes(fixture))

    def test_dist_14_source_inspection_is_local_read_only(self):
        candidate, _ = self.copied_candidate("source-inspection")
        fixture = self.workspace / "source-inspection-fixture"
        seed_implementation_fixture(fixture)
        before = source_bytes(fixture)
        result = self.candidate_cli(
            candidate, "setup_domain_source", "--root", str(fixture),
            "--config", "bc-config.yaml", "--source-id", "owned-domain",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("ready", report["status"])
        self.assertEqual("no-change", report["outcome"])
        self.assertEqual([], report["written"])
        self.assertEqual(before, source_bytes(fixture))

    def test_dist_15_local_template_update_is_a_read_only_proposal(self):
        candidate, _ = self.copied_candidate("template-update")
        base, local, proposed = (self.workspace / name for name in ("base", "local", "proposed"))
        for root in (base, local, proposed):
            root.mkdir()
        (base / "guide.md").write_bytes(b"Original guidance.\n")
        (local / "guide.md").write_bytes(b"Original guidance.\n")
        (proposed / "guide.md").write_bytes(b"Candidate guidance.\n")
        before = tuple(source_bytes(root) for root in (base, local, proposed))
        result = self.candidate_cli(
            candidate, "plan_template_update", "--base", str(base),
            "--local", str(local), "--candidate", str(proposed),
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("proposed", report["status"])
        self.assertTrue(any(change["path"] == "guide.md" for change in report["changes"]))
        self.assertEqual(before, tuple(source_bytes(root) for root in (base, local, proposed)))

    def test_dist_15_offline_extraction_and_scoring_use_real_candidate_modules(self):
        candidate, _ = self.copied_candidate("offline-adapters")
        fixture = self.workspace / "offline-input"
        fixture.mkdir()
        source = fixture / "notes.txt"
        source.write_bytes(b"Rule: A source statement remains a candidate.\r\n")
        original = source.read_bytes()
        extracted_path = fixture / "candidates.json"
        extracted = self.candidate_cli(
            candidate, "extract_source", "--root", str(fixture),
            "--source", "notes.txt", "--kind", "text", "--output", str(extracted_path),
        )
        self.assertEqual(0, extracted.returncode, extracted.stdout + extracted.stderr)
        envelope = json.loads(extracted_path.read_text(encoding="utf-8"))
        self.assertEqual(("extracted", 1), (envelope["status"], envelope["candidate_count"]))
        self.assertEqual(original, source.read_bytes())
        scored_path = fixture / "scored.json"
        scored = self.candidate_cli(
            candidate, "score_candidates", "--root", str(fixture),
            "--input", str(extracted_path), "--output", str(scored_path),
        )
        self.assertEqual(0, scored.returncode, scored.stdout + scored.stderr)
        scoring = json.loads(scored_path.read_text(encoding="utf-8"))
        self.assertEqual(1, len(scoring["candidates"]))
        self.assertIn("score", scoring["candidates"][0])

    def test_dist_15_parameterized_html_svg_render_and_pdf_pptx_refusal(self):
        candidate, _ = self.copied_candidate("renderer-inputs")
        fixture = self.workspace / "rendered-source"
        fixture.mkdir()
        write_delivery_fixture(fixture)
        swas = self.add_swas(fixture)
        baseline = "sha256:" + sha256(swas.read_bytes())
        for output_format in ("html", "svg"):
            with self.subTest(output_format=output_format):
                result = self.candidate_cli(
                    candidate, "render_presentation", "--root", str(fixture),
                    "--scope", SCOPE, "--format", output_format,
                    "--source", "architecture/SWAS-001.md", "--baseline", baseline,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                if output_format == "html":
                    self.assertIn("SWAS-001", result.stdout)
                    self.assertIn("This section is the supplied source, not a hard-coded slide.", result.stdout)
                else:
                    self.assertIn("<svg", result.stdout)
                    self.assertIn("SWAS-001", result.stdout)
        for output_format in ("pdf", "pptx"):
            result = self.candidate_cli(
                candidate, "render_presentation", "--root", str(fixture),
                "--scope", SCOPE, "--format", output_format,
                "--source", "architecture/SWAS-001.md", "--baseline", baseline,
            )
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertEqual("unavailable", json.loads(result.stdout)["status"])

    def test_dist_15_ledger_summary_is_read_only_and_writer_refuses_missing_attestation(self):
        candidate, _ = self.copied_candidate("ledger")
        template = candidate / "_templates/reports/ai-interaction-log.csv"
        header = template.read_bytes()
        fixture = self.workspace / "synthetic-ledger.csv"
        fixture.write_bytes(
            header + b"1,fixture-only,2026-10-19T00:00:00Z,fixture,1,TASK12,README.md,"
            b"sha256:fixture,synthetic local input,,,,,\r\n"
        )
        before = fixture.read_bytes()
        summary = self.candidate_cli(candidate, "summarize_usage", "--log", str(fixture))
        self.assertEqual(0, summary.returncode, summary.stdout + summary.stderr)
        result = json.loads(summary.stdout)
        self.assertEqual(1, result["record_count"])
        self.assertEqual(1, result["usage"]["unknown_record_count"])
        self.assertEqual(sha256(before), result["source_sha256"])
        self.assertFalse(fixture.with_name(fixture.name + ".lock").exists())

        refused = self.candidate_cli(
            candidate, "log_interaction", "--log", str(fixture),
            "--record-id", "not-written", "--time", "2026-10-19T00:00:00Z",
            "--tool", "fixture", "--tool-version", "1", "--task-ref", "TASK12",
            "--object-ref", "README.md", "--object-baseline", "sha256:fixture",
            "--summary", "no write attestation supplied",
        )
        self.assertEqual(2, refused.returncode, refused.stdout + refused.stderr)
        self.assertIn("WRITE_ATTESTATION_REQUIRED", refused.stderr)
        self.assertEqual(before, fixture.read_bytes())
        self.assertFalse(fixture.with_name(fixture.name + ".lock").exists())

    def test_dist_16_candidate_contains_no_maker_paths_results_or_credential_markers(self):
        candidate, _ = self.copied_candidate("leakage-check")
        all_files = [path for path in candidate.rglob("*") if path.is_file()]
        relatives = {path.relative_to(candidate).as_posix() for path in all_files}
        self.assertFalse(any(path.startswith((
            ".git/", ".venv/", ".github/utilities/tests/", "docs/design/",
            "docs/plan/", "docs/research/",
        )) for path in relatives))
        self.assertNotIn("docs/agent-support.md", relatives)
        self.assertFalse(any(path.startswith("logs/") and path != "logs/README.md" for path in relatives))
        forbidden = (
            re.compile(rb"(?i)C:\\Users\\[^\\\r\n]+\\"),
            re.compile(rb"(?i)\.copilot[\\/]+session-state"),
            re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
            re.compile(rb"AKIA[0-9A-Z]{16}"),
        )
        for path in all_files:
            raw = path.read_bytes()
            for marker in forbidden:
                self.assertIsNone(marker.search(raw), path.relative_to(candidate).as_posix())

    def test_dist_17_original_t05_fixed_input_stays_in_a_disposable_document_copy(self):
        candidate, _ = self.copied_candidate("t05-source")
        exercise = self.workspace / "T05-document-only"
        exercise.mkdir()
        for relative in (
            "README.md", "src/README.md", "docs/development.md",
            "_templates/items/development-log.md", "logs/README.md",
        ):
            destination = exercise / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((candidate / relative).read_bytes())
        readme = exercise / "README.md"
        before_candidate = (candidate / "README.md").read_bytes()
        text = readme.read_text(encoding="utf-8")
        self.assertIn("| 项目名称 | 待填写 |", text)
        self.assertIn("| 当前工作范围摘要 | 待填写，尚未确认 |", text)
        text = text.replace("| 项目名称 | 待填写 |", "| 项目名称 | 骨架文档演练 |", 1)
        text = text.replace(
            "| 当前工作范围摘要 | 待填写，尚未确认 |",
            "| 当前工作范围摘要 | 只维护资料，不创建应用 |", 1,
        )
        readme.write_text(text, encoding="utf-8", newline="\n")
        self.assertIn("骨架文档演练", readme.read_text(encoding="utf-8"))
        self.assertIn("只维护资料，不创建应用", readme.read_text(encoding="utf-8"))
        self.assertIn("project-registration", (exercise / "src/README.md").read_text(encoding="utf-8"))
        self.assertEqual(before_candidate, (candidate / "README.md").read_bytes())
        self.assertFalse((exercise / "src" / "app.py").exists())
        self.assertFalse((exercise / "verification" / "VT-001.md").exists())

    def test_dist_17_original_t07_t11_t12_boundaries_remain_visible(self):
        candidate, _ = self.copied_candidate("original-boundaries")
        development = (candidate / "docs/development.md").read_text(encoding="utf-8")
        self.assertIn("业务应用仍未配置", development)
        self.assertTrue((candidate / ".github/skills/verify-change/SKILL.md").is_file())
        self.assertEqual(["README.md"], sorted(path.name for path in (candidate / "src").iterdir()))
        self.assertFalse((candidate / "docs/research").exists())
        self.assertFalse((candidate / "docs/design").exists())
        self.assertFalse((candidate / ".git").exists())

    def test_dist_17_original_t13_fixed_rule_facts_are_only_test_fixture_inputs(self):
        candidate, _ = self.copied_candidate("domain-input-boundary")
        fixture = self.workspace / "fixed-domain-input"
        fixture.mkdir()
        write_delivery_fixture(fixture)
        body = (
            "# DM-001：固定文档演练素材\n\n"
            "概念：成员、物品、借用记录；每条借用记录关联一名成员与一件物品；未归还记录计为在借。\n\n"
            "成员资格上下文提供资格有效性，不管理借还或额度。借用上下文依据资格结果管理借还与在借额度，不修改成员资格。\n\n"
            '<a id="rule-001"></a>\n## RULE-001：初始额度\n\n'
            "借用时须有有效资格，每名成员最多有 2 件在借物品。资格有效且已有 1 件时可借第 2 件；"
            "已有 2 件时拒绝新增且不改变现有记录。\n\n"
            "资格失效后既有借用的处理、并发一致性仍未定义。\n"
        )
        write_metadata(fixture, metadata(id="DM-001", kind="domain-model"), body, "domain-model/DM-001.md")
        before = (fixture / "domain-model/DM-001.md").read_bytes()
        self.assertTrue((candidate / "_templates/items/invariant.md").is_file())
        self.assertTrue((candidate / "_templates/items/bounded-context.md").is_file())
        facts = before.decode("utf-8")
        for statement in (
            "成员、物品、借用记录", "未归还记录计为在借",
            "成员资格上下文提供资格有效性", "借用上下文依据资格结果",
            "已有 1 件时可借第 2 件", "已有 2 件时拒绝新增",
            "资格失效后既有借用的处理、并发一致性仍未定义",
        ):
            self.assertIn(statement, facts)
        checked = self.candidate_cli(candidate, "check_artifacts", "--root", str(fixture))
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        self.assertEqual("clean", json.loads(checked.stdout)["status"])
        arguments = ["--root", str(fixture)]
        for target in DELIVERY:
            arguments.extend(("--delivery", target))
        trace = self.candidate_cli(candidate, "check_traceability", *arguments)
        self.assertEqual(0, trace.returncode, trace.stdout + trace.stderr)
        self.assertEqual("clean", json.loads(trace.stdout)["status"])
        self.assertFalse((fixture / "user-stories").exists(), "No US is needed for this path")
        self.assertEqual(before, (fixture / "domain-model/DM-001.md").read_bytes())
        self.assertFalse((candidate / "domain-model/DM-001.md").exists(),
                         "Fixed P3 exercise data must not ship in the candidate")

    def test_dist_18_rule_change_uses_exact_local_base_and_keeps_behavior_not_run(self):
        candidate, _ = self.copied_candidate("rule-change-impact")
        fixture = self.workspace / "rule-change-fixture"
        seed_git_repo(fixture)
        write_delivery_fixture(fixture)
        write_metadata(
            fixture,
            metadata(id="TASK-001", kind="development-log",
                     upstream=["sample/CTX-001/SR-001"]),
            "# TASK-001: Local change-impact fixture\n\nTask source only; no application run.\n",
            "tasks/TASK-001.md",
        )
        git(fixture, "add", "--", ".")
        git(fixture, "commit", "--quiet", "-m", "Fixed rule baseline two")
        base = git(fixture, "rev-parse", "HEAD")
        old_vts = {
            relative: git(fixture, "show", f"{base}:{relative}").encode("utf-8")
            for relative in ("verification/VT-001.md", "verification/VT-002.md")
        }
        changes = {
            "domain-model/DM-001.md": [
                ("Allowance limit: 2", "Allowance limit: 3"),
            ],
            "stakeholder-requirements/REQ-001.md": [
                ("有效会员在源规则额度内能完成借用。",
                 "资格有效且已有 2 件在借时可借第 3 件；已有 3 件时拒绝且保留所有记录。"),
                ("超出源规则额度时不得形成新的业务借用。",
                 "已有 3 件在借时拒绝新增且不改变现有记录。"),
            ],
            "software-requirements/SR-001.md": [
                ("在源规则允许范围内提交后新增一条借用记录。",
                 "在借 2 件时提交可新增第 3 条借用记录；在借 3 件时拒绝且不改变记录。"),
                ("超出额度提交时返回拒绝且借用记录不变。",
                 "已有 3 件在借时返回拒绝且借用记录不变。"),
            ],
            "verification/VT-001.md": [
                ("额度内会员取得一次新的借用。", "有效会员在借 2 件后可取得第 3 件借用。"),
                ("超额度会员没有形成新的借用。", "已有 3 件在借时没有形成新的借用。"),
            ],
            "verification/VT-002.md": [
                ("有效请求新增一条关联会员的记录。", "在借 2 件时新增第 3 条关联会员的记录。"),
                ("超额请求返回拒绝且前后记录完全相同。",
                 "在借 3 件时返回拒绝且前后记录完全相同。"),
            ],
        }
        for relative, replacements in changes.items():
            path = fixture / relative
            text = path.read_text(encoding="utf-8")
            for old, new in replacements:
                self.assertIn(old, text, relative)
                text = text.replace(old, new, 1)
            path.write_text(text, encoding="utf-8", newline="\n")
        rule = fixture / "domain-model/DM-001.md"
        vt_before = {
            path.relative_to(fixture).as_posix(): path.read_bytes()
            for path in (fixture / "verification").glob("VT-*.md")
        }
        result = self.candidate_cli(
            candidate, "check_traceability", "--root", str(fixture), "--base", base,
            "--task", "sample/CTX-001/TASK-001",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(base, report["baseline"]["base_sha"])
        self.assertTrue(report["candidates"], report)
        changed_paths = {entry["path"] for entry in report["changed_sources"]}
        self.assertTrue(set(changes) <= changed_paths)
        for relative, old_bytes in old_vts.items():
            self.assertEqual(old_bytes, git(fixture, "show", f"{base}:{relative}").encode("utf-8"))
        for relative, current_bytes in vt_before.items():
            self.assertEqual(current_bytes, (fixture / relative).read_bytes())
            self.assertIn(b"not-run", current_bytes)
        self.assertIn("Allowance limit: 3", rule.read_text(encoding="utf-8"))

    def test_fix2_dist_20_verification_receipt_preserves_commit_and_dirty_scope(self):
        expected_commit = git(WORKTREE, "rev-parse", "HEAD")
        git_environment = {key: value for key, value in os.environ.items()
                           if not key.startswith("GIT_")}
        git_environment.update({
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        })
        status_run = subprocess.run(
            ["git", "--no-pager", "-c", "core.quotepath=false", "-c", "core.fsmonitor=false",
             "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=all"],
            cwd=WORKTREE, env=git_environment, shell=False, capture_output=True,
            text=True, encoding="utf-8",
        )
        self.assertEqual(0, status_run.returncode, status_run.stdout + status_run.stderr)
        status_lines = status_run.stdout.splitlines()
        expected_dirty = sorted(
            ({"status": line[:2], "path": line[3:]} for line in status_lines),
            key=lambda item: item["path"],
        )
        candidate, _ = self.copied_candidate("verify-provenance")
        before = source_bytes(candidate)
        report_path = self.report_workspace / "verification-provenance.json"
        self.assertFalse(report_path.is_relative_to(candidate))
        self.assertFalse(report_path.is_relative_to(WORKTREE))

        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(WORKTREE), "--verify", str(candidate),
             "--allow-output-root", str(self.workspace),
             "--allow-output-root", str(self.report_workspace),
             "--report", str(report_path)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        verification = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual("valid", verification["status"])
        self.assertEqual(0, verification["exit_code"])
        self.assertEqual(expected_commit, verification["provenance"]["source_commit"])
        self.assertEqual(
            expected_dirty,
            sorted(verification["provenance"]["dirty_scope"], key=lambda item: item["path"]),
        )

        expected_hashes = {
            entry["path"]: sha256(
                WORKTREE.joinpath(*PurePosixPath(entry["path"]).parts).read_bytes()
            )
            for entry in self.manifest()["files"]
        }
        reported_hashes = {item["path"]: item["candidate_sha256"] for item in verification["files"]}
        self.assertEqual(len(expected_hashes), 132)
        self.assertEqual(132, verification["verified_count"])
        self.assertEqual(expected_hashes, reported_hashes)
        self.assertEqual(before, source_bytes(candidate))

    def test_dist_19_candidate_verifier_reports_missing_and_drifted_files(self):
        candidate, _ = self.copied_candidate("resource-drift")
        drifted = candidate / "README.md"
        original = drifted.read_bytes()
        drifted.write_bytes(original + b"\nCandidate-only drift marker.\n")
        missing = candidate / ".github/contracts/artifact.schema.json"
        expected = missing.read_bytes()
        missing.unlink()

        report_path = self.report_workspace / "verify-drift.json"
        run = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
             "--root", str(WORKTREE), "--verify", str(candidate),
             "--allow-output-root", str(self.workspace),
             "--allow-output-root", str(self.report_workspace), "--report", str(report_path)],
            cwd=WORKTREE, shell=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(1, run.returncode, run.stdout + run.stderr)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        observed = {(item["code"], item["path"]) for item in report["findings"]}
        self.assertIn(("HASH_MISMATCH", "README.md"), observed)
        self.assertIn(("MISSING_FILE", ".github/contracts/artifact.schema.json"), observed)
        self.assertEqual(original + b"\nCandidate-only drift marker.\n", drifted.read_bytes())
        self.assertEqual(expected, (WORKTREE / ".github/contracts/artifact.schema.json").read_bytes())

    def test_dist_20_repeated_candidate_verification_is_deterministic_and_read_only(self):
        candidate, first_receipt = self.copied_candidate("deterministic-a")
        repeated_candidate, second_receipt = self.copied_candidate("deterministic-b")
        self.assertTrue(repeated_candidate.is_dir())
        self.assertEqual(first_receipt["manifest_sha256"], second_receipt["manifest_sha256"])
        self.assertEqual(first_receipt["provenance"], second_receipt["provenance"])
        self.assertEqual(first_receipt["files"], second_receipt["files"])
        self.assertEqual(first_receipt["excluded_files"], second_receipt["excluded_files"])
        selected = [item["path"] for item in self.manifest()["files"]]
        source_before = {relative: (WORKTREE / relative).read_bytes() for relative in selected}
        args = [
            sys.executable, "-B", "-X", "utf8", str(COPY_TOOL),
            "--root", str(WORKTREE), "--verify", str(candidate),
            "--allow-output-root", str(self.workspace),
        ]
        first = subprocess.run(args, cwd=WORKTREE, shell=False, capture_output=True,
                               text=True, encoding="utf-8")
        second = subprocess.run(args, cwd=WORKTREE, shell=False, capture_output=True,
                                text=True, encoding="utf-8")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            (first_receipt["files"], first_receipt["manifest_sha256"]),
            (second_receipt["files"], second_receipt["manifest_sha256"]),
        )
        self.assertEqual(source_before, {relative: (WORKTREE / relative).read_bytes()
                                        for relative in selected})
