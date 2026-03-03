"""Direct tests for next-part terminal render helpers."""

from __future__ import annotations

import desloppify.app.commands.next_parts.render as render_mod


def test_render_terminal_items_group_mode_uses_group_renderer(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake_grouped(items, group) -> None:
        captured["items"] = items
        captured["group"] = group

    monkeypatch.setattr(render_mod, "_render_grouped", _fake_grouped)

    render_mod.render_terminal_items(
        [{"id": "smells::src/a.py::x"}],
        {},
        {},
        group="detector",
        explain=False,
    )

    assert captured["group"] == "detector"


def test_render_terminal_items_cluster_drill_renders_compact_followups(monkeypatch) -> None:
    rendered: list[str] = []
    compact: list[str] = []
    monkeypatch.setattr(render_mod, "colorize", lambda text, _style: text)
    monkeypatch.setattr(
        render_mod,
        "_render_item",
        lambda item, *_args, **_kwargs: rendered.append(str(item.get("id", ""))),
    )
    monkeypatch.setattr(
        render_mod,
        "_render_compact_item",
        lambda item, *_args: compact.append(str(item.get("id", ""))),
    )

    items = [
        {"id": "issue::a", "summary": "A"},
        {"id": "issue::b", "summary": "B"},
    ]
    plan = {"active_cluster": "cluster/a", "clusters": {"cluster/a": {"issue_ids": ["issue::a", "issue::b"]}}}

    render_mod.render_terminal_items(
        items,
        {},
        {},
        group="item",
        explain=False,
        plan=plan,
    )

    assert rendered == ["issue::a"]
    assert compact == ["issue::b"]


def test_render_terminal_items_single_item_prints_next_label(monkeypatch, capsys) -> None:
    monkeypatch.setattr(render_mod, "colorize", lambda text, _style: text)
    monkeypatch.setattr(render_mod, "_render_item", lambda *_args, **_kwargs: None)

    render_mod.render_terminal_items(
        [{"id": "issue::solo", "summary": "Solo"}],
        {},
        {},
        group="item",
        explain=False,
    )

    out = capsys.readouterr().out
    assert "Next item" in out

