from __future__ import annotations

from desloppify.languages._framework.base.types import LangSecurityResult
from desloppify.languages.cxx import CxxConfig
from desloppify.languages.cxx.detectors.security import detect_cxx_security


def test_detect_cxx_security_normalizes_findings(tmp_path):
    source = tmp_path / "src" / "unsafe.cpp"
    source.parent.mkdir(parents=True)
    source.write_text(
        '#include <cstring>\n'
        '#include <cstdlib>\n'
        "void copy(char *dst, const char *src) {\n"
        "    std::strcpy(dst, src);\n"
        "    system(src);\n"
        "}\n"
    )

    result = detect_cxx_security([str(source.resolve())], zone_map=None)

    assert isinstance(result, LangSecurityResult)
    assert result.files_scanned == 1
    kinds = {entry["detail"]["kind"] for entry in result.entries}
    assert "unsafe_c_string" in kinds
    assert "command_injection" in kinds


def test_cxx_config_security_hook_returns_lang_result(tmp_path):
    source = tmp_path / "src" / "token.cpp"
    source.parent.mkdir(parents=True)
    source.write_text(
        "#include <cstdlib>\n"
        "int issue(const char* cmd) {\n"
        "    return std::system(cmd);\n"
        "}\n"
    )

    cfg = CxxConfig()
    result = cfg.detect_lang_security_detailed([str(source.resolve())], zone_map=None)

    assert isinstance(result, LangSecurityResult)
    assert result.files_scanned == 1
    assert result.entries
    assert result.entries[0]["detail"]["kind"] == "command_injection"
