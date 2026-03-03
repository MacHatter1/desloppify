"""Direct tests for plan commit-log command handlers."""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import desloppify.app.commands.plan.commit_log_handlers as commit_log_mod


def test_commit_log_dispatch_warns_when_disabled(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        commit_log_mod, "load_config", lambda: {"commit_tracking_enabled": False}
    )
    monkeypatch.setattr(commit_log_mod, "colorize", lambda text, _style: text)

    commit_log_mod.cmd_commit_log_dispatch(argparse.Namespace(commit_log_action=None))

    out = capsys.readouterr().out
    assert "Commit tracking is disabled" in out


def test_commit_log_dispatch_without_action_routes_to_status(monkeypatch) -> None:
    called: dict[str, object] = {}
    plan = {"queue_order": [], "commit_log": []}
    monkeypatch.setattr(
        commit_log_mod, "load_config", lambda: {"commit_tracking_enabled": True}
    )
    monkeypatch.setattr(commit_log_mod, "load_plan", lambda: plan)
    monkeypatch.setattr(
        commit_log_mod, "_cmd_commit_log_status", lambda incoming: called.setdefault("plan", incoming)
    )

    commit_log_mod.cmd_commit_log_dispatch(argparse.Namespace(commit_log_action=None))

    assert called["plan"] is plan


def test_cmd_commit_log_record_filters_and_saves(monkeypatch, capsys) -> None:
    plan = {"uncommitted_issues": ["issue::a", "issue::b"], "commit_log": []}
    saved: list[dict] = []
    appended: list[tuple[str, dict]] = []

    monkeypatch.setattr(commit_log_mod, "colorize", lambda text, _style: text)
    monkeypatch.setattr(
        commit_log_mod,
        "detect_git_context",
        lambda: SimpleNamespace(
            available=True,
            branch="main",
            head_sha="abcdef123456",
            has_uncommitted=False,
        ),
    )
    monkeypatch.setattr(
        commit_log_mod,
        "filter_issue_ids_by_pattern",
        lambda issue_ids, patterns: [issue_ids[-1]],
    )
    monkeypatch.setattr(
        commit_log_mod,
        "record_commit",
        lambda *_args, **_kwargs: {
            "sha": "abcdef123456",
            "branch": "main",
            "issue_ids": ["issue::b"],
        },
    )
    monkeypatch.setattr(
        commit_log_mod,
        "append_log_entry",
        lambda _plan, action, **kwargs: appended.append((action, kwargs)),
    )
    monkeypatch.setattr(commit_log_mod, "save_plan", lambda incoming: saved.append(incoming))
    monkeypatch.setattr(commit_log_mod, "load_config", lambda: {"commit_pr": 0})

    args = argparse.Namespace(
        sha=None,
        branch=None,
        note="recorded",
        only=["*issue::b*"],
    )
    commit_log_mod._cmd_commit_log_record(args, plan)

    out = capsys.readouterr().out
    assert "Recorded commit abcdef123456 with 1 issue(s)." in out
    assert saved and saved[0] is plan
    assert appended and appended[0][0] == "commit_record"

