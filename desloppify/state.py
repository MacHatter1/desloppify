"""Public state API facade.

State internals live in `desloppify.engine._state`; this module exposes the
stable, non-private API used by commands, review flows, and language phases.
"""

from typing import NamedTuple

from desloppify.engine._state.filtering import (
    add_ignore,
    issue_in_scan_scope,
    is_ignored,
    make_issue,
    open_scope_breakdown,
    path_scoped_issues,
    remove_ignored_issues,
)
from desloppify.engine._state.merge import (
    MergeScanOptions,
    find_suspect_detectors,
    merge_scan,
    upsert_issues,
)
from desloppify.engine._state.noise import (
    DEFAULT_ISSUE_NOISE_BUDGET,
    DEFAULT_ISSUE_NOISE_GLOBAL_BUDGET,
    apply_issue_noise_budget,
    resolve_issue_noise_budget,
    resolve_issue_noise_global_budget,
    resolve_issue_noise_settings,
)
from desloppify.engine._state.persistence import load_state, save_state
from desloppify.engine._state.resolution import (
    coerce_assessment_score,
    match_issues,
    resolve_issues,
)
from desloppify.engine._state.schema_scores import (
    _get_objective_score,
    _get_overall_score,
    _get_strict_score,
    _get_verified_strict_score,
)
from desloppify.engine._state.schema import (
    CURRENT_VERSION,
    STATE_DIR,
    STATE_FILE,
    ConcernDismissal,
    DimensionScore,
    Issue,
    StateModel,
    StateStats,
    SubjectiveAssessment,
    SubjectiveIntegrity,
    empty_state,
    ensure_state_defaults,
    json_default,
    migrate_state_keys,
    utc_now,
    validate_state_invariants,
)
from desloppify.engine._state.scoring import (
    suppression_metrics,
)


class ScoreSnapshot(NamedTuple):
    """All four canonical scores from a single state dict."""

    overall: float | None
    objective: float | None
    strict: float | None
    verified: float | None


def score_snapshot(state: StateModel) -> ScoreSnapshot:
    """Load all four canonical scores from *state* in one call."""
    return ScoreSnapshot(
        overall=_get_overall_score(state),
        objective=_get_objective_score(state),
        strict=_get_strict_score(state),
        verified=_get_verified_strict_score(state),
    )


# Backward-compatible wrappers; prefer ``score_snapshot(state)`` for new code.
def get_overall_score(state: StateModel) -> float | None:
    return score_snapshot(state).overall


def get_objective_score(state: StateModel) -> float | None:
    return score_snapshot(state).objective


def get_strict_score(state: StateModel) -> float | None:
    return score_snapshot(state).strict


def get_verified_strict_score(state: StateModel) -> float | None:
    return score_snapshot(state).verified


__all__ = [
    # Types
    "ConcernDismissal",
    "DimensionScore",
    "Issue",
    "MergeScanOptions",
    "ScoreSnapshot",
    "StateModel",
    "StateStats",
    "SubjectiveAssessment",
    "SubjectiveIntegrity",
    # Constants
    "CURRENT_VERSION",
    "DEFAULT_ISSUE_NOISE_BUDGET",
    "DEFAULT_ISSUE_NOISE_GLOBAL_BUDGET",
    "STATE_DIR",
    "STATE_FILE",
    # Functions
    "add_ignore",
    "apply_issue_noise_budget",
    "coerce_assessment_score",
    "empty_state",
    "ensure_state_defaults",
    "find_suspect_detectors",
    "issue_in_scan_scope",
    "open_scope_breakdown",
    "is_ignored",
    "json_default",
    "load_state",
    "make_issue",
    "match_issues",
    "merge_scan",
    "path_scoped_issues",
    "remove_ignored_issues",
    "resolve_issue_noise_budget",
    "resolve_issue_noise_global_budget",
    "resolve_issue_noise_settings",
    "resolve_issues",
    "save_state",
    "score_snapshot",
    "suppression_metrics",
    "upsert_issues",
    "utc_now",
    "validate_state_invariants",
    "migrate_state_keys",
]
