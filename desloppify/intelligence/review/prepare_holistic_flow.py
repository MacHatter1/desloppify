"""Holistic review preparation workflow helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from desloppify.base.discovery.file_paths import rel
from desloppify.intelligence.review._context.models import HolisticContext
from desloppify.intelligence.review._prepare.helpers import HOLISTIC_WORKFLOW
from desloppify.intelligence.review._prepare.issue_history import (
    ReviewHistoryOptions,
    build_batch_issue_focus,
    build_issue_history_context,
)

_NON_PRODUCTION_ZONES = frozenset({"test", "config", "generated", "vendor"})


def collect_allowed_review_files(
    files: list[str],
    lang: object,
    *,
    base_path: Path | None = None,
) -> set[str]:
    """Return relative production-file paths allowed for holistic review batches."""
    allowed: set[str] = set()
    zone_map = getattr(lang, "zone_map", None)
    resolved_base = base_path.resolve() if isinstance(base_path, Path) else None
    for filepath in files:
        if not isinstance(filepath, str):
            continue
        normalized = filepath.strip().replace("\\", "/")
        if not normalized:
            continue
        if zone_map is not None:
            try:
                zone = zone_map.get(filepath)
                zone_value = getattr(zone, "value", str(zone))
            except (AttributeError, KeyError, TypeError, ValueError):
                zone_value = "production"
            if zone_value in _NON_PRODUCTION_ZONES:
                continue
        allowed.add(normalized)
        allowed.add(rel(filepath))
        if resolved_base is not None:
            try:
                allowed.add(Path(filepath).resolve().relative_to(resolved_base).as_posix())
            except ValueError:
                pass
    return allowed


def file_in_allowed_scope(filepath: object, allowed_files: set[str]) -> bool:
    """True when *filepath* resolves to a currently in-scope review file."""
    if not isinstance(filepath, str):
        return False
    normalized = filepath.strip().replace("\\", "/")
    if not normalized:
        return False
    if normalized in allowed_files:
        return True
    return rel(filepath) in allowed_files


def filter_issue_focus_to_scope(
    issue_focus: object,
    allowed_files: set[str],
) -> dict[str, object] | None:
    """Drop out-of-scope related_files from historical issue focus payload."""
    if not isinstance(issue_focus, dict):
        return None
    issues_raw = issue_focus.get("issues", [])
    issues: list[dict[str, object]] = []
    if isinstance(issues_raw, list):
        for raw_issue in issues_raw:
            if not isinstance(raw_issue, dict):
                continue
            issue = dict(raw_issue)
            related_raw = issue.get("related_files", [])
            if isinstance(related_raw, list):
                issue["related_files"] = [
                    path for path in related_raw if file_in_allowed_scope(path, allowed_files)
                ]
            issues.append(issue)
    scoped = dict(issue_focus)
    scoped["issues"] = issues
    scoped["selected_count"] = len(issues)
    return scoped


def filter_batches_to_file_scope(
    batches: list[dict[str, Any]],
    *,
    allowed_files: set[str],
) -> list[dict[str, Any]]:
    """Strip out-of-scope files/signals from review batches."""
    if not allowed_files:
        return []

    scoped_batches: list[dict[str, Any]] = []
    for raw_batch in batches:
        if not isinstance(raw_batch, dict):
            continue
        batch = dict(raw_batch)
        files_to_read = batch.get("files_to_read", [])
        if isinstance(files_to_read, list):
            scoped_files = [
                filepath
                for filepath in files_to_read
                if file_in_allowed_scope(filepath, allowed_files)
            ]
        else:
            scoped_files = []
        batch["files_to_read"] = scoped_files

        concern_signals = batch.get("concern_signals", [])
        if isinstance(concern_signals, list):
            batch["concern_signals"] = [
                signal
                for signal in concern_signals
                if isinstance(signal, dict)
                and file_in_allowed_scope(signal.get("file", ""), allowed_files)
            ]
            if "concern_signal_count" in batch:
                batch["concern_signal_count"] = len(batch["concern_signals"])

        issue_focus = filter_issue_focus_to_scope(
            batch.get("historical_issue_focus"),
            allowed_files,
        )
        if issue_focus is not None:
            batch["historical_issue_focus"] = issue_focus

        has_seed_files = bool(batch["files_to_read"])
        has_signals = bool(batch.get("concern_signals"))
        if has_seed_files or has_signals:
            scoped_batches.append(batch)
    return scoped_batches


def prepare_holistic_review_payload(
    path: Path,
    lang: object,
    state: dict,
    options,
    *,
    is_file_cache_enabled_fn,
    enable_file_cache_fn,
    disable_file_cache_fn,
    build_holistic_context_fn,
    build_review_context_fn,
    load_dimensions_for_lang_fn,
    resolve_dimensions_fn,
    get_lang_guidance_fn,
    build_investigation_batches_fn,
    batch_concerns_fn,
    filter_batches_to_dimensions_fn,
    append_full_sweep_batch_fn,
    serialize_context_fn,
    log_best_effort_failure_fn,
    logger,
) -> dict[str, object]:
    """Prepare holistic review payload with injected dependencies for patchability."""
    resolved_options = options
    all_files = (
        resolved_options.files
        if resolved_options.files is not None
        else (lang.file_finder(path) if lang.file_finder else [])
    )
    allowed_review_files = collect_allowed_review_files(
        all_files,
        lang,
        base_path=path,
    )

    already_cached = is_file_cache_enabled_fn()
    if not already_cached:
        enable_file_cache_fn()
    try:
        context = HolisticContext.from_raw(
            build_holistic_context_fn(path, lang, state, files=all_files)
        )
        review_ctx = build_review_context_fn(path, lang, state, files=all_files)
    finally:
        if not already_cached:
            disable_file_cache_fn()

    default_dims, holistic_prompts, system_prompt = load_dimensions_for_lang_fn(lang.name)
    _, per_file_prompts, _ = load_dimensions_for_lang_fn(lang.name)
    dims = resolve_dimensions_fn(
        cli_dimensions=resolved_options.dimensions,
        default_dimensions=default_dims,
    )
    lang_guide = get_lang_guidance_fn(lang.name)
    valid_dims = set(holistic_prompts) | set(per_file_prompts)
    invalid_requested = [
        dim for dim in (resolved_options.dimensions or []) if dim not in valid_dims
    ]
    invalid_default = [dim for dim in default_dims if dim not in valid_dims]
    batches = build_investigation_batches_fn(
        context,
        lang,
        repo_root=path,
        max_files_per_batch=resolved_options.max_files_per_batch,
    )

    try:
        from desloppify.engine.concerns import generate_concerns

        concerns = generate_concerns(state)
        concerns = [
            concern
            for concern in concerns
            if file_in_allowed_scope(getattr(concern, "file", ""), allowed_review_files)
        ]
        concerns_batch = batch_concerns_fn(
            concerns,
            max_files=resolved_options.max_files_per_batch,
            active_dimensions=dims,
        )
        if concerns_batch:
            batches.append(concerns_batch)
    except (ImportError, AttributeError, TypeError, ValueError) as exc:
        log_best_effort_failure_fn(logger, "generate review concern batch", exc)

    batches = filter_batches_to_dimensions_fn(
        batches,
        dims,
        fallback_max_files=resolved_options.max_files_per_batch,
    )
    include_full_sweep = bool(resolved_options.include_full_sweep)
    if resolved_options.dimensions:
        include_full_sweep = False
    if include_full_sweep:
        append_full_sweep_batch_fn(
            batches=batches,
            dims=dims,
            all_files=all_files,
            lang=lang,
            max_files=resolved_options.max_files_per_batch,
        )
    batches = filter_batches_to_file_scope(
        batches,
        allowed_files=allowed_review_files,
    )

    selected_prompts: dict[str, dict[str, object]] = {}
    for dim in dims:
        prompt = holistic_prompts.get(dim)
        if prompt is None:
            prompt = per_file_prompts.get(dim)
        if prompt is None:
            continue
        selected_prompts[dim] = prompt

    payload: dict[str, Any] = {
        "command": "review",
        "mode": "holistic",
        "language": lang.name,
        "dimensions": dims,
        "dimension_prompts": selected_prompts,
        "lang_guidance": lang_guide,
        "holistic_context": context.to_dict(),
        "review_context": serialize_context_fn(review_ctx),
        "system_prompt": system_prompt,
        "total_files": context.codebase_stats.get("total_files", 0),
        "workflow": HOLISTIC_WORKFLOW,
        "invalid_dimensions": {
            "requested": invalid_requested,
            "default": invalid_default,
        },
    }
    if resolved_options.include_issue_history:
        history_payload = build_issue_history_context(
            state,
            options=ReviewHistoryOptions(
                max_issues=resolved_options.issue_history_max_issues,
            ),
        )
        payload["historical_review_issues"] = history_payload
        for batch in batches:
            if not isinstance(batch, dict):
                continue
            batch_dims = batch.get("dimensions", [])
            batch["historical_issue_focus"] = build_batch_issue_focus(
                history_payload,
                dimensions=batch_dims,
                max_items=resolved_options.issue_history_max_batch_items,
            )
        batches = filter_batches_to_file_scope(
            batches,
            allowed_files=allowed_review_files,
        )
    payload["investigation_batches"] = batches
    return payload


__all__ = ["prepare_holistic_review_payload"]
