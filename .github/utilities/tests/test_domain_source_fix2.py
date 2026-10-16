"""Task15 fix2 / remaining I3: physical comments and continuation exposure.

Include-bearing fixtures are NEVER passed to Git. The existing pre-invocation
and network filesystem tripwires fail before any such command/access can run.
"""

from __future__ import annotations

import json
from pathlib import Path

from artifact_io import ArtifactInputError
import check_artifacts
from tests.test_domain_source import DomainFixture, digest
from tests.test_domain_source_fix1 import blocked_git_and_network_files


HEADERS = (b"[include]", b'[includeIf "gitdir:**"]')
ENDPOINT_LINE = b"\tpath = //never-contact.invalid/share/fix2.conf\n"


class CommentContinuationFixTests(DomainFixture):
    def setUp(self):
        super().setUp()
        self.source_config = self.source / ".git/config"
        self.parent_config = self.root / ".git/config"
        self.original_source = self.source_config.read_bytes()
        self.original_parent = self.parent_config.read_bytes()

    def config_bytes(self, suffix, *, newline=b"\n", bom=False, parent=False):
        original = self.original_parent if parent else self.original_source
        raw = (original + suffix).replace(b"\r\n", b"\n").replace(b"\n", newline)
        return (b"\xef\xbb\xbf" if bom else b"") + raw

    def refused(self, raw, *, native=False, code="GIT_CONFIG_INCLUDES_UNSUPPORTED"):
        path = self.parent_config if native else self.source_config
        path.write_bytes(raw)
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            with self.assertRaises(ArtifactInputError) as caught:
                if native:
                    self.tool()._native(self.root, "rev-parse", "--show-toplevel")
                else:
                    check_artifacts._git(self.source, "rev-parse", "--show-toplevel")
        self.assertEqual(code, caught.exception.code)
        self.assertEqual([], attempts, "No affected Git call or UNC filesystem access may be attempted")
        self.assertEqual(before, self.snapshot())
        self.assertNotIn("never-contact.invalid", str(caught.exception))

    def test_i3_hash_comment_backslash_preserves_physical_include_header(self):
        for newline in (b"\n", b"\r\n"):
            for bom in (False, True):
                for header in HEADERS:
                    with self.subTest(newline=newline, bom=bom, header=header):
                        suffix = b"\n# owner comment ending with a backslash\\\n" + header + b"\n" + ENDPOINT_LINE
                        self.refused(self.config_bytes(suffix, newline=newline, bom=bom))

    def test_i3_semicolon_comment_backslash_preserves_physical_include_header(self):
        for newline in (b"\n", b"\r\n"):
            for bom in (False, True):
                for header in HEADERS:
                    with self.subTest(newline=newline, bom=bom, header=header):
                        suffix = b"\n; owner comment ending with a backslash\\\n" + header + b"\n" + ENDPOINT_LINE
                        self.refused(self.config_bytes(suffix, newline=newline, bom=bom))

    def test_i3_comment_backslash_parity_never_continues_a_physical_comment(self):
        for marker in (b"#", b";"):
            for count in (1, 2, 3, 4):
                for newline in (b"\n", b"\r\n"):
                    with self.subTest(marker=marker, count=count, newline=newline):
                        suffix = b"\n" + marker + b" owner comment " + b"\\" * count + b"\n[include]\n" + ENDPOINT_LINE
                        self.refused(self.config_bytes(suffix, newline=newline))

    def test_i3_inline_comment_after_quoted_value_does_not_absorb_the_next_header(self):
        for marker in (b"#", b";"):
            for newline in (b"\n", b"\r\n"):
                with self.subTest(marker=marker, newline=newline):
                    suffix = (b'\n[alias]\n\tnote = "literal # ; text" ' + marker
                              + b" owner comment\\\n[include]\n" + ENDPOINT_LINE)
                    self.refused(self.config_bytes(suffix, newline=newline))

    def test_i3_parent_api_typed_refusal_precedes_every_affected_git_call(self):
        for marker in (b"#", b";"):
            with self.subTest(marker=marker):
                suffix = b"\n" + marker + b" owner comment\\\n[include]\n" + ENDPOINT_LINE
                self.parent_config.write_bytes(self.config_bytes(suffix, parent=True))
                selected = dict(self.declaration, kind="local", path="domain-model/规则.md",
                                baseline=digest((self.source / "domain-model/规则.md").read_bytes()))
                before = self.snapshot()
                with blocked_git_and_network_files() as attempts:
                    result = self.tool().inspect_domain_source(self.root, selected)
                self.assertEqual(("unavailable", 2), (result["status"], result["exit_code"]), result)
                self.assertIn("GIT_CONFIG_INCLUDES_UNSUPPORTED", self.codes(result))
                self.assertEqual([], result["written"])
                self.assertEqual([], attempts)
                self.assertEqual(before, self.snapshot())
                self.assertNotIn("never-contact.invalid", json.dumps(result))

    def test_i3_native_parent_refuses_hidden_include_before_spawn(self):
        for marker in (b"#", b";"):
            for newline in (b"\n", b"\r\n"):
                with self.subTest(marker=marker, newline=newline):
                    suffix = b"\n" + marker + b" comment\\\n" + HEADERS[1] + b"\n" + ENDPOINT_LINE
                    self.refused(self.config_bytes(suffix, newline=newline, bom=True, parent=True), native=True)

    def test_i3_ordinary_comments_and_actual_quoted_literals_are_preserved(self):
        suffix = (b'\n# owner "comment" [include] ending with a backslash\\\n'
                  b'; owner comment [includeIf] ending with a backslash\\\n'
                  b'[alias]\n\tnote = "literal [include] and [includeIf] # ; text"\n')
        self.source_config.write_bytes(self.config_bytes(suffix, bom=True))
        before = self.snapshot()
        with blocked_git_and_network_files() as attempts:
            self.assertIsNone(check_artifacts._git_config_file(self.source_config))
        self.assertEqual([], attempts)
        # This config has NO include declaration or endpoint; the real local
        # Git read is a preservation control, never a network reproduction.
        actual = check_artifacts._git(self.source, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        self.assertEqual(self.source, Path(actual))
        self.assertEqual(before, self.snapshot())

    def test_i3_quoted_lf_crlf_continuation_literal_is_not_an_include(self):
        for newline in (b"\n", b"\r\n"):
            for bom in (False, True):
                with self.subTest(newline=newline, bom=bom):
                    suffix = b'\n[alias]\n\tnote = "literal before \\\n[include] and [includeIf] still quoted"\n'
                    self.source_config.write_bytes(self.config_bytes(suffix, newline=newline, bom=bom))
                    before = self.snapshot()
                    with blocked_git_and_network_files() as attempts:
                        self.assertIsNone(check_artifacts._git_config_file(self.source_config))
                    self.assertEqual([], attempts)
                    # No endpoint/path exists in this safe literal control.
                    self.assertTrue(check_artifacts._git(self.source, "rev-parse", "--show-toplevel").strip())
                    self.assertEqual(before, self.snapshot())

    def test_i3_value_continuation_does_not_change_later_comment_endings(self):
        for marker in (b"#", b";"):
            for newline in (b"\n", b"\r\n"):
                with self.subTest(marker=marker, newline=newline):
                    suffix = (b"\n[alias]\n\tnote = plain\\\ncontinued " + marker
                              + b" owner comment\\\n[include]\n" + ENDPOINT_LINE)
                    self.refused(self.config_bytes(suffix, newline=newline))

    def test_i3_ambiguous_bare_cr_continuation_is_typed_before_git(self):
        for suffix in (b"\n[alias]\n\tnote = unfinished\\\r",
                       b"\n[alias]\n\tnote = unfinished\\\r[include]\n" + ENDPOINT_LINE):
            with self.subTest(suffix=suffix):
                self.refused(self.config_bytes(suffix), code="GIT_CONFIG_UNSAFE")
