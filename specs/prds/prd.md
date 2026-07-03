# PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Ürün Adı:** Equa
**Sürüm:** 1.0 (MVP)
**Tarih:** 4 Temmuz 2026
**Platform:** Web App (Mobile-First PWA & Desktop Dashboard)
**İş Modeli:** B2B2C SaaS
**Geliştirme Süresi:** 3 Sprint (6 Hafta)

---

## 1. Executive Summary (Yönetici Özeti)
Equa, yoğun eğitim süreçlerinden (bootcamp, akademi, üniversite) geçen öğrenciler için tasarlanmış, B2B2C modeliyle çalışan yapay zeka destekli bir kariyer ve kapasite koçudur. Sistem, kurumların müfredatını (syllabus) baz alarak öğrencinin akademik, teknik ve sosyal gelişimini analiz eder; sürdürülebilir haftalık aksiyon planları sunar. Kurumlara ise dropout (bırakma) risklerini proaktif olarak tespit eden ve doğrudan korunan eğitim geliri/başarı oranını gösteren bir ROI dashboard'u sağlar.

## 2. Problem Statement (Problem Tanımı)
Öğrenciler teknik gelişim, portfolyo oluşturma ve sosyal beceri kazanımı arasında önceliklendirme yapamamakta ve tükenmişlik (burnout) yaşamaktadır. Eğitim kurumları ise öğrencilerin psikolojik yükünü, kapasite aşımlarını ve kariyer hazırlık seviyelerini gerçek zamanlı göremediği için dropout oranlarını düşürmekte ve işe yerleştirme hedeflerinde reaktif kalmaktadır.

## 3. Vision (Vizyon)
Her öğrencinin kendi psikolojik ve bilişsel kapasitesine uygun, sürdürülebilir bir hızda (Equilibrium/Pace) hedeflerine ulaşmasını sağlamak; kurumların öğrenci başarısını şansa bırakmadığı veri odaklı bir eğitim ekosistemi yaratmak.

## 4. Goals & Non-Goals

**Hedefler:**
*   Öğrencilerin %70'ini haftalık 2 dakikalık AI Web App sohbetleriyle "Haftalık Aktif Kullanıcı (WAU)" olarak tutmak.
*   B2B pilot müşterilerinde (bootcamp/akademi) öğrenci bırakma (dropout) oranlarını %20 azaltmak.
*   Risk tespitinden mentör müdahalesine kadar geçen süreyi 14 günden 2 güne indirmek.

**Hedeflenmeyenler (Non-Goals):**
*   WhatsApp, Telegram veya Discord botu olmak (UX standartları ve gizlilik nedeniyle sadece Web App).
*   Klinik psikolojik destek veya tıbbi teşhis (burnout) sunmak.
*   Klasik bir manuel görev yöneticisi (Jira/Asana alternatifi) olmak.

## 5. Target Users & Personas

**Birincil Kullanıcı (Öğrenci) - "Bunalmış Can"**
*   **Profil:** 22 yaşında, teknik bir bootcamp öğrencisi. Portfolyo ve mülakat stresi yüksek.
*   **İhtiyaç (JTBD):** "Bana şu anki kapasiteme ve kurumun müfredatına uygun, tükenmeme engel olacak yutulabilir (bite-sized) bir haftalık kariyer reçetesi ver."

**İkincil Kullanıcı (Kurum Koordinatörü) - "Kör Uçuşundaki Zeynep"**
*   **Profil:** 100+ öğrencinin başarısından sorumlu eğitim profesyoneli.
*   **İhtiyaç (JTBD):** "Bana öğrencilerimin risk metriklerini ve Equa'nın kurtardığı öğrenci sayısını (ROI) tek ekranda göster ki, dropout yaşanmadan proaktif müdahale edebileyim."

## 6. Functional Requirements (MoSCoW)

| ID | Modül | Gereksinim | Öncelik |
| :--- | :--- | :--- | :--- |
| FR1 | Platform | Sistemin PWA destekli duyarlı (responsive) bir Web App olarak çalışması. | **Must** |
| FR2 | Onboarding | 5 dakikalık chat tabanlı teşhis (diagnostic) ve profil oluşturma akışı. | **Must** |
| FR3 | Data Ingestion | LinkedIn profil PDF'i yükleyerek OCR/LLM (Textract/LlamaParse) ile yetkinlik JSON'u çıkarma. | **Must** |
| FR4 | Fallback Flow | PDF okunamadığında AI'ın eksik verileri chat üzerinden kullanıcıya sorması. | **Must** |
| FR5 | AI Core | Hafıza (Memory) ve RAG kullanan haftalık 2 dakikalık AI Check-in asistanı. | **Must** |
| FR6 | Curriculum Inject| AI'ın sadece kurumun sisteme yüklediği müfredat bağlamında görev önermesi. | **Must** |
| FR7 | Load Balancing | Öğrenci kapasitesine göre haftalık maks. 3 görev atayan dengeleme algoritması. | **Must** |
| FR8 | B2B Dashboard | Kurumlar için öğrenci risk sinyallerini (Yeşil, Sarı, Kırmızı) gösteren arayüz. | **Must** |
| FR9 | ROI Tracker | Dashboard'da "Önlenen Dropout Sayısı / Korunan Gelir" metriğinin gösterimi. | **Must** |
| FR10| Integration | GitHub OAuth ile repo/commit kalitesi analizi. | **Won't (MVP)** |

