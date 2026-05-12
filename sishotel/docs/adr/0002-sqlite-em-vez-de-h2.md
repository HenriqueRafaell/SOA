# ADR-002 — SQLite como equivalente do H2 + SQLAlchemy para portabilidade

- **Status**: Aceita
- **Data**: 2026-05-04
- **Contexto**: CP2 — Sistema de Reserva de Hotel (FIAP 3ESPR)

## Contexto

O enunciado sugere H2, MySQL ou PostgreSQL. H2 é um banco embarcado em Java; **não há driver oficial para Python**. A stack escolhida foi Python + FastAPI, portanto precisamos do equivalente mais próximo em filosofia (zero-config, in-memory ou single-file) sem perder portabilidade para um banco "de verdade" caso a banca queira testar em ambiente diferente.

## Decisão

**Banco**: SQLite com URL configurável via `.env`:

```env
DATABASE_URL=sqlite:///./sishotel.db        # arquivo local (padrão)
# DATABASE_URL=sqlite:///:memory:           # in-memory (testes)
# DATABASE_URL=postgresql+psycopg2://...    # produção
```

**Acesso a dados**: SQLAlchemy 2.0 (Core + ORM). Justificativa:
- Abstração que permite trocar SQLite ↔ PostgreSQL sem alterar service/repository.
- API estável e tipada com `Mapped[...]`, alinhada a Python moderno.
- Integração nativa com Alembic para migrações versionadas.

**Migrações**: Alembic com `render_as_batch=True` no `env.py` — essencial para SQLite, que não suporta certos `ALTER TABLE` diretamente.

**IDs**: `CHAR(36)` (UUID em string) gerados na aplicação (`default=lambda: str(uuid.uuid4())`), conforme sugestão do enunciado para "máxima portabilidade". Em PostgreSQL pode-se migrar para o tipo nativo `UUID` em uma futura revisão sem mudar o código de domínio.

## Consequências

**Positivas**
- Zero setup: a banca roda `alembic upgrade head && uvicorn ...` e a aplicação já sobe com seed.
- O mesmo código de domínio funciona em SQLite (avaliação) e PostgreSQL (produção real).
- Testes ficam triviais: `sqlite:///:memory:` com `StaticPool` no `conftest.py`.

**Negativas**
- SQLite tem limitações de concorrência e tipos (ex.: `Numeric` armazenado como texto). Não é problema para o escopo do trabalho, mas seria limitante em produção real.
- `Decimal` em SQLite via SQLAlchemy retorna como string em alguns drivers — tratamos isso convertendo explicitamente nos services (`Decimal(room.price_per_night)`).
