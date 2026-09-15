"""Safety and evaluation contracts for the local load-validation harness."""

from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.run_load_validation import (
    LoadProfile,
    RequestSample,
    evaluate_samples,
    validate_target_url,
)

BASE_PROFILE = {
    "name": "unit-smoke",
    "evidence_tier": "local_smoke",
    "duration_seconds": 5,
    "concurrency": 2,
    "target_requests_per_second": 10,
    "request_timeout_seconds": 2,
    "dataset": {"people": 4, "events": 2},
    "operations": {"health": 1, "people": 2},
    "thresholds": {
        "minimum_requests": 4,
        "maximum_error_rate": 0,
        "maximum_p95_ms": 500,
        "minimum_throughput_rps": 1,
    },
}


def test_profile_requires_bounded_supported_workload() -> None:
    profile = LoadProfile.from_mapping(BASE_PROFILE)

    assert profile.name == "unit-smoke"
    assert profile.operation_names == ("health", "people")
    assert profile.total_weight == 3

    invalid = deepcopy(BASE_PROFILE)
    invalid["operations"] = {"delete_everything": 1}
    with pytest.raises(ValueError, match="Unsupported load operation"):
        LoadProfile.from_mapping(invalid)

    invalid = deepcopy(BASE_PROFILE)
    invalid["target_requests_per_second"] = 0
    with pytest.raises(ValueError, match="target_requests_per_second"):
        LoadProfile.from_mapping(invalid)

    invalid = deepcopy(BASE_PROFILE)
    invalid["duration_seconds"] = 3601
    with pytest.raises(ValueError, match="duration_seconds"):
        LoadProfile.from_mapping(invalid)

    invalid = deepcopy(BASE_PROFILE)
    invalid["target_requests_per_second"] = 1001
    with pytest.raises(ValueError, match="target_requests_per_second"):
        LoadProfile.from_mapping(invalid)

    invalid = deepcopy(BASE_PROFILE)
    invalid["request_timeout_seconds"] = 121
    with pytest.raises(ValueError, match="request_timeout_seconds"):
        LoadProfile.from_mapping(invalid)


def test_release_profile_requires_an_owner_approval_reference() -> None:
    candidate = deepcopy(BASE_PROFILE)
    candidate["evidence_tier"] = "release_candidate"
    candidate["approval_reference"] = ""

    with pytest.raises(ValueError, match="approval_reference"):
        LoadProfile.from_mapping(candidate)

    candidate["approval_reference"] = "https://github.com/tomqwu/SignUpFlow/issues/271"
    assert LoadProfile.from_mapping(candidate).evidence_tier == "release_candidate"


def test_target_defaults_to_owned_loopback_and_has_no_ambiguous_path() -> None:
    assert validate_target_url("http://127.0.0.1:8123") == "http://127.0.0.1:8123"
    assert validate_target_url("http://localhost:8123/") == "http://localhost:8123"

    with pytest.raises(ValueError, match="loopback"):
        validate_target_url("https://staging.example.com")
    with pytest.raises(ValueError, match="origin only"):
        validate_target_url("http://127.0.0.1:8123/api/v1")
    with pytest.raises(ValueError, match="credentials"):
        validate_target_url("http://user:pass@127.0.0.1:8123")
    with pytest.raises(ValueError, match="HTTPS"):
        validate_target_url("http://staging.example.com", allow_authorized_remote=True)

    assert (
        validate_target_url("https://staging.example.com", allow_authorized_remote=True)
        == "https://staging.example.com"
    )


def test_threshold_evaluation_reports_each_failure_without_hiding_errors() -> None:
    profile = LoadProfile.from_mapping(BASE_PROFILE)
    samples = [
        RequestSample("health", 10, 200),
        RequestSample("people", 20, 200),
        RequestSample("people", 900, 500, "unexpected status 500"),
        RequestSample("health", 15, 200),
    ]

    result = evaluate_samples(profile, samples, duration_seconds=1)

    assert result["outcome"] == "failed"
    assert result["request_count"] == 4
    assert result["error_count"] == 1
    assert result["operations"]["people"]["error_count"] == 1
    assert any("error rate" in failure for failure in result["failures"])
    assert any("p95" in failure for failure in result["failures"])


def test_threshold_evaluation_passes_only_when_every_limit_is_met() -> None:
    profile = LoadProfile.from_mapping(BASE_PROFILE)
    samples = [
        RequestSample("health", 10, 200),
        RequestSample("people", 20, 200),
        RequestSample("people", 30, 200),
        RequestSample("health", 15, 200),
    ]

    result = evaluate_samples(profile, samples, duration_seconds=1)

    assert result["outcome"] == "passed"
    assert result["failures"] == []
    assert result["throughput_rps"] == 4
