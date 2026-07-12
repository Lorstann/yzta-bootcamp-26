# **Takım İsmi**

Takım 320

# Ürün İle İlgili Bilgiler

## Takım Üyeleri

- Dilan Özyazıcı: Product Owner
- Mustafa Kurtar: Scrum Master
- Elif Kahrıman: Team Member / Developer
- Hafize Talya Keysan: Team Member / Developer
- Hasibe Nur Tunç: Team Member / Developer

## Ürün İsmi

--Equa--

## Ürün Açıklaması

- Equa, bootcamp, akademi ve üniversite gibi yoğun eğitim süreçlerinden geçen öğrenciler için tasarlanmış, B2B2C modeliyle çalışan yapay zeka destekli bir kariyer ve kapasite koçudur. Kurumların müfredatını baz alarak öğrencinin gelişimini analiz eder ve sürdürülebilir haftalık aksiyon planları sunar. Kurumlara ise dropout risklerini proaktif tespit eden bir ROI dashboard'u sağlar.

## Ürün Özellikleri

- PWA destekli duyarlı (responsive) Web App (mobil-first)
- Haftalık 2 dakikalık AI check-in asistanı (streaming chat)
- Kurum müfredatına dayalı RAG tabanlı görev önerisi
- Öğrenci kapasitesine göre haftalık max 3 görev atama
- Kurumlar için öğrenci risk sinyalleri (Yeşil, Sarı, Kırmızı) dashboard'u
- Önlenen dropout sayısı ve korunan gelir (ROI) metrikleri

## Hedef Kitle

- Bootcamp ve akademi öğrencileri (birincil kullanıcı — "Bunalmış Can")
- Eğitim kurumu koordinatörleri (ikincil kullanıcı — "Kör Uçuşundaki Zeynep")
- 100+ öğrencinin başarısından sorumlu eğitim profesyonelleri
- Teknik bootcamp ve kariyer hazırlık programları

## Product Backlog URL

[Story Backlog (specs/stories)](specs/stories/README.md) · [Epic İndeksi (specs/epics)](specs/epics/README.md) · [PRD](specs/prds/prd.md) · [Tech Stack](specs/techstack.md)

## Daily Scrum Notları

Toplantılar bootcamp sürecinde Slack ve Google Meets üzerinden yürütülmüştür. Aşağıda Sprint 1 kapsamındaki önemli günlük notlar kronolojik olarak özetlenmiştir.

### 22.06.2026

- Ekip tanışması yapıldı.
- Ürün **teması** üzerinde konuşuldu; çevresel ve toplumsal temalara yönelindi.
- Scrum Master ve Product Owner belirlendi.

### 25.06.2026

- Proje fikri üzerine toplantı yapıldı.
- Proje fikri kesinleştirildi.
- Takım bilgilendirme formu doldurularak gönderildi.

### 29.06.2026

- Proje fikri için **kullanım senaryoları** üzerinde çalışıldı.
- **Ürün ismi** tartışmaları yapıldı.
- Dokümantasyon için **Google Docs** oluşturuldu.
- Fikre yönelik öneriler, eksiklikler ve analizler; ekip üyeleri tarafından süre ve gün fark etmeksizin dokümana eklendi.

### 03.07.2026

