"""Public plan operations API re-export shim."""

from __future__ import annotations

from desloppify.engine._plan.operations_cluster import (
    add_to_cluster,
    create_cluster,
    delete_cluster,
    merge_clusters,
    move_cluster,
    remove_from_cluster,
)
from desloppify.engine._plan.operations_lifecycle import (
    clear_focus,
    purge_ids,
    reset_plan,
    set_focus,
)
from desloppify.engine._plan.operations_meta import (
    _get_log_cap as _meta_get_log_cap,
    annotate_issue,
    append_log_entry as _append_log_entry,
    describe_issue,
)
from desloppify.engine._plan.operations_queue import move_items
from desloppify.engine._plan.operations_skip import (
    resurface_stale_skips,
    skip_items,
    unskip_items,
)


def _get_log_cap() -> int:
    """Compatibility bridge for tests monkeypatching operations._get_log_cap."""
    return _meta_get_log_cap()


def append_log_entry(*args, **kwargs) -> None:
    """Compatibility wrapper for operations_meta.append_log_entry.

    If callers monkeypatch ``operations._get_log_cap``, reflect it into
    ``operations_meta`` before dispatching.
    """
    from desloppify.engine._plan import operations_meta as _meta

    patched = globals().get("_get_log_cap")
    if callable(patched):
        _meta._get_log_cap = patched
    else:
        _meta._get_log_cap = _meta_get_log_cap
    _append_log_entry(*args, **kwargs)


__all__ = [
    "add_to_cluster",
    "annotate_issue",
    "append_log_entry",
    "clear_focus",
    "create_cluster",
    "delete_cluster",
    "describe_issue",
    "merge_clusters",
    "move_cluster",
    "move_items",
    "purge_ids",
    "remove_from_cluster",
    "reset_plan",
    "resurface_stale_skips",
    "set_focus",
    "skip_items",
    "unskip_items",
]