## 7. AI & Security Requirements (Red Teaming & Guardrails)

*   **RAG Tabanlı Hafıza (Retrieval-Augmented Generation):** AI, her yanıtta öğrencinin önceki haftalardaki beyanlarını, yüklenen PDF dokümanlarını ve kurum müfredatını vektörel olarak taramalıdır.
*   **Explainable AI (XAI):** Kurum dashboard'undaki "Kırmızı Risk" bayrağının yanında, yapay zekanın bu kararı hangi davranışsal metriklere (örn: 3 haftadır görev yapılmıyor, düşük enerji beyanı) dayanarak verdiği loglanmalıdır.
*   **Guardrails (Etik Sınırlar):** Kullanıcı sohbet ekranına depresyon, intihar veya eğitimi bırakma isteğiyle ilgili anahtar kelimeler girdiğinde, sistem anında klinik tavsiye vermeyi durdurur. Şefkatli bir yönlendirme şablonu (template) çalıştırır ve kuruma "Yüksek Risk - Mentör Görüşmesi Bekliyor" sinyali gönderir. Ham sohbet verisi **asla** kurumla paylaşılmaz.

## 8. Technical Architecture

Sistem, yüksek performans ve asenkron AI işlemleri göz önüne alınarak modern, bulut tabanlı bir mimariyle inşa edilecektir:

*   **Frontend (Web App):** React (Öğrenciler için PWA optimizasyonu, Kurumlar için zengin veri tabloları). Mock-API ile asenkron paralel geliştirme.
*   **Backend API:** FastAPI (Python) - Streaming AI yanıtları, asenkron işlemler ve hızlı uç noktalar için.
*   **Database (İlişkisel):** Amazon RDS (PostgreSQL) - Kullanıcı profilleri, tenant izolasyonu ve metrikler.
*   **Database (Vektörel):** pgvector (RDS içinde) veya harici yönetilen Vector DB (Pinecone/Weaviate) (RAG hafızası için).
*   **Storage (Depolama):** Amazon S3 - Kurum müfredat dokümanları (PDF/Docx).
*   **AI Orchestration:** Amazon Bedrock (veya doğrudan OpenAI/Anthropic API) + LangChain/LlamaIndex.
*   **Tenant Isolation:** Row-Level Security (RLS) ile B2B müşterilerinin verilerinin donanımsal ve yazılımsal izolasyonu.

## 9. Success Metrics & KPIs

*   **B2B Kurum Çıktıları:**
    *   Dropout oranında net azalma (Pilot program öncesi/sonrası kıyaslaması).
    *   Equa Dashboard üzerinden tetiklenen başarılı mentör müdahalesi sayısı.
*   **Öğrenci Kullanım Metrikleri:**
    *   `ai_checkin_completion_rate`: Haftalık %70 üzeri.
    *   `task_completion_rate`: Önerilen hedeflerin (kapasite dengeli) %60 oranında tamamlanması.
    *   Kariyer hazırlık (Gap Analysis) skorlarında periyodik artış.

## 10. Acceptance Criteria (Kabul Kriterleri)
1.  Öğrenci sisteme mobil tarayıcıdan (Web App) giriş yapabilmeli, herhangi bir uygulama mağazası indirmesine gerek kalmamalıdır.
2.  Kurum müfredatına dahil olmayan hiçbir yeni framework veya araç, AI tarafından öğrenciye "bu hafta bunu öğrenmelisin" şeklinde **önerilmemelidir**.
3.  Öğrenci yorgun olduğunu veya kapasitesinin dolduğunu beyan ettiğinde, sistem açık olan hedefleri otomatik olarak yeniden ölçeklendirmeli (downscale) veya askıya almalıdır.
4.  B2B müşterisi (A Kurumu), B Kurumuna ait hiçbir öğrenci verisini veya müfredatını sistemde kesinlikle görememelidir.

## 11. Roadmap (3 Sprint / 6 Hafta)

**Sprint 1: Çekirdek Deneyim ve Mock-Up (Gün 1-14)**
*   API kontratlarının (JSON) kilitlenmesi.
*   FastAPI iskeletinin kurulması ve Bedrock/LLM ile streaming chat endpoint'inin açılması.
*   Manuel yüklenen bir müfredat üzerinden vektörel (RAG) testlerin yapılması.
*   React PWA arayüzünün (Chat UI) mock-API ile tamamlanması.

**Sprint 2: Hafıza, Güvenlik ve Kurum Altyapısı (Gün 15-28)**
*   PDF yükleme ve Fallback (Sohbet) onboarding akışının koda dökülmesi.
*   PostgreSQL Multi-tenant (çok kiracılı) yapısının ayağa kaldırılması.
*   Red Teaming (Guardrails) senaryolarının aktif edilmesi (Psikolojik sınırların çekilmesi).
*   Öğrenci Dashboard'u ve Kurum (B2B) Dashboard arayüz iskeletinin hazırlanması.

**Sprint 3: B2B ROI ve Canlıya Çıkış (Gün 29-42)**
*   B2B Dashboard'a "Risk Skorlaması" ve "Kurtarılan Öğrenci / ROI" verilerinin bağlanması.
*   Uçtan uca (E2E) testler ve Edge Case denemeleri.
*   2 Pilot bootcamp'in öğrenci listelerinin yüklenmesi ve PWA linkinin öğrencilere gönderilerek canlıya çıkılması (Launch).