"""Mobile validation stays local and retains the test command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.mobile_codegen import (
    CodegenError,
    diff_generated_trees,
    normalize_generated_text,
    prepare_generator_schema,
    resolve_tool,
)

WF = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "mobile-ci.yml"


def test_mobile_validation_is_local():
    assert not WF.exists(), "Mobile CI must not be restored"
    txt = (WF.parents[2] / "mobile/README.md").read_text()
    assert "flutter pub get" in txt
    # Info-level lints must not fail the build (9 known infos in mobile/).
    assert "flutter analyze --no-fatal-infos" in txt
    assert "flutter test" in txt
    assert "$(FLUTTER) test" in (WF.parents[2] / "Makefile").read_text()
    assert "no CI checks" in txt


def test_mobile_codegen_preserves_strict_contract_without_broken_aliases():
    makefile = (WF.parents[2] / "Makefile").read_text()

    assert "mobile-codegen-preflight" in makefile
    assert "mobile-codegen-check" in makefile
    assert "scripts/mobile_codegen.py" in makefile
    assert "test-mobile-generated:" in makefile
    assert "analyze --no-fatal-warnings" in makefile
    assert "/Users/tomwu/Projects/flutter" not in makefile


def test_codegen_prepares_only_the_generator_compatibility_copy(tmp_path: Path):
    source = tmp_path / "openapi.json"
    output = tmp_path / "generator.json"
    schema = {
        "openapi": "3.1.0",
        "components": {
            "schemas": {
                "SignupRequest": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"name": {"type": "string"}},
                },
                "Other": {"type": "object", "additionalProperties": False},
            }
        },
    }
    source.write_text(json.dumps(schema), encoding="utf-8")

    prepare_generator_schema(source, output)

    prepared = json.loads(output.read_text(encoding="utf-8"))
    assert "additionalProperties" not in prepared["components"]["schemas"]["SignupRequest"]
    assert prepared["components"]["schemas"]["Other"]["additionalProperties"] is False
    assert json.loads(source.read_text(encoding="utf-8")) == schema


def test_codegen_tree_comparison_is_deterministic_and_ignores_tool_caches(tmp_path: Path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    (left / "lib").mkdir(parents=True)
    (right / "lib").mkdir(parents=True)
    (left / "lib" / "client.dart").write_text("same\n", encoding="utf-8")
    (right / "lib" / "client.dart").write_text("same\n", encoding="utf-8")
    (left / ".dart_tool").mkdir()
    (right / ".dart_tool").mkdir()
    (left / ".dart_tool" / "state").write_text("left", encoding="utf-8")
    (right / ".dart_tool" / "state").write_text("right", encoding="utf-8")

    assert diff_generated_trees(left, right) == []

    (right / "lib" / "client.dart").write_text("changed\n", encoding="utf-8")
    assert diff_generated_trees(left, right) == ["changed: lib/client.dart"]


def test_codegen_normalizes_text_without_touching_binary_files(tmp_path: Path):
    generated = tmp_path / "generated"
    generated.mkdir()
    text_file = generated / "client.dart"
    binary_file = generated / "logo.png"
    text_file.write_text("first  \nsecond\t\n\n", encoding="utf-8")
    binary_file.write_bytes(b"\xff\x00\x01")

    normalize_generated_text(generated)

    assert text_file.read_text(encoding="utf-8") == "first\nsecond\n"
    assert binary_file.read_bytes() == b"\xff\x00\x01"


def test_codegen_missing_tool_reports_the_override_name():
    with pytest.raises(CodegenError, match=r"Flutter executable not found.*FLUTTER"):
        resolve_tool(
            "Flutter",
            "FLUTTER",
            environ={},
            candidates=(),
            which=lambda _name: None,
        )


def test_ios_project_and_pods_share_the_supported_deployment_target():
    root = WF.parents[2]
    podfile = (root / "mobile/ios/Podfile").read_text()
    project = (root / "mobile/ios/Runner.xcodeproj/project.pbxproj").read_text()

    assert "platform :ios, '15.0'" in podfile
    assert "config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '15.0'" in podfile
    assert "IPHONEOS_DEPLOYMENT_TARGET = 13.0" not in project
    assert project.count("IPHONEOS_DEPLOYMENT_TARGET = 15.0") == 3


def test_mobile_integration_runner_executes_device_files_sequentially():
    runner = (WF.parents[2] / "mobile/scripts/run_integration_tests.sh").read_text()

    assert 'for test_file in "${TEST_FILES[@]}"' in runner
    assert '"$FLUTTER" test "$test_file" -d "$TARGET_DEVICE"' in runner
    assert 'exec flutter test "$TEST_TARGET"' not in runner