- Dokümantasyonda belirlenen kriterlere göre **elemeler** yapıldı.
- **Ürün ismi kesinleştirildi:** Equa.
- **Ürün kapsamı** belirlendi.
- Gerekli dokümanlar oluşturuldu:
  - [PRD](specs/prds/prd.md)
  - [Epic'ler](specs/epics/README.md)
  - [User Stories](specs/stories/README.md)
- Sprintler için **planlama** yapıldı.
- Kodlama aşamasına geçmeden önce fikrin detaylı planlanmasının daha mantıklı olduğuna karar verildi:
  - **Sprint 1:** Planlama, derinleşme ve analiz
  - **Sprint 2 ve 3:** Ürün geliştirme, test etme ve production aşamaları

---

# Sprint 1

**Sprint Hedefi (Gün 1–14):** Ekip olarak tanışmak, proje mimarisini oluşturmak; detaylı PRD, epic ve story dokümanlarını hazırlayarak tech stack ve architecture kararlarını netleştirmek.

- **Backlog düzeni ve Story seçimleri**: Sprint 1'de kod geliştirmesi yapılmamıştır. Backlog'umuz ürün gereksinimlerini analiz ederek planlama ve dokümantasyon odaklı ilerlemiştir. Story başına çıkan tahmin puanı, toplam puanın yarısından az tutulmuştur.

  Sprint 1 teslim çıktıları:

  | Çıktı | Konum | Açıklama |
  |-------|-------|----------|
  | PRD | [specs/prds/prd.md](specs/prds/prd.md) | Equa MVP ürün gereksinimleri |
  | Epic'ler | [specs/epics/](specs/epics/README.md) | 8 epic + indeks |
  | Story Backlog | [specs/stories/](specs/stories/README.md) | 26 story (Sprint 2–3 için plan) |
  | Tech Stack | [specs/techstack.md](specs/techstack.md) | FastAPI, React PWA, PostgreSQL, RAG mimarisi |

  Kod implementasyonu (S01–S07) Sprint 2 backlog'una alınmıştır. Story'ler yapılacak işlere (task'lere) bölünmüştür. Detaylar: [specs/stories/README.md](specs/stories/README.md)

- **Daily Scrum**: Daily Scrum toplantılarının zamansal sebeplerden ötürü Slack üzerinden yapılmasına karar verilmiştir. Daily Scrum toplantısı örneği jpeg veya word olarak Readme'de tarafımızdan paylaşılmaktadır: [Sprint 1 Daily Scrum Chats](https://github.com/OyunveUygulamaAkademisi/BootcampScrumTemplate/blob/main/ProjectManagement/Sprint1Documents/DailyScrumMeetingNotesSprint1.docx?raw=true)

- **Sprint board update**: Sprint board screenshotları: 
![Backlog 1](https://raw.githubusercontent.com/OyunveUygulamaAkademisi/BootcampScrumTemplate/main/ProjectManagement/Sprint1Documents/backlog1.png) 
![Backlog 2](https://raw.githubusercontent.com/OyunveUygulamaAkademisi/BootcampScrumTemplate/main/ProjectManagement/Sprint1Documents/backlog2.png) 
![Backlog 3](https://raw.githubusercontent.com/OyunveUygulamaAkademisi/BootcampScrumTemplate/main/ProjectManagement/Sprint1Documents/backlog3.png)

- **Ürün Durumu**: Sprint 1 kapsamında çalışan bir ürün demosu bulunmamaktadır; teslim çıktıları dokümantasyon ve mimari planlama düzeyindedir.

- **Sprint Review**: 
Alınan kararlar: Takım 320 olarak ekip tanışması ve rol dağılımı (PO, Scrum Master, Developer) tamamlandı. Equa için detaylı PRD yazıldı; 8 epic ve 26 story ile backlog oluşturuldu. Tech stack (FastAPI + Python backend, React PWA frontend, PostgreSQL + pgvector, S3, Bedrock/LLM + RAG) ve katmanlı mimari kararları [specs/techstack.md](specs/techstack.md) dosyasında belgelendi. Kod geliştirmesi Sprint 2'de başlayacak şekilde S01–S07 story'leri backlog'a işlendi. Sprint Review katılımcıları: Takım 320 (Dilan Özyazıcı, Mustafa Kurtar, Elif Kahrıman, Hafize Talya Keysan, Hasibe Nur Tunç)

- **Sprint Retrospective:**
  - Sprint 1'de önce planlama ve dokümantasyon yapmak, takımın ürün vizyonu ve mimari üzerinde ortak fikir birliğine varmasını sağladı
  - Ekip tanışması ve rol netliği bootcamp sürecinin geri kalanı için iyi bir temel oluşturdu
  - Sprint 2'de kod yazımına geçerken görev dağılımının daha somut yapılması ve story point tahminlerinin gerçek implementasyon deneyimiyle güncellenmesi gerekiyor

---

# Sprint 2


---

# Sprint 3

---
