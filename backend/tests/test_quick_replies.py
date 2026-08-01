"""Quick-reply [SECENEKLER] parsing + sanitizer."""

from backend.services.chat_service import StreamSanitizer, _parse_quick_replies, parse_state


def test_sanitizer_strips_secenekler():
    s = StreamSanitizer()
    out = s.feed(
        "Nasıl hissediyorsun?\n"
        "[SECENEKLER]\n- İyiyim\n- Yorgunum\n[/SECENEKLER]"
    )
    out += s.flush()
    assert "[SECENEKLER]" not in out
    assert "İyiyim" not in out
    assert "Nasıl hissediyorsun?" in out


def test_parse_quick_replies():
    text = (
        "Seç:\n[SECENEKLER]\n"
        "- Zaman yetmiyor\n"
        "- Konuyu anlamadım\n"
        "- Bu çok uzun bir seçenek metni kesilmeli\n"
        "[/SECENEKLER]"
    )
    replies = _parse_quick_replies(text)
    assert replies is not None
    assert replies[0] == "Zaman yetmiyor"
    assert len(replies[2]) <= 24


def test_parse_state_accepts_word_labels():
    text = (
        '[DURUM]{"enerji":"İyiyim","motivasyon":"İstekliyim",'
        '"engel":null,"yuk":"orta","hazir":false}[/DURUM]'
    )
    state = parse_state(text)
    assert state is not None
    assert state["enerji"] == 8
    assert state["motivasyon"] == 8
    assert state["yuk"] == "orta"
