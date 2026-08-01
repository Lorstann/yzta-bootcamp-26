"""Tests for stream sanitizer and DURUM state parsing."""

from backend.services.chat_service import StreamSanitizer, parse_state


def test_sanitizer_strips_complete_blocks():
    s = StreamSanitizer()
    out = s.feed(
        "Merhaba!\n[DURUM]{\"enerji\":4}[/DURUM]\n"
        "[GOREVLER]\n- görev 1\n[/GOREVLER]"
    )
    out += s.flush()
    assert "[DURUM]" not in out
    assert "[GOREVLER]" not in out
    assert "Merhaba!" in out
    assert "görev" not in out


def test_sanitizer_handles_split_tags():
    s = StreamSanitizer()
    parts = [
        "Anladım. ",
        "[DU",
        "RUM]{\"enerji\":5,\"motivasyon\":4}[/DUR",
        "UM]\nKalan metin.",
    ]
    out = "".join(s.feed(p) for p in parts) + s.flush()
    assert "[DURUM]" not in out
    assert "Anladım." in out
    assert "Kalan metin." in out
    assert "enerji" not in out


def test_sanitizer_raw_preserves_hidden():
    s = StreamSanitizer()
    s.feed("Hi [DURUM]{\"enerji\":3}[/DURUM]")
    s.flush()
    assert "[DURUM]" in s.raw
    assert "enerji" in s.raw


def test_parse_state_valid():
    text = (
        'Selam\n[DURUM]{"enerji":4,"motivasyon":3,'
        '"engel":"React","yuk":"yuksek","hazir":false}[/DURUM]'
    )
    state = parse_state(text)
    assert state is not None
    assert state["enerji"] == 4
    assert state["motivasyon"] == 3
    assert state["engel"] == "React"
    assert state["yuk"] == "yuksek"
    assert state["hazir"] is False


def test_parse_state_rejects_out_of_range():
    text = '[DURUM]{"enerji":99,"motivasyon":0,"yuk":"absurd"}[/DURUM]'
    state = parse_state(text)
    assert state is not None
    assert state.get("enerji") is None
    assert state.get("motivasyon") is None
    assert state.get("yuk") is None


def test_parse_state_invalid_json():
    assert parse_state("[DURUM]{not json}[/DURUM]") is None


def test_parse_state_missing_block():
    assert parse_state("sadece metin") is None
