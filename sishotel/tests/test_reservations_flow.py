"""Testes E2E cobrindo as regras de negócio do fluxo de reservas."""
from datetime import date, timedelta


def _create_guest(client, **overrides):
    payload = {
        "full_name": "João Teste",
        "document": "00011122233",
        "email": "joao@test.com",
        "phone": "+55-11-91111-0000",
        **overrides,
    }
    r = client.post("/api/v1/guests", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def _create_room(client, **overrides):
    payload = {
        "number": 1001,
        "type": "STANDARD",
        "capacity": 2,
        "price_per_night": "250.00",
        **overrides,
    }
    r = client.post("/api/v1/rooms", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------- #
# CRUDs básicos
# --------------------------------------------------------------------- #
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_get_guest(client):
    g = _create_guest(client)
    r = client.get(f"/api/v1/guests/{g['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "joao@test.com"


def test_duplicate_guest_document(client):
    _create_guest(client)
    r = client.post("/api/v1/guests", json={
        "full_name": "Outro",
        "document": "00011122233",  # mesmo doc
        "email": "outro@test.com",
    })
    assert r.status_code == 409
    assert r.json()["code"] == "DUPLICATE_RESOURCE"


def test_create_room_and_list(client):
    _create_room(client)
    r = client.get("/api/v1/rooms")
    assert r.status_code == 200
    assert len(r.json()) == 1


# --------------------------------------------------------------------- #
# Regras de negócio - Reservas
# --------------------------------------------------------------------- #
def test_create_reservation_happy_path(client):
    g = _create_guest(client)
    room = _create_room(client)
    payload = {
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(date.today() + timedelta(days=2)),
        "checkout_expected": str(date.today() + timedelta(days=5)),
        "guests_count": 2,
    }
    r = client.post("/api/v1/reservations", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "CREATED"
    # 3 diárias * 250 = 750
    assert float(body["estimated_amount"]) == 750.00


def test_invalid_date_range(client):
    g = _create_guest(client)
    room = _create_room(client)
    r = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": "2026-06-10",
        "checkout_expected": "2026-06-08",  # antes do checkin
        "guests_count": 1,
    })
    assert r.status_code == 400  # validation pydantic


def test_capacity_exceeded(client):
    g = _create_guest(client)
    room = _create_room(client, capacity=2)
    r = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(date.today() + timedelta(days=1)),
        "checkout_expected": str(date.today() + timedelta(days=3)),
        "guests_count": 5,  # excede
    })
    assert r.status_code == 400
    assert r.json()["code"] == "CAPACITY_EXCEEDED"


def test_room_unavailable_overlap(client):
    g = _create_guest(client)
    room = _create_room(client)
    base = date.today() + timedelta(days=10)
    # Primeira reserva ocupa o quarto
    client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(base),
        "checkout_expected": str(base + timedelta(days=5)),
        "guests_count": 1,
    })
    # Segundo hóspede tenta sobrepor
    g2 = _create_guest(client, document="99999999", email="ana2@test.com")
    r = client.post("/api/v1/reservations", json={
        "guest_id": g2["id"],
        "room_id": room["id"],
        "checkin_expected": str(base + timedelta(days=2)),
        "checkout_expected": str(base + timedelta(days=6)),
        "guests_count": 1,
    })
    assert r.status_code == 409
    assert r.json()["code"] == "ROOM_UNAVAILABLE"


def test_checkin_window_too_early(client):
    g = _create_guest(client)
    room = _create_room(client)
    future = date.today() + timedelta(days=15)
    res = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(future),
        "checkout_expected": str(future + timedelta(days=2)),
        "guests_count": 1,
    }).json()

    r = client.post(f"/api/v1/reservations/{res['id']}/check-in")
    assert r.status_code == 422
    assert r.json()["code"] == "CHECKIN_WINDOW_VIOLATION"


def test_full_lifecycle_checkin_checkout(client):
    g = _create_guest(client)
    room = _create_room(client)
    today = date.today()
    res = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(today),
        "checkout_expected": str(today + timedelta(days=3)),
        "guests_count": 2,
    }).json()

    # Check-in OK
    r = client.post(f"/api/v1/reservations/{res['id']}/check-in")
    assert r.status_code == 200
    assert r.json()["status"] == "CHECKED_IN"
    assert r.json()["checkin_at"] is not None

    # Check-out OK
    r = client.post(f"/api/v1/reservations/{res['id']}/check-out")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "CHECKED_OUT"
    assert body["final_amount"] is not None
    # diarias = max(1, ...) -> pelo menos 1 diária
    assert float(body["final_amount"]) >= 250.00


def test_cannot_cancel_after_checkin(client):
    g = _create_guest(client)
    room = _create_room(client)
    today = date.today()
    res = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(today),
        "checkout_expected": str(today + timedelta(days=2)),
        "guests_count": 1,
    }).json()

    client.post(f"/api/v1/reservations/{res['id']}/check-in")

    r = client.post(f"/api/v1/reservations/{res['id']}/cancel")
    assert r.status_code == 409
    assert r.json()["code"] == "INVALID_RESERVATION_STATE"


def test_cannot_checkout_without_checkin(client):
    g = _create_guest(client)
    room = _create_room(client)
    today = date.today()
    res = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(today),
        "checkout_expected": str(today + timedelta(days=2)),
        "guests_count": 1,
    }).json()

    r = client.post(f"/api/v1/reservations/{res['id']}/check-out")
    assert r.status_code == 409
    assert r.json()["code"] == "INVALID_RESERVATION_STATE"


def test_cancel_then_room_available_again(client):
    """Reserva CANCELED não bloqueia o quarto no mesmo período."""
    g = _create_guest(client)
    room = _create_room(client)
    base = date.today() + timedelta(days=20)
    res = client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(base),
        "checkout_expected": str(base + timedelta(days=3)),
        "guests_count": 1,
    }).json()

    # Cancela
    client.post(f"/api/v1/reservations/{res['id']}/cancel")

    # Outro hóspede deve conseguir reservar no mesmo período
    g2 = _create_guest(client, document="98765432", email="g2@test.com")
    r = client.post("/api/v1/reservations", json={
        "guest_id": g2["id"],
        "room_id": room["id"],
        "checkin_expected": str(base),
        "checkout_expected": str(base + timedelta(days=3)),
        "guests_count": 1,
    })
    assert r.status_code == 201


def test_cannot_delete_room_with_active_reservation(client):
    g = _create_guest(client)
    room = _create_room(client)
    base = date.today() + timedelta(days=30)
    client.post("/api/v1/reservations", json={
        "guest_id": g["id"],
        "room_id": room["id"],
        "checkin_expected": str(base),
        "checkout_expected": str(base + timedelta(days=2)),
        "guests_count": 1,
    })

    r = client.delete(f"/api/v1/rooms/{room['id']}")
    assert r.status_code == 409
    assert r.json()["code"] == "ROOM_HAS_RESERVATIONS"
