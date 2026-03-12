from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from desloppify.languages._framework.runtime import make_lang_run
from desloppify.languages.cxx import CxxConfig
from desloppify.languages.cxx.phases import phase_coupling

_FIXTURES = Path(__file__).parent / "fixtures"


def _run_scan_fixture(name: str) -> SimpleNamespace:
    root = _FIXTURES / name
    lang = make_lang_run(CxxConfig())
    issues, potentials = phase_coupling(root, lang)
    return SimpleNamespace(
        root=root,
        dep_graph=lang.dep_graph or {},
        issues=issues,
        potentials=potentials,
    )


def test_cmake_fixture_produces_dep_graph_and_cycles():
    result = _run_scan_fixture("cmake_sample")

    assert result.dep_graph
    assert any(issue["detector"] == "cycles" for issue in result.issues)
    assert result.potentials["cycles"] > 0


def test_makefile_fixture_uses_best_effort_fallback():
    result = _run_scan_fixture("makefile_sample")
    main = str((result.root / "src" / "main.cpp").resolve())
    header = str((result.root / "include" / "local.hpp").resolve())

    assert result.dep_graph
    assert not (result.root / "compile_commands.json").exists()
    assert header in result.dep_graph[main]["imports"]
