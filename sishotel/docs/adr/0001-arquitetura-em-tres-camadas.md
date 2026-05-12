# ADR-001 — Arquitetura em 3 camadas (Controller → Service → Repository)

- **Status**: Aceita
- **Data**: 2026-05-04
- **Contexto**: CP2 — Sistema de Reserva de Hotel (FIAP 3ESPR)

## Contexto

O enunciado exige arquitetura em 3 camadas (MVC) com DTOs para entrada/saída e validação de dados, garantindo separação de responsabilidades entre apresentação, regras de negócio e persistência.

Em FastAPI é tentador colocar toda a lógica no próprio endpoint (router), porque o framework facilita esse caminho. Esse atalho compromete a testabilidade e mistura regras de domínio com detalhes de HTTP.

## Decisão

Adotamos quatro camadas bem definidas, com fluxo unidirecional:

1. **Controller** (`app/routers/`) — `APIRouter` do FastAPI. Responsável por mapear HTTP ↔ Service: recebe DTOs validados pelo Pydantic, chama o service correspondente e devolve o response model. Nenhuma regra de negócio aqui.
2. **Service / Domínio** (`app/services/`) — concentra todas as regras de negócio (FSM, sobreposição, capacidade, janela de check-in, cálculo de valor). Lança exceções de domínio (`DomainException` e subclasses). Faz `commit/rollback` da transação.
3. **Repository / DAO** (`app/repositories/`) — encapsula o acesso a dados. Expõe métodos de domínio (ex.: `find_overlapping`, `has_active_reservations_for_room`) em vez de vazar SQLAlchemy para fora.
4. **Models** (`app/models/`) — entidades SQLAlchemy puras, sem lógica de negócio.

DTOs Pydantic em `app/schemas/` ficam na fronteira de entrada e saída do Controller, garantindo validação antes de chegar no domínio.

## Consequências

**Positivas**
- Cada camada é testável isoladamente (services são testáveis sem subir a aplicação).
- Mudanças no banco (SQLite → PostgreSQL) ou no transporte (REST → gRPC) ficam contidas.
- O código fica fácil de auditar pela banca: cada regra está em um local previsível dentro do service.
- A FSM da reserva e o `find_overlapping` ficam expressos como código de domínio, não como query espalhada.

**Negativas**
- Mais arquivos do que uma abordagem "tudo no router".
- Para CRUDs triviais (ex.: criar hóspede sem regras), o service vira basicamente um passthrough — overhead aceitável em troca de uniformidade.
