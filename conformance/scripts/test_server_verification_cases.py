#!/usr/bin/env python3
"""Tests for server verification fixture validation."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import server_verify_runner


def write_cases(directory: str, document: Any) -> Path:
    path = Path(directory) / "cases.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


class LoadCasesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = server_verify_runner.load_cases()

    def test_checked_in_fixture_is_valid(self) -> None:
        self.assertGreater(len(self.cases), 0)
        for case in self.cases:
            self.assertIn("input", case)
            self.assertIn("expected", case)

    def test_empty_case_list_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_cases(directory, {"cases": []})

            with self.assertRaises(ValueError) as context:
                server_verify_runner.load_cases(path)

        self.assertIn("schema validation", str(context.exception))

    def test_case_without_expected_result_is_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        case.pop("expected")
        with tempfile.TemporaryDirectory() as directory:
            path = write_cases(directory, {"cases": [case]})

            with self.assertRaises(ValueError) as context:
                server_verify_runner.load_cases(path)

        self.assertIn("expected", str(context.exception))

    def test_unknown_case_property_is_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        case["expcted"] = case["expected"]
        with tempfile.TemporaryDirectory() as directory:
            path = write_cases(directory, {"cases": [case]})

            with self.assertRaises(ValueError):
                server_verify_runner.load_cases(path)

    def test_result_shape_is_enforced(self) -> None:
        case = copy.deepcopy(self.cases[0])
        case["expected"] = {"ok": True}
        with tempfile.TemporaryDirectory() as directory:
            path = write_cases(directory, {"cases": [case]})

            with self.assertRaises(ValueError):
                server_verify_runner.load_cases(path)

    def test_duplicate_case_names_are_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        with tempfile.TemporaryDirectory() as directory:
            path = write_cases(directory, {"cases": [case, copy.deepcopy(case)]})

            with self.assertRaises(ValueError) as context:
                server_verify_runner.load_cases(path)

        self.assertIn("duplicate", str(context.exception))


if __name__ == "__main__":
    unittest.main()
