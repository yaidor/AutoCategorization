from pathlib import Path

from app.services.csv_ingest import _hash_transcript, _normalize_header, parse_csv_bytes

FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_header_strips_accents() -> None:
    assert _normalize_header("Transcripción") == "transcripcion"
    assert _normalize_header("Correo Electrónico") == "correo_electronico"
    assert _normalize_header("Número de Teléfono") == "numero_de_telefono"
    assert _normalize_header("Fecha de la Reunión") == "fecha_de_la_reunion"


def test_normalize_header_lowercases_and_replaces_spaces() -> None:
    assert _normalize_header("Vendedor Asignado") == "vendedor_asignado"
    assert _normalize_header("FECHA DE LA REUNION") == "fecha_de_la_reunion"
    assert _normalize_header("  Closed  ") == "closed"


def test_hash_transcript_is_deterministic_and_64_chars() -> None:
    h1 = _hash_transcript("hola mundo")
    h2 = _hash_transcript("hola mundo")
    assert h1 == h2
    assert len(h1) == 64


def test_hash_transcript_distinguishes_inputs() -> None:
    assert _hash_transcript("hola") != _hash_transcript("Hola")
    assert _hash_transcript("hola") != _hash_transcript("hola ")


def test_parse_sample_csv_separates_valid_from_errors() -> None:
    data = (FIXTURES / "sample.csv").read_bytes()
    rows, errors = parse_csv_bytes(data)

    assert len(rows) == 3
    assert len(errors) >= 2

    error_rows = {err.row for err in errors}
    assert 5 in error_rows
    assert 6 in error_rows


def test_parse_sample_csv_row_fields_are_typed() -> None:
    data = (FIXTURES / "sample.csv").read_bytes()
    rows, _ = parse_csv_bytes(data)

    toro = next(r for r in rows if r.seller_name == "Toro")
    assert toro.name == "Cliente Uno"
    assert toro.email == "uno@example.com"
    assert toro.phone == "56911111111"
    assert toro.closed is True
    assert toro.meeting_date.isoformat() == "2024-01-15"


def test_parse_handles_accented_headers() -> None:
    csv_data = (
        "Nombre,Correo Electrónico,Número de Teléfono,Fecha de la Reunión,"
        "Vendedor asignado,closed,Transcripción\n"
        "Cliente,c@example.com,5691,2024-01-01,Toro,1,Texto.\n"
    ).encode()
    rows, errors = parse_csv_bytes(csv_data)
    assert errors == []
    assert len(rows) == 1
    assert rows[0].name == "Cliente"


def test_parse_empty_email_becomes_none() -> None:
    data = (FIXTURES / "sample.csv").read_bytes()
    rows, _ = parse_csv_bytes(data)

    zorro = next(r for r in rows if r.seller_name == "Zorro")
    assert zorro.email is None
    assert zorro.phone == "56933333333"


def test_parse_missing_required_headers() -> None:
    csv_data = b"Nombre,closed\nX,1\n"
    rows, errors = parse_csv_bytes(csv_data)
    assert rows == []
    assert len(errors) == 1
    assert "faltantes" in errors[0].message.lower()


def test_parse_empty_csv() -> None:
    rows, errors = parse_csv_bytes(b"")
    assert rows == []
    assert len(errors) == 1


def test_parse_strips_utf8_bom() -> None:
    csv_data = (
        "﻿Nombre,Correo Electronico,Numero de Telefono,Fecha de la Reunion,"
        "Vendedor asignado,closed,Transcripcion\n"
        "Cliente,c@example.com,5691,2024-01-01,Toro,1,Texto.\n"
    ).encode()
    rows, errors = parse_csv_bytes(csv_data)
    assert errors == []
    assert len(rows) == 1
