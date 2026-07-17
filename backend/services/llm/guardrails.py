# backend/services/llm/guardrails.py
"""
S16: Anahtar kelime tabanlı guardrail sistemi.
Ham sohbet asla kuruma gönderilmez (techstack.md §7) — bu modül sadece
kategori seviyesinde bir sinyal üretir, mesaj içeriğini dışarı sızdırmaz.
"""
from dataclasses import dataclass
from typing import Optional

def _normalize(text: str) -> str:
    """
    Türkçe karakterler için güvenli lowercase.
    Python'ın standart .lower()'ı 'İ' harfini yanlış çevirir (İ -> i̇, noktalı
    bileşik karakter), bu yüzden Türkçe metinlerde önce elle çeviriyoruz.
    """
    return text.replace("İ", "i").replace("I", "ı").lower()

CRITICAL_RISK_KEYWORDS = {
    "intihar", "kendimi öldürmek", "yaşamak istemiyorum", "hayatıma son",
    "dayanamıyorum", "kendime zarar", "ölmek istiyorum", "hiçbir şeyin anlamı yok",
}
DROPOUT_RISK_KEYWORDS = {
    "bırakmak istiyorum", "okulu bırakacağım", "bootcamp'i bırakıyorum",
    "pes ediyorum", "bana göre değilmiş", "kaydımı sildirmek",
}
DEPRESSION_KEYWORDS = {
    "çok depresifim", "tükendim", "tükenmişlik", "burnout",
    "sürekli ağlıyorum", "umutsuz", "çaresiz", "değersiz",
}

_CATEGORY_MAP = {
    "critical": CRITICAL_RISK_KEYWORDS,
    "dropout": DROPOUT_RISK_KEYWORDS,
    "depression": DEPRESSION_KEYWORDS,
}

# Performans + güvenlik: kelimeler modül İLK YÜKLENDİĞİNDE (bir kez) normalize ediliyor.
_NORMALIZED_CATEGORY_MAP = {
    category: {_normalize(word) for word in words}
    for category, words in _CATEGORY_MAP.items()
}

COMPASSIONATE_REDIRECT_TEMPLATE = """
Duygularını benimle paylaştığın için çok teşekkür ederim. Şu an çok zor bir
dönemden geçtiğini duyabiliyorum ve bu hissettiklerin gerçekten ağır olabilir.

Ben bir yapay zeka asistanıyım ve sana hak ettiğin insani ve profesyonel desteği
tam olarak sağlayamam. Lütfen bu yükü tek başına taşıma.

1. Eğitim sürecinle ilgili sıkışmışlık hissediyorsan, kurumundaki öğrenci destek
   koordinatörünle görüşebilirsin, sana yardım etmek için oradalar.
2. Kendini güvende hissetmiyor ya da yoğun bir çaresizlik yaşıyorsan, lütfen hemen
   güvendiğin bir yakınına ulaş ya da 112 Acil Çağrı Merkezi'ni ara.

Sen değerlisin ve destek almaktan çekinmemelisin.
"""

@dataclass
class GuardrailResult:
    triggered: bool
    category: Optional[str] = None      # "critical" | "dropout" | "depression" | None
    template: Optional[str] = None

def check_for_risks(message: str) -> GuardrailResult:
    """
    Kullanıcı mesajında riskli kelimeleri arar.
    Önem sırası: critical > dropout > depression.
    """
    normalized = _normalize(message)

    for category in ("critical", "dropout", "depression"):
        keywords = _NORMALIZED_CATEGORY_MAP[category]
        if any(word in normalized for word in keywords):
            return GuardrailResult(
                triggered=True,
                category=category,
                template=COMPASSIONATE_REDIRECT_TEMPLATE,
            )

    return GuardrailResult(triggered=False)