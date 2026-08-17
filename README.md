# 🚨 Project Dont Panic — AI-Tabanlı Kurumsal Kriz Yönetimi & PR Simülatörü

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F61?style=flat)](https://langchain.com)
[![Next.js](https://img.shields.io/badge/Next.js-15+-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

**Project Dont Panic**, yüksek riskli kurumsal kriz anlarında (veri sızıntıları, yapay zeka malfonksiyonları, CEO deepfake skandalları vb.) yöneticilerin ve PR ekiplerinin kriz iletişimi stratejilerini ve kararlarını gerçek zamanlı simüle eden **Multi-Agent (Çoklu Yapay Zeka Ajanı)** destekli interaktif bir simülasyon platformudur.

---

## 📌 Proje Özeti ve Çalışma Mantığı

Kullanıcı (Kriz Yöneticisi), simülasyon terminalinden kriz anına yönelik bir basın açıklaması, tweet veya stratejik hamle girer. Arka planda **LangGraph** mimarisiyle çalışan yapay zeka ajanları bu açıklamayı anında değerlendirir:

1. **Strateji Ajanı (Orchestrator):** Kriz Şiddet Seviyesi, Marka İtibar Endeksi ve Borsa Hisse Etkisi metriklerindeki anlık değişimi ($\Delta$) hesaplar.
2. **Gazeteci Ajanı (Journalist):** Bloomberg veya TechChronicle tarzı medya organlarının son dakika haber başlıklarını üretir.
3. **Sosyal Medya Ajanı (Troll):** İnternet halkının, sosyal medyanın (Twitter/X vb.) vereceği viralleşen tepkileri ve linç dalgalarını simüle eder.

Tüm sonuçlar **WebSockets** protokolü ile gecikmesiz olarak ön yüzdeki canlı kontrol paneline akar.

---

## ✨ Öne Çıkan Özellikler

- 🤖 **Çoklu Ajan Mimarisi (Multi-Agent Engine):** LangGraph ve `qwen-397b` büyük dil modeli ile birbiriyle uyumlu çalışan 3 farklı uzmanlaşmış ajan (*Orchestrator*, *Journalist*, *Troll*).
- 📊 **Canlı Telemetri & Zaman Serisi Analitiği:** Recharts kütüphanesi ile Kriz Şiddet Seviyesi, Marka İtibarı ve Borsa Değişiminin tur bazlı grafiksel takibi.
- 📡 **Gerçek Zamanlı Canlı Akış (WebSockets):** Ajanların akıl yürütme adımlarının (Chain-of-Thought) ve ürettikleri sosyal medya postlarının anlık ekrana düşmesi.
- 🧠 **Şeffaf Ajan Akıl Yürütme Konsolu (Agent Reasoning Console):** Yapay zekanın kararları alırken izlediği mantık adımlarının kullanıcıya şeffaf gösterimi.
- 🎯 **Hazır Kriz Senaryoları (Scenario Templates):**
  - **Data Breach 2026:** Biyometrik veri sızıntısı skandalı.
  - **AI Hallucination Scandal:** Tıbbi yapay zeka hatalı teşhis vakası.
  - **CEO Deepfake Leak:** CEO adına üretilen şantaj içerikli sahte ses/video sızıntısı.

---

## 🏗️ Sistem Mimarısı & Akış Diyagramı

```mermaid
graph TD
    User([Kullanıcı / PR Yöneticisi]) -->|Aksiyon Metni Gönderir| WS[WebSocket Router / FastAPI]
    WS --> Graph[LangGraph StateGraph Engine]
    
    subgraph Multi-Agent Engine (Python / qwen-397b)
        Graph --> Orch[1. Lead Crisis Orchestrator]
        Orch -->|Metric Deltas & Evaluation| Jour[2. Journalist Agent]
        Jour -->|Breaking News Output| Troll[3. Troll / Internet Mob Agent]
        Troll -->|Viral Tweets & Memes| StateEnd[State Update Complete]
    end
    
    StateEnd -->|Canlı Veri Akışı| WS
    WS -->|Social Posts, Agent Logs, Metrics| UI[Next.js Dashboard UI]
```

---

## 🛠️ Teknoloji Yığını (Tech Stack)

### Arka Yüz (Backend)
- **Dil / Runtime:** Python 3.10+
- **API Framework:** FastAPI, Uvicorn
- **Yapay Zeka Mimarisi:** LangGraph, LangChain, Pydantic
- **İletişim Protokolü:** Real-Time WebSockets
- **LLM Motoru:** Custom Qwen Provider (`qwen-397b`)

### Ön Yüz (Frontend)
- **Framework:** Next.js 15 (App Router), React 19, TypeScript
- **Stil & Tasarım:** Tailwind CSS, Lucide Icons
- **Grafik & Veri Görselleştirme:** Recharts
- **State Yönetimi:** Zustand

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler
- Python 3.10 veya üzeri
- Node.js 18.0 veya üzeri
- npm veya yarn / pnpm / bun

---

### 1. Arka Yüz (Backend) Kurulumu

```bash
# Backend dizinine gidin
cd backend

# Sanal ortam (venv) oluşturun ve aktifleştirin
python3 -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Environment (.env) dosyasını ayarlayın
cp .env.example .env
# .env dosyasını açıp LLM_API_KEY bilginizi güncelleyin

# Sunucuyu başlatın
uvicorn app.main:app --reload --port 8000
```
Backend `http://localhost:8000` üzerinde çalışmaya başlayacaktır.

---

### 2. Ön Yüz (Frontend) Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Bağımlılıkları yükleyin
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```
Frontend `http://localhost:3000` üzerinde açılacaktır.

---

## 🔒 Güvenlik & Environment Yapılandırması

Projedeki hassas veriler (`LLM_API_KEY` vb.) root dizinindeki `.gitignore` kuralları ile koruma altındadır ve Git takibinden hariç tutulmuştur. 

Projeyi klonlayan kullanıcılar `backend/.env.example` dosyasını referans alarak kendi `backend/.env` dosyalarını oluşturmalıdır:

```env
PORT=8000
HOST=0.0.0.0
ENV=development

LLM_API_KEY=your_actual_api_key_here
LLM_BASE_URL=https://api.your-llm-provider.com/v1
LLM_MODEL=qwen-397b
```

---

## 📝 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
