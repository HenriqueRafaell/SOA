# ADR-003 — Tratamento centralizado de exceções com payload padronizado

- **Status**: Aceita
- **Data**: 2026-05-04
- **Contexto**: CP2 — Sistema de Reserva de Hotel (FIAP 3ESPR)

## Contexto

O enunciado pede tratamento de exceções, mapeamento correto de status HTTP (400, 404, 409, 422) e payload de erro padronizado (`code`, `message`, `timestamp`). Implementar isso espalhado nos routers (`try/except` em cada endpoint, montando o JSON manualmente) é caminho garantido para inconsistência: mensagens fora do padrão, status code errado, e código duplicado.

## Decisão

Duas peças:

**1. Hierarquia de exceções de domínio** (`app/exceptions/domain.py`)

Uma classe base `DomainException` carrega três atributos de classe que cada subclasse sobrescreve:
- `code: str` — identificador estável e em SCREAMING_SNAKE (ex.: `ROOM_UNAVAILABLE`)
- `status_code: int` — HTTP status correspondente
- `message: str` — mensagem padrão (sobrescritível na instância)

Cada regra do enunciado tem sua exceção dedicada:

| Regra | Exceção | Status |
|---|---|---|
| Datas inválidas | `InvalidDateRangeException` | 400 |
| Sobreposição | `RoomUnavailableException` | 409 |
| Capacidade | `CapacityExceededException` | 400 |
| FSM violada | `InvalidReservationStateException` | 409 |
| Janela de check-in | `CheckinWindowException` | 422 |
| Quarto inativo | `RoomInactiveException` | 409 |
| Quarto com reservas (delete) | `RoomHasReservationsException` | 409 |
| Recurso duplicado | `DuplicateResourceException` | 409 |
| Recurso ausente | `*NotFoundException` | 404 |

Services lançam essas exceções; **nunca** retornam tuplas de erro nem montam HTTPException manualmente.

**2. Handlers globais** (`app/exceptions/handlers.py`)

Registrados via `register_exception_handlers(app)` no `main.py`. Tratam:
- `DomainException` → traduz para JSON com `code`/`message`/`timestamp`/`details` e status apropriado.
- `RequestValidationError` (Pydantic) → 400 com `code=VALIDATION_ERROR` e lista achatada dos campos.
- `IntegrityError` (SQLAlchemy, violação de UNIQUE/FK) → 409 com `DuplicateResource`.
- `HTTPException` (Starlette) → padroniza no mesmo schema.
- `Exception` (catch-all) → 500 com `INTERNAL_SERVER_ERROR`.

Schema do payload em `app/schemas/error.py` (`ErrorResponse`) — referenciado no `responses=` dos routers para aparecer no Swagger.

## Consequências

**Positivas**
- Routers ficam limpos: sem `try/except`, sem montar dict de erro.
- Adicionar uma nova regra = criar uma exceção e lançar do service. O handler já cuida.
- Swagger documenta os erros possíveis por endpoint via `responses={...}`.
- Banca consegue inspecionar o `code` programaticamente, o que ajuda na correção.

**Negativas**
- Mais uma camada para entender no onboarding.
- O catch-all `Exception` → 500 mascara stack trace; em desenvolvimento isso pode atrapalhar — mitigado deixando o `uvicorn --reload` mostrar o traceback no terminal. Em produção real, plugaríamos um Sentry ou similar.
