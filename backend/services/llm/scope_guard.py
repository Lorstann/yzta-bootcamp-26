# backend/services/llm/scope_guard.py
"""
Kapsam kilidi: Equa burnout/kariyer koçu dışına çıkan mesajları reddeder.

Katman 1 — hızlı desen (0 ms): chip / kısa mesaj / deny / allow.
Katman 2 — yalnızca kararsız kalanlar için küçük LLM sınıflandırıcı (fail-open).

Konu dışı mesajlar risk sinyali ÜRETMEZ (off_topic ayrı kanal).
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Literal

from backend.config import settings
from backend.services.checkin_flow import (
    ENERGY_CHOICES,
    MOTIVATION_CHOICES,
    Stage,
    default_quick_replies,
)

logger = logging.getLogger(__name__)

ScopeFamily = Literal["leisure", "hard"]

_SHORT_CIRCUIT_MAX_LEN = 25
_CLASSIFIER_TIMEOUT_S = 2.5

_CLASSIFIER_PROMPT = """\
Sen Equa kapsam sınıflandırıcısısın. Tek kelime yanıt ver: IN veya OUT.

IN = eğitim/müfredat, teknik öğrenme, kariyer/mülakat, çalışma planı,
zaman yönetimi, motivasyon, stres, uyku, mola/dinlenme planlama,
bootcamp süreci, kişisel kapasite.

OUT = yemek tarifi, genel kültür/tarih/coğrafya soruları, ödev çözme,
makale/şiir/çeviri üretimi, haber/spor/siyaset, alakasız eğlence içeriği.

