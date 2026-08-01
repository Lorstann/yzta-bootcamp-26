"""Task specificity: filter fix, pipe parse, generic drop."""

from backend.services.chat_service import (
    StreamSanitizer,
    _filter_tasks_for_curriculum,
    _parse_tasks,
    drop_generic_tasks,
)


def test_no_curriculum_keeps_technical_tasks():
    tasks = [
        {"title": "Pandas groupby tekrarı", "description": "3 agregasyon"},
        {"title": "SQL JOIN yaz", "description": "LEFT JOIN"},
    ]
    kept = _filter_tasks_for_curriculum(tasks, "Henüz müfredat yüklenmedi.")
    assert len(kept) == 2
    assert any("Pandas" in t["title"] for t in kept)


def test_off_scope_solidity_dropped_without_track():
    tasks = [
        {"title": "Solidity contract yaz", "description": ""},
        {"title": "Pandas tekrarı", "description": "groupby"},
    ]
    kept = _filter_tasks_for_curriculum(tasks, "Henüz müfredat yüklenmedi.")
    assert all("Solidity" not in t["title"] for t in kept)
    assert any("Pandas" in t["title"] for t in kept)


def test_wellness_task_kept_even_without_curriculum_overlap():
    tasks = [
        {
            "title": "Bornova’da yürüyüş",
            "description": "30 dk parkta yürü",
        }
    ]
    kept = _filter_tasks_for_curriculum(
        tasks,
        "React hooks useState",
        hobbies=["yürüyüş"],
        city="İzmir",
    )
    assert len(kept) == 1


def test_parse_tasks_pipe_format():
    text = """
Tamam, bugün için:
[GOREVLER]
- Pandas groupby | 30 dk, 3 agregasyon notebook'a
- Kısa yürüyüş | 20 dk açık hava
[/GOREVLER]
"""
    tasks = _parse_tasks(text)
    assert tasks is not None
    assert tasks[0]["title"] == "Pandas groupby"
    assert "30 dk" in tasks[0]["description"]
    assert tasks[1]["title"] == "Kısa yürüyüş"


def test_drop_generic_keeps_specific():
    tasks = [
        {"title": "Proje gereksinimlerini ve eksik kalan yerleri listele", "description": ""},
        {"title": "Mentörüne takıldığın en net soruyu yaz", "description": ""},
        {"title": "Pandas groupby ile 3 agregasyon", "description": "30 dk"},
    ]
    kept = drop_generic_tasks(tasks)
    assert len(kept) == 1
    assert "Pandas" in kept[0]["title"]


def test_drop_generic_never_empties():
    tasks = [
        {"title": "Mentörüne soru yaz", "description": ""},
        {"title": "Planını gözden geçir", "description": ""},
    ]
    kept = drop_generic_tasks(tasks)
    assert len(kept) == 2


def test_sanitizer_strips_profil_block():
    s = StreamSanitizer()
    out = s.feed("Merhaba [PROFIL]{\"sehir\":\"İzmir\"}[/PROFIL] dünya")
    out += s.flush()
    assert "İzmir" not in out
    assert "Merhaba" in out
    assert "dünya" in out
    assert "[PROFIL]" in s.raw
