# Async Todo & Log API

Hafta 3 Python Backend Projesi.

## Teknolojiler

- Python 3.14
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.0 Async
- Alembic
- Pydantic v2
- Pytest
- Docker Compose

## Özellikler

- Todo oluşturma, listeleme, görüntüleme, güncelleme ve silme
- AuditLog ile işlem geçmişi
- API Key doğrulaması
- Asenkron veritabanı bağlantısı
- Alembic database migration
- Swagger / OpenAPI dokümantasyonu

## Kurulum

Sanal ortam oluştur:

    python -m venv .venv

Sanal ortamı etkinleştir:

    .venv\Scripts\Activate.ps1

Paketleri yükle:

    python -m pip install -r requirements.txt

.env.example dosyasını .env olarak kopyala:

    Copy-Item .env.example .env

PostgreSQL'i başlat:

    docker compose up -d

Migration uygula:

    python -m alembic upgrade head

API'yi başlat:

    python -m uvicorn app.main:app --reload

Swagger adresi:

    http://127.0.0.1:8000/docs

## Testler

    python -m pytest -v

## API Endpointleri

| Method | Endpoint | Açıklama |
|---|---|---|
| GET | / | Ana sayfa |
| POST | /echo | Echo testi |
| POST | /todos | Görev oluştur |
| GET | /todos | Görevleri listele |
| GET | /todos/{todo_id} | Görev detayı |
| PUT | /todos/{todo_id} | Görev güncelle |
| DELETE | /todos/{todo_id} | Görev sil |
| GET | /logs | İşlem geçmişi |

Todo ve Log endpointleri X-API-Key başlığı ile korunmaktadır.
