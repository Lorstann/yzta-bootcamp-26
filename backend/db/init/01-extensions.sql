-- D2: pgvector extension'ını etkinleştir
-- Bu dosya PostgreSQL container ilk açılışında otomatik çalışır.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
