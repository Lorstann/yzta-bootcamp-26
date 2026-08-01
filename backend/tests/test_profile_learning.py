"""Silent [PROFIL] learning merge rules."""

from backend.services.chat_service import _parse_learned_profile
from backend.services.profile_service import _merge_string_lists, _normalize_interests


def test_parse_learned_profile():
    text = 'ok [PROFIL]{"sehir":"İzmir","ilce":"Bornova","hobiler":["yürüyüş"],"sarj":[],"program":"Veri Bilimi"}[/PROFIL]'
    data = _parse_learned_profile(text)
    assert data is not None
    assert data["sehir"] == "İzmir"
    assert data["hobiler"] == ["yürüyüş"]
    assert data["program"] == "Veri Bilimi"


def test_parse_learned_profile_missing():
    assert _parse_learned_profile("sadece sohbet") is None


def test_normalize_interests():
    out = _normalize_interests(
        {"hobbies": ["  yürüyüş ", "Kitap", "yürüyüş"], "recharge": ["doğa"], "extra": 1}
    )
    # extra="forbid" is on schema; normalize tolerates dict and drops unknown keys
    assert out is not None
    assert out["hobbies"] == ["yürüyüş", "Kitap"]
    assert out["recharge"] == ["doğa"]


def test_merge_string_lists_dedupes():
    merged = _merge_string_lists(["Yürüyüş"], ["yürüyüş", "Kitap"])
    assert merged == ["Yürüyüş", "Kitap"]
