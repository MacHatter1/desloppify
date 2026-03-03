"""Direct tests for scan plan reconciliation orchestration."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import desloppify.app.commands.scan.plan_reconcile as reconcile_mod


def _runtime(*, state=None) -> SimpleNamespace:
    return SimpleNamespace(
        state=state or {},
        state_path=Path("/tmp/fake-state.json"),
        config={},
    )


def test_reconcile_plan_post_scan_saves_when_any_step_changes(monkeypatch) -> None:
    saved: list[dict] = []
    monkeypatch.setattr(reconcile_mod, "load_plan", lambda _path=None: {})
    monkeypatch.setattr(reconcile_mod, "_apply_plan_reconciliation", lambda *_a, **_k: False)
    monkeypatch.setattr(reconcile_mod, "_sync_unscored_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_subjective_policy_context", lambda *_a, **_k: (95.0, object(), False)
    )
    monkeypatch.setattr(
        reconcile_mod,
        "_sync_stale_and_log",
        lambda *_a, **_k: True,
    )
    monkeypatch.setattr(reconcile_mod, "_sync_auto_clusters_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(reconcile_mod, "_sync_triage_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_sync_communicate_score_and_log", lambda *_a, **_k: False
    )
    monkeypatch.setattr(reconcile_mod, "_sync_create_plan_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_sync_plan_start_scores_and_log", lambda *_a, **_k: False
    )
    monkeypatch.setattr(reconcile_mod, "save_plan", lambda plan, _path=None: saved.append(plan))

    reconcile_mod.reconcile_plan_post_scan(_runtime())

    assert len(saved) == 1


def test_reconcile_plan_post_scan_does_not_save_when_no_changes(monkeypatch) -> None:
    saved: list[dict] = []
    monkeypatch.setattr(reconcile_mod, "load_plan", lambda _path=None: {})
    monkeypatch.setattr(reconcile_mod, "_apply_plan_reconciliation", lambda *_a, **_k: False)
    monkeypatch.setattr(reconcile_mod, "_sync_unscored_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_subjective_policy_context", lambda *_a, **_k: (95.0, object(), False)
    )
    monkeypatch.setattr(reconcile_mod, "_sync_stale_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(reconcile_mod, "_sync_auto_clusters_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(reconcile_mod, "_sync_triage_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_sync_communicate_score_and_log", lambda *_a, **_k: False
    )
    monkeypatch.setattr(reconcile_mod, "_sync_create_plan_and_log", lambda *_a, **_k: False)
    monkeypatch.setattr(
        reconcile_mod, "_sync_plan_start_scores_and_log", lambda *_a, **_k: False
    )
    monkeypatch.setattr(reconcile_mod, "save_plan", lambda plan, _path=None: saved.append(plan))

    reconcile_mod.reconcile_plan_post_scan(_runtime())

    assert saved == []


def test_reconcile_plan_post_scan_swallows_plan_load_exceptions(monkeypatch) -> None:
    monkeypatch.setattr(reconcile_mod, "load_plan", lambda _path=None: (_ for _ in ()).throw(OSError("boom")))

    # No exception should escape; reconciliation is best-effort.
    reconcile_mod.reconcile_plan_post_scan(_runtime())

