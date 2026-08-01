"""Wellbeing burnout bands and context builder."""

from backend.services.wellbeing import burnout_level, build_wellbeing_context


def test_burnout_yuksek_on_low_energy():
    assert burnout_level(energy=2, motivation=6, capacity=70) == "yuksek"


def test_burnout_orta_on_mid_signals():
    assert burnout_level(energy=5, motivation=8, capacity=80) == "orta"
    assert burnout_level(energy=8, motivation=8, capacity=40) == "orta"


def test_burnout_dusuk_when_healthy():
    assert burnout_level(energy=8, motivation=8, capacity=80) == "dusuk"


def test_wellbeing_empty_profile_asks_gently():
    ctx = build_wellbeing_context({}, {"enerji": 4})
    assert "Bilgi yok" in ctx
    assert "UYDURMA" in ctx


def test_wellbeing_includes_hobbies_city_track():
    ctx = build_wellbeing_context(
        {
            "city": "İzmir",
            "district": "Bornova",
            "program_track": "Veri Bilimi",
            "interests": {"hobbies": ["yürüyüş", "kitap"], "recharge": ["doğa"]},
            "capacity_score": 45,
        },
        {"enerji": 4, "motivasyon": 5},
    )
    assert "İzmir" in ctx
    assert "Bornova" in ctx
    assert "Veri Bilimi" in ctx
    assert "yürüyüş" in ctx
    assert "Burnout riski:" in ctx