Mesaj: {message}
"""

# İçerik talebi — aktiviteye çevrilebilir (tarif verme, molayı öner)
_LEISURE_DENY = (
    "tarif",
    "nasıl pişir",
    "nasil pisir",
    "kaç kalori",
    "kac kalori",
    "dizi öner",
    "dizi oner",
    "film öner",
    "film oner",
    "şarkı sözü",
    "sarki sozu",
    "oyun öner",
    "oyun oner",
    "ne pişir",
    "ne pisir",
    "yemek tarifi",
    "makarna tarifi",
    "kek tarifi",
    "playlist",
    "müzik öner",
    "muzik oner",
)

# Tamamen kapsam dışı — kısa red
_HARD_DENY = (
    "kaç yılında",
    "kac yilinda",
    "kaç yılında bitti",
    "başkenti",
    "baskenti",
    "kim buldu",
    "kim icat",
    "integral",
    "denklemi çöz",
    "denklemi coz",
    "şu ödevi",
    "su odevi",
    "ödevimi çöz",
    "odevimi coz",
    "çeviri yap",
    "ingilizceye çevir",
    "türkçeye çevir",
    "makale yaz",
    "şiir yaz",
    "siir yaz",
    "maç sonucu",
    "mac sonucu",
    "seçim sonucu",
    "secim sonucu",
    "döviz",
    "doviz",
    "hisse senedi",
    "bitcoin",
    "kripto fiyat",
    "dünya savaşı",
    "dunya savasi",
    "osmanlı",
    "osmanli",
)

# Kapsam içi ipuçları
_ALLOW_HINTS = (
    "mülakat",
    "mulakat",
    "cv",
    "özgeçmiş",
    "ozgecmis",
    "portfolyo",
    "portfolio",
    "python",
    "sql",
    "pandas",
    "react",
    "javascript",
    "typescript",
    "node",
    "git",
    "docker",
    "api",
    "sprint",
    "ödev teslim",
    "odev teslim",
    "müfredat",
    "mufredat",
    "bootcamp",
    "akademi",
    "yorgun",
    "tüken",
    "tuken",
    "uyku",
    "mola",
    "motivasyon",
    "enerji",
    "plan",
    "görev",
    "gorev",
    "kapasite",
    "stres",
    "zorlanıyorum",
    "zorlaniyorum",
    "anlamadım",
    "anlamadim",
    "nasıl çalış",
    "nasil calis",
    "tekrar et",
    "konuyu",
    "ders",
    "proje",
    "github",
    "linkedin",
    "iş başvuru",
    "is basvuru",
    "dinlen",
    "şarj",
    "sarj",
    "hobi",
    "yürüyüş",
    "yuruyus",
)


def _normalize(text: str) -> str:
    return (
        (text or "")
        .replace("İ", "i")
        .replace("I", "ı")
        .lower()
        .strip()
    )


def _chip_labels() -> frozenset[str]:
    labels: set[str] = set()
    for table in (ENERGY_CHOICES, MOTIVATION_CHOICES):
        for label in table:
            labels.add(_normalize(label))
    # Same chips as default_quick_replies for explore/focus
    for stage in ("opening", "explore", "focus"):
        for label in default_quick_replies(stage):
            labels.add(_normalize(label))
    return frozenset(labels)


_CHIP_LABELS = _chip_labels()


@dataclass(frozen=True)
class ScopeDecision:
    in_scope: bool
    family: ScopeFamily | None = None
    reason: str | None = None  # log/telemetri only


def _fast_pattern(message: str) -> ScopeDecision | None:
    """
    Return a firm decision or None if unsure (needs classifier).
    Deny beats allow. Short/chip → IN without classifier.
    """
    cleaned = (message or "").strip()
    if not cleaned:
        return ScopeDecision(in_scope=True, reason="empty")

    norm = _normalize(cleaned)

    # Short-circuit: chips and very short replies
    if norm in _CHIP_LABELS:
        return ScopeDecision(in_scope=True, reason="chip")
    if len(cleaned) < _SHORT_CIRCUIT_MAX_LEN and not any(
        d in norm for d in (*_LEISURE_DENY, *_HARD_DENY)
    ):
        return ScopeDecision(in_scope=True, reason="short")

    # Deny first
    for pattern in _LEISURE_DENY:
        if pattern in norm:
            return ScopeDecision(
                in_scope=False, family="leisure", reason=f"leisure:{pattern}"
            )
    for pattern in _HARD_DENY:
        if pattern in norm:
            return ScopeDecision(
                in_scope=False, family="hard", reason=f"hard:{pattern}"
            )

    # Allow hints
    if any(h in norm for h in _ALLOW_HINTS):
        return ScopeDecision(in_scope=True, reason="allow_hint")

    return None  # unsure


async def _classify_with_llm(message: str) -> ScopeDecision:
    """Small LLM call; fail-open (IN) on any error/timeout/missing key."""
    if not settings.scope_classifier_enabled:
        logger.info("Scope classifier disabled — fail-open IN")
        return ScopeDecision(in_scope=True, reason="classifier_disabled")

    if not settings.llm_api_key:
        logger.warning("Scope classifier: no API key — fail-open IN")
        return ScopeDecision(in_scope=True, reason="no_api_key")

    try:
        from langchain_core.messages import HumanMessage

        from backend.services.llm.provider import build_chat_llm

        llm = build_chat_llm(streaming=False)
        prompt = _CLASSIFIER_PROMPT.format(message=message.strip()[:500])

        async def _invoke():
            return await llm.ainvoke([HumanMessage(content=prompt)])

        result = await asyncio.wait_for(_invoke(), timeout=_CLASSIFIER_TIMEOUT_S)
        text = (getattr(result, "content", None) or str(result) or "").strip().upper()
        # Take first token
        token = text.split()[0] if text else ""
        if token.startswith("OUT"):
            logger.info("Scope classifier OUT | preview=%s", message[:40])
            return ScopeDecision(
                in_scope=False, family="hard", reason="classifier_out"
            )
        logger.info("Scope classifier IN | preview=%s", message[:40])
        return ScopeDecision(in_scope=True, reason="classifier_in")
    except asyncio.TimeoutError:
        logger.warning("Scope classifier timeout — fail-open IN")
        return ScopeDecision(in_scope=True, reason="classifier_timeout")
    except Exception as err:
        logger.warning("Scope classifier error — fail-open IN | err=%s", err)
        return ScopeDecision(in_scope=True, reason="classifier_error")


async def check_scope(message: str) -> ScopeDecision:
    """
    Full scope check: fast patterns first, then optional LLM classifier.
    """
    fast = _fast_pattern(message)
    if fast is not None:
        if not fast.in_scope:
            logger.info(
                "Scope deny (fast) | family=%s reason=%s",
                fast.family,
                fast.reason,
            )
        return fast
    return await _classify_with_llm(message)


_LEISURE_REFUSALS = (
    "Tarif veya içerik üretmek bende yok — ama şunu yapabiliriz: "
    "bu aktivite sana iyi geliyorsa bunu bugünün molası olarak planlayalım. "
    "İstersen ne kadar süre ayıracağını birlikte netleştirelim.",
    "Bunu bir ChatGPT gibi yanıtlayamam; Equa olarak görevim tükenmeni "
    "engellemek. Yemek/hobi seni şarj ediyorsa onu molaya çevirmek daha "
    "doğru — tarif vermem, ama dinlenme planında yer açabiliriz.",
    "İçerik (tarif, dizi listesi vb.) vermiyorum. Bunun yerine: ekrandan "
    "uzaklaşmak için kısa bir aktivite planı çıkarabiliriz. Bootcamp "
    "sürecine veya bugünkü enerjine dönebiliriz.",
)

_HARD_REFUSALS = (
    "Bu Equa'nın kapsamı dışında. Ben bootcamp sürecinde kapasite, "
    "müfredat, kariyer ve tükenmişliği önleme konusunda yardımcı oluyorum. "
    "Genel kültür / ödev çözme / alakasız sorulara cevap vermiyorum.",
    "Bunu yanıtlayamam — Equa bir genel sohbet botu değil. Eğitim, teknik "
    "öğrenme, mülakat veya dinlenme planı hakkında sorarsan yardımcı olurum.",
    "Kapsam dışı. Amacım ChatGPT gibi her şeye cevap vermek değil; "
    "öğrenme yolunda yanındayım ve burnout'u engellemek. "
    "Müfredat, proje veya bugünkü ruh halinle devam edelim.",
)


def build_refusal_text(
    *,
    family: ScopeFamily | None,
    mode: Literal["checkin", "coach"] = "checkin",
    stage: Stage | str | None = None,
    turn_count: int = 0,
    program_track: str | None = None,
    blocker: str | None = None,
) -> str:
    """Deterministic refusal — no LLM call. 3 variants via turn_count % 3."""
    idx = abs(int(turn_count)) % 3
    if family == "leisure":
        body = _LEISURE_REFUSALS[idx]
    else:
        body = _HARD_REFUSALS[idx]
        extras: list[str] = []
        if program_track:
            extras.append(f"Programın: {program_track}.")
        if blocker:
            extras.append(f"Bugün konuştuğumuz engel: {blocker}.")
        if extras:
            body = f"{body} {' '.join(extras)}"

    if mode == "checkin" and stage and stage != "completed":
        redirect = _stage_redirect(stage)
        if redirect:
            body = f"{body}\n\n{redirect}"
    return body


def _stage_redirect(stage: Stage | str) -> str:
    if stage == "opening":
        return "Şimdi check-in'e dönelim: bugün nasıl bir moddasın?"
    if stage == "explore":
        return "Check-in'e dönelim: bugün seni en çok ne zorladı?"
    if stage == "focus":
        return "Check-in'e dönelim: bugün neye odaklanmak istersin?"
    if stage == "closing":
        return "Check-in'i toparlayalım — bugün için küçük bir adım belirleyelim."
    return ""


def refusal_quick_replies(
    *,
    mode: Literal["checkin", "coach"],
    stage: Stage | str | None = None,
) -> list[str] | None:
    if mode != "checkin" or not stage or stage == "completed":
        return None
    replies = default_quick_replies(stage)
    return replies or None
