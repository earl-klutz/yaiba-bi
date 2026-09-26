"""Small CLI reporting and fixed-baseline checks shared by the two scripts."""
from __future__ import annotations

import ast
from collections import Counter
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
BASELINE = json.loads(Path(__file__).with_name("baseline.json").read_text(encoding="utf-8"))


def same(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, (tuple, list)):
        return len(actual) == len(expected) and all(same(a, b) for a, b in zip(actual, expected))
    return actual == expected


class Report:
    def __init__(self, prefix):
        self.prefix = prefix
        self.counts = Counter()
        self.blocked = False

    def emit(self, case, status, expected, actual, reason="", required=True):
        self.counts[status] += 1
        self.blocked |= status == "SKIP" and required
        print(f"{self.prefix}-{case} {status} expected={expected!r} actual={actual!r} reason={reason}")

    def check(self, case, condition, expected, actual):
        self.emit(case, "PASS" if condition else "FAIL", expected, actual)

    def run(self, case, expected, action):
        try:
            actual = action()
            self.check(case, same(actual, expected), expected, actual)
        except Exception as exc:
            self.emit(case, "FAIL", expected, f"{type(exc).__name__}: {exc}")

    def finish(self):
        code = 1 if self.counts["FAIL"] else 2 if self.blocked else 0
        print(f"{self.prefix}-SUMMARY PASS={self.counts['PASS']} FAIL={self.counts['FAIL']} "
              f"SKIP={self.counts['SKIP']} exit={code}")
        return code


def load_target(name, report):
    sys.path.insert(0, str(SRC))
    os.environ["MPLBACKEND"] = "Agg"
    # core/__init__.py eagerly imports these existing project dependencies.
    missing = [dep for dep in ("numpy", "pandas", "matplotlib", "tqdm", "yaiba", "scipy")
               if importlib.util.find_spec(dep) is None]
    if missing:
        for case in ("IMPORT", "DEFAULT", "BASELINE", "SMOKE"):
            report.emit(case, "SKIP", "installed dependencies", missing, "required dependency unavailable")
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        target = importlib.import_module(f"yaiba_bi.core.{name}")
        expected_path = (SRC / f"yaiba_bi/core/{name}.py").resolve()
        actual_path = Path(target.__file__).resolve()
        if actual_path != expected_path:
            report.emit("IMPORT", "FAIL", str(expected_path), str(actual_path))
            return None
        report.emit("IMPORT", "PASS", str(expected_path), str(actual_path))
        return target
    except Exception as exc:
        # Missing names, circular imports and transitive import failures are not
        # automatically reclassified as missing optional dependencies.
        report.emit("IMPORT", "FAIL", "local module imports", f"{type(exc).__name__}: {exc}")
        return None


def references(name, report):
    tree = ast.parse((SRC / f"yaiba_bi/core/{name}.py").read_text(encoding="utf-8"))
    found = Counter()

    def visit(node, scope="module"):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            scope += "." + node.name
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id in ("columns", "defaults", "errors", "layouts", "paths")):
            found[scope + "|" + node.value.id + "." + node.attr] += 1
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree)
    for site, count in BASELINE[name]["references"].items():
        report.check("REF-" + site, found[site] == count, count, found[site])
    imports = {alias.name for node in tree.body if isinstance(node, ast.ImportFrom)
               and node.level == 1 and node.module == "config" for alias in node.names}
    report.check("REF-IMPORT", set(("columns", "defaults", "errors", "layouts", "paths", "TIMEZONE_JST")) <= imports,
                 "config modules and timezone", sorted(imports))
    tz_name = "TZ_JST" if name == "movie" else "JST"
    tz_values = [n.value for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == tz_name for t in n.targets)]
    report.check("REF-TIMEZONE", len(tz_values) == 1 and isinstance(tz_values[0], ast.Name)
                 and tz_values[0].id == "TIMEZONE_JST", "TIMEZONE_JST", [ast.dump(v) for v in tz_values])


def defaults_and_baseline(name, target, report):
    for key, literal in BASELINE[name]["defaults"].items():
        cls, field = key.split(".")
        expected = ast.literal_eval(literal)
        actual = getattr(getattr(target, cls)(), field)
        report.check("DEFAULT-" + key, same(actual, expected), expected, actual)
    for ref, literal in BASELINE[name]["values"].items():
        mod, key = ref.split(".")
        config = importlib.import_module("yaiba_bi.core.config." + mod)
        expected_path = (SRC / f"yaiba_bi/core/config/{mod}.py").resolve()
        expected = ast.literal_eval(literal)
        actual = getattr(config, key)
        report.check("BASELINE-" + ref, Path(config.__file__).resolve() == expected_path
                     and same(actual, expected), (literal, type(expected).__name__), (repr(actual), type(actual).__name__))
    tz = getattr(target, "TZ_JST" if name == "movie" else "JST")
    report.check("BASELINE-TIMEZONE", type(tz) is ZoneInfo and tz.key == "Asia/Tokyo", "ZoneInfo Asia/Tokyo", repr(tz))
    if name == "histogram":
        report.check("BASELINE-RETAINED-ERRORS", same(target.EC_STATS_EMPTY, -2302)
                     and same(target.EC_STATS_UNKNOWN, -2399), (-2302, -2399),
                     (target.EC_STATS_EMPTY, target.EC_STATS_UNKNOWN))


def exception_result(action):
    try:
        action()
    except Exception as exc:
        return type(exc).__name__, getattr(exc, "code", None)
    return "no exception", None
