# SisHotel — Sistema de Reserva de Hotel

> **FIAP · 3ESPR · 2026 · Profa. Damiana Costa · Arquitetura Orientada a Serviço · CP2 — Semana 10**

API REST para gestão de reservas de hotel cobrindo o ciclo de vida **reserva → check-in → check-out**, implementada em **Python + FastAPI** com arquitetura em 3 camadas (Controller → Service → Repository).

---

## 📋 Sumário

- [Stack](#-stack)
- [Como executar](#-como-executar)
- [Banco de dados, migrações e seed](#-banco-de-dados-migrações-e-seed)
- [Contrato da API (Swagger/OpenAPI)](#-contrato-da-api-swaggeropenapi)
- [Endpoints](#-endpoints)
- [Exemplos de requisição (cURL)](#-exemplos-de-requisição-curl)
- [Regras de negócio implementadas](#-regras-de-negócio-implementadas)
- [Tratamento de erros](#-tratamento-de-erros)
- [Decisões de arquitetura (ADRs)](#-decisões-de-arquitetura-adrs)
- [Diagrama das camadas](#-diagrama-das-camadas)
- [Testes](#-testes)
- [Estrutura do projeto](#-estrutura-do-projeto)

---

## 🧰 Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Framework Web | FastAPI 0.115 |
| ORM / Repository | SQLAlchemy 2.0 |
| Migrações versionadas | Alembic 1.13 |
| Validação de DTOs | Pydantic 2.9 |
| Banco de dados | SQLite (in-file por padrão, ou in-memory) |
| Testes | pytest 8.3 |
| Servidor ASGI | Uvicorn |

> **Nota sobre o banco**: o enunciado sugere H2/MySQL/PostgreSQL. Como **H2 é exclusivo do mundo Java**, o equivalente prático em Python é **SQLite** (também zero-config e in-memory opcional). O `DATABASE_URL` é configurável via `.env`, então migrar para PostgreSQL é trocar uma linha.

---

## 🚀 Como executar

### Pré-requisitos
- Python **3.11 ou superior** instalado
- `pip` disponível

### Passo a passo

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd sishotel

# 2. Criar e ativar virtualenv
python -m venv .venv
source .venv/bin/activate         # Linux / macOS
# .venv\Scripts\activate           # Windows PowerShell

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Copiar arquivo de configuração
cp .env.example .env

# 5. Rodar migrações (cria schema + seed inicial)
alembic upgrade head

# 6. Subir a API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A aplicação fica disponível em:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Healthcheck**: http://localhost:8000/health

---

## 🗄️ Banco de dados, migrações e seed

### Configuração

A URL do banco é controlada pela variável `DATABASE_URL` no `.env`:

```env
# SQLite local (padrão)
DATABASE_URL=sqlite:///./sishotel.db

# SQLite in-memory (útil para testes manuais voláteis)
# DATABASE_URL=sqlite:///:memory:

# PostgreSQL (exemplo)
# DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/sishotel
```

### Migrações (Alembic)

| Versão | Arquivo | O que faz |
|---|---|---|
| **V1** | `alembic/versions/0001_init.py` | Cria tabelas `guests`, `rooms`, `reservations`, índices e constraints |
| **V2** | `alembic/versions/0002_seed.py` | Insere dados iniciais (2 hóspedes, 3 quartos e 1 reserva exemplo) |

Comandos úteis:

```bash
alembic upgrade head        # aplica todas as migrações
alembic downgrade -1        # reverte a última
alembic history             # lista migrações
alembic current             # versão atual aplicada
```

### Seed (dados iniciais)

Após `alembic upgrade head`, o banco já vem com:

**Hóspedes**:
- `11111111-1111-1111-1111-111111111111` — Ana Silva
- `22222222-2222-2222-2222-222222222222` — Bruno Souza

**Quartos**:
- `aaaaaaaa-...` — Quarto 101, STANDARD, R$ 250/diária
- `bbbbbbbb-...` — Quarto 201, DELUXE,   R$ 380/diária
- `cccccccc-...` — Quarto 301, SUITE,    R$ 520/diária

**Reserva exemplo**: `99999999-...` (Ana no Quarto 101, status `CREATED`).

---

## 📄 Contrato da API (Swagger/OpenAPI)

O FastAPI gera o contrato **automaticamente** a partir dos DTOs e routers:

- **Swagger UI interativo**: http://localhost:8000/docs
- **OpenAPI 3.1 JSON**: http://localhost:8000/openapi.json

> Para um arquivo estático, basta `curl http://localhost:8000/openapi.json > docs/openapi.json` após subir a aplicação.

---

## 🛣️ Endpoints

### Hóspedes (`/api/v1/guests`)

| Método | Path | Descrição | Status sucesso |
|---|---|---|---|
| `GET`    | `/api/v1/guests`             | Lista todos                 | 200 |
| `GET`    | `/api/v1/guests/{id}`        | Busca por ID                | 200 |
| `POST`   | `/api/v1/guests`             | Cria hóspede                | 201 |
| `PUT`    | `/api/v1/guests/{id}`        | Atualiza hóspede            | 200 |
| `DELETE` | `/api/v1/guests/{id}`        | Remove hóspede              | 204 |

### Quartos (`/api/v1/rooms`)

| Método | Path | Descrição | Status sucesso |
|---|---|---|---|
| `GET`    | `/api/v1/rooms`              | Lista todos                 | 200 |
| `GET`    | `/api/v1/rooms/{id}`         | Busca por ID                | 200 |
| `POST`   | `/api/v1/rooms`              | Cria quarto                 | 201 |
| `PUT`    | `/api/v1/rooms/{id}`         | Atualiza quarto             | 200 |
| `DELETE` | `/api/v1/rooms/{id}`         | Remove (se sem reservas)    | 204 |

### Reservas (`/api/v1/reservations`)

| Método | Path | Descrição | Status sucesso |
|---|---|---|---|
| `GET`  | `/api/v1/reservations`                       | Lista todas             | 200 |
| `GET`  | `/api/v1/reservations/{id}`                  | Busca por ID            | 200 |
| `POST` | `/api/v1/reservations`                       | Cria reserva            | 201 |
| `POST` | `/api/v1/reservations/{id}/check-in`         | Realiza check-in        | 200 |
| `POST` | `/api/v1/reservations/{id}/check-out`        | Realiza check-out       | 200 |
| `POST` | `/api/v1/reservations/{id}/cancel`           | Cancela (se CREATED)    | 200 |

---

## 📡 Exemplos de requisição (cURL)

> O arquivo `docs/examples.http` traz a versão completa para REST Client / Insomnia.

### Criar hóspede

```bash
curl -X POST http://localhost:8000/api/v1/guests \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Carlos Pereira",
    "document": "55544433322",
    "email": "carlos@example.com",
    "phone": "+55-11-91234-5678"
  }'
```

**Resposta esperada** (`201 Created`):
```json
{
  "id": "f1e2d3c4-...",
  "full_name": "Carlos Pereira",
  "document": "55544433322",
  "email": "carlos@example.com",
  "phone": "+55-11-91234-5678",
  "created_at": "2026-05-12T13:00:00"
}
```

### Criar quarto

```bash
curl -X POST http://localhost:8000/api/v1/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "number": 401,
    "type": "DELUXE",
    "capacity": 3,
    "price_per_night": 420.00
  }'
```

### Criar reserva

```bash
curl -X POST http://localhost:8000/api/v1/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": "11111111-1111-1111-1111-111111111111",
    "room_id":  "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "checkin_expected":  "2026-06-10",
    "checkout_expected": "2026-06-13",
    "guests_count": 2
  }'
```

**Resposta esperada** (`201 Created`):
```json
{
  "id": "a8b9c0d1-...",
  "guest_id": "11111111-...",
  "room_id":  "bbbbbbbb-...",
  "checkin_expected":  "2026-06-10",
  "checkout_expected": "2026-06-13",
  "checkin_at": null,
  "checkout_at": null,
  "status": "CREATED",
  "estimated_amount": "1140.00",
  "final_amount": null,
  "created_at": "2026-05-12T13:00:00",
  "updated_at": null
}
```

### Check-in

```bash
curl -X POST http://localhost:8000/api/v1/reservations/{id}/check-in
```

### Check-out

```bash
curl -X POST http://localhost:8000/api/v1/reservations/{id}/check-out
```

### Cancelar reserva

```bash
curl -X POST http://localhost:8000/api/v1/reservations/{id}/cancel
```

### Tentar reserva com sobreposição (deve falhar com 409)

```bash
curl -i -X POST http://localhost:8000/api/v1/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": "22222222-2222-2222-2222-222222222222",
    "room_id":  "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "checkin_expected":  "2026-06-06",
    "checkout_expected": "2026-06-08",
    "guests_count": 1
  }'
```

**Resposta esperada** (`409 Conflict`):
```json
{
  "code": "ROOM_UNAVAILABLE",
  "message": "Quarto indisponível no período solicitado (sobreposição de reservas)",
  "timestamp": "2026-05-12T13:00:00.000Z",
  "details": null
}
```

---

## 📐 Regras de negócio implementadas

Todas as regras do enunciado estão na camada **Service** (`app/services/`), com exceções dedicadas no domínio:

| # | Regra | Onde | Erro / Status |
|---|---|---|---|
| 1 | `checkout_expected > checkin_expected` | `ReservationCreate.validate_dates` + `ReservationService.create` | `INVALID_DATE_RANGE` / **400** |
| 2 | Disponibilidade do quarto (sem sobreposição, ignorando CANCELED) | `ReservationRepository.find_overlapping` | `ROOM_UNAVAILABLE` / **409** |
| 3 | `guests_count <= room.capacity` | `ReservationService.create` | `CAPACITY_EXCEEDED` / **400** |
| 4 | FSM: `CREATED → CHECKED_IN → CHECKED_OUT` ou `CREATED → CANCELED` | `ReservationService.check_in/check_out/cancel` | `INVALID_RESERVATION_STATE` / **409** |
| 5 | Janela de check-in: somente a partir de `checkin_expected` | `ReservationService.check_in` | `CHECKIN_WINDOW_VIOLATION` / **422** |
| 6 | `final_amount = max(1, dias) × price_per_night` | `ReservationService.check_out` | — |
| 7 | Não excluir quarto com reservas ativas (use `INATIVO`) | `RoomService.delete` | `ROOM_HAS_RESERVATIONS` / **409** |

**Regra de sobreposição** (conforme enunciado):
> Conflito se `entradaA < saídaB` **E** `entradaB < saídaA` no mesmo quarto, com status diferente de CANCELED.

---

## ⚠️ Tratamento de erros

Todos os erros respondem com um **payload padronizado** (`ErrorResponse`):

```json
{
  "code": "ROOM_UNAVAILABLE",
  "message": "Quarto indisponível no período solicitado (sobreposição de reservas)",
  "timestamp": "2026-05-12T13:00:00.000Z",
  "details": null
}
```

| Categoria | HTTP | Quando |
|---|---|---|
| Validação de campo (DTO) | **400** | Pydantic detecta tipo/tamanho/formato inválido |
| Regra de domínio simples | **400** | `InvalidDateRange`, `CapacityExceeded` |
| Recurso não existe | **404** | `*NotFoundException` |
| Conflito de estado/duplicidade | **409** | `RoomUnavailable`, `InvalidReservationState`, `DuplicateResource`, `RoomHasReservations`, `RoomInactive` |
| Política de janela | **422** | `CheckinWindowViolation` |
| Falha inesperada | **500** | Qualquer exceção não tratada |

Os handlers globais ficam em `app/exceptions/handlers.py`.

---

## 🏛️ Decisões de arquitetura (ADRs)

Veja `docs/adr/` para as ADRs detalhadas:

- **[ADR-001](docs/adr/0001-arquitetura-em-tres-camadas.md)** — Adotar arquitetura em 3 camadas (Controller → Service → Repository)
- **[ADR-002](docs/adr/0002-sqlite-em-vez-de-h2.md)** — Usar SQLite como equivalente do H2 (compatível com PostgreSQL via SQLAlchemy)
- **[ADR-003](docs/adr/0003-tratamento-de-erros-padronizado.md)** — Tratamento centralizado de exceções com payload padronizado

---

## 📊 Diagrama das camadas

```
┌──────────────────────────────────────────────────────────────────┐
│                        Cliente HTTP                              │
│              (curl / Postman / Swagger UI / app)                 │
└──────────────────────────────┬───────────────────────────────────┘
                               │  JSON
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  CONTROLLER (app/routers/)                                       │
│  - FastAPI APIRouter                                             │
│  - Recebe DTOs validados pelo Pydantic                           │
│  - Mapeia HTTP ↔ Service                                         │
│  - Define status codes e responses                               │
└──────────────────────────────┬───────────────────────────────────┘
                               │  DTOs
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  SERVICE / DOMÍNIO (app/services/)                               │
│  - Implementa regras de negócio                                  │
│  - FSM da Reserva (CREATED→CHECKED_IN→CHECKED_OUT / CANCELED)    │
│  - Lança exceções de domínio (DomainException)                   │
│  - Faz commit/rollback de transações                             │
└──────────────────────────────┬───────────────────────────────────┘
                               │  Entidades
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  REPOSITORY / DAO (app/repositories/)                            │
│  - Acesso a dados encapsulado                                    │
│  - Consultas tipadas via SQLAlchemy 2.0                          │
│  - find_overlapping(), has_active_reservations_for_room(), etc.  │
└──────────────────────────────┬───────────────────────────────────┘
                               │  SQL
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  PERSISTÊNCIA                                                    │
│  - SQLAlchemy ORM (app/models/)                                  │
│  - Alembic migrations (alembic/versions/)                        │
│  - SQLite / PostgreSQL                                           │
└──────────────────────────────────────────────────────────────────┘

  ─ Transversais ─
  • app/schemas/    → DTOs Pydantic (entrada/saída) + ErrorResponse
  • app/exceptions/ → Exceções de domínio + handlers globais
  • app/config.py   → Settings via .env
```

### FSM da Reserva

```
              ┌─────────────┐
              │   CREATED   │ ◄─── POST /reservations
              └──────┬──────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             │
  ┌─────────┐  ┌──────────┐        │
  │ CANCELED│  │CHECKED_IN│ ◄──────┘  POST /{id}/check-in
  └─────────┘  └────┬─────┘
                    │
                    ▼
              ┌────────────┐
              │CHECKED_OUT │ ◄─── POST /{id}/check-out
              └────────────┘
```

---

## 🧪 Testes

A suíte cobre as principais regras de negócio em testes E2E (via `TestClient` do FastAPI sobre SQLite in-memory):

```bash
pytest -v
```

Testes incluídos (`tests/test_reservations_flow.py`):
- ✅ Healthcheck
- ✅ CRUD básico de hóspedes e quartos
- ✅ Duplicidade de documento → 409
- ✅ Reserva happy-path com cálculo de valor estimado
- ✅ Datas inválidas → 400
- ✅ Capacidade excedida → 400
- ✅ Sobreposição de período → 409
- ✅ Check-in fora da janela → 422
- ✅ Ciclo completo (create → check-in → check-out) com `final_amount`
- ✅ Cancelar após check-in → 409
- ✅ Check-out sem check-in → 409
- ✅ Reserva cancelada libera o quarto
- ✅ Não excluir quarto com reservas ativas → 409

---

## 📂 Estrutura do projeto

```
sishotel/
├── app/
│   ├── __init__.py
│   ├── main.py                       # Entry point (cria FastAPI app)
│   ├── config.py                     # Settings via Pydantic
│   ├── db/
│   │   └── database.py               # Engine, SessionLocal, Base, get_db
│   ├── models/                       # SQLAlchemy ORM
│   │   ├── guest.py
│   │   ├── room.py
│   │   └── reservation.py
│   ├── schemas/                      # DTOs Pydantic
│   │   ├── guest.py
│   │   ├── room.py
│   │   ├── reservation.py
│   │   └── error.py
│   ├── repositories/                 # Camada DAO
│   │   ├── guest_repository.py
│   │   ├── room_repository.py
│   │   └── reservation_repository.py
│   ├── services/                     # Regras de negócio
│   │   ├── guest_service.py
│   │   ├── room_service.py
│   │   └── reservation_service.py
│   ├── routers/                      # Controllers (REST endpoints)
│   │   ├── guests.py
│   │   ├── rooms.py
│   │   └── reservations.py
│   └── exceptions/
│       ├── domain.py                 # Exceções de domínio
│       └── handlers.py               # Handlers globais FastAPI
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_init.py              # V1 — schema
│       └── 0002_seed.py              # V2 — seed
├── tests/
│   ├── conftest.py
│   └── test_reservations_flow.py
├── docs/
│   ├── adr/
│   │   ├── 0001-arquitetura-em-tres-camadas.md
│   │   ├── 0002-sqlite-em-vez-de-h2.md
│   │   └── 0003-tratamento-de-erros-padronizado.md
│   └── examples.http
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 👥 Grupo

> Preencher com os nomes e RMs dos integrantes (até 5).

- Nome — RM
- Nome — RM
- Nome — RM
- Nome — RM
- Nome — RM

---

## 📜 Licença

Projeto acadêmico — FIAP 2026.
