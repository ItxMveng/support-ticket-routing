from pathlib import Path

import pytest

from support_ticket_routing.data import (
    Ticket,
    deduplicate,
    read_split,
    read_tickets,
    select,
    stratified_split,
    write_split,
)


def _ticket(i: int, queue: str = "IT Support", language: str = "en", body: str = "") -> Ticket:
    return Ticket(
        id=f"t{i:05d}",
        subject="",
        body=body or f"message {i}",
        answer="ok",
        queue=queue,
        priority="low",
        type="Incident",
        language=language,
    )


TICKETS = [_ticket(i, queue="IT Support" if i % 2 else "Billing and Payments") for i in range(200)]


def test_split_is_disjoint_complete_and_deterministic() -> None:
    first = stratified_split(TICKETS)
    again = stratified_split(list(reversed(TICKETS)))
    assert first == again
    ids = [i for name in first for i in first[name]]
    assert sorted(ids) == sorted(t.id for t in TICKETS) and len(ids) == len(set(ids))


def test_split_keeps_proportions_in_each_stratum() -> None:
    splits = stratified_split(TICKETS)
    by_id = {t.id: t for t in TICKETS}
    for name, expected in (("train", 70), ("validation", 15), ("test", 15)):
        queues = [by_id[i].queue for i in splits[name]]
        assert queues.count("IT Support") == queues.count("Billing and Payments") == expected


def test_split_depends_on_seed_and_checks_fractions() -> None:
    assert stratified_split(TICKETS, seed=1) != stratified_split(TICKETS, seed=2)
    with pytest.raises(ValueError):
        stratified_split(TICKETS, fractions=(0.5, 0.5, 0.5))


def test_duplicates_are_removed_whatever_the_case_and_spacing() -> None:
    tickets = [_ticket(0, body="Mon VPN  ne marche pas"), _ticket(1, body="mon vpn ne marche pas")]
    kept, removed = deduplicate(tickets)
    assert [t.id for t in kept] == ["t00000"] and removed == ["t00001"]


def test_read_tickets_assigns_row_ids_and_text(tmp_path: Path) -> None:
    path = tmp_path / "tickets.csv"
    path.write_text(
        "subject,body,answer,type,queue,priority,language,version\n"
        'VPN,"Le VPN tombe\nsouvent",Redémarrez,Incident,IT Support,high,en,400\n'
        ",Facture en double,Remboursée,Request,Billing and Payments,low,de,400\n",
        encoding="utf-8",
    )
    tickets = read_tickets(path)
    assert [t.id for t in tickets] == ["t00000", "t00001"]
    assert tickets[0].text == "VPN\nLe VPN tombe\nsouvent"
    assert tickets[1].text == "Facture en double"


def test_split_files_roundtrip(tmp_path: Path) -> None:
    write_split(["t00002", "t00001"], tmp_path / "test.txt")
    ids = read_split(tmp_path / "test.txt")
    assert ids == ["t00002", "t00001"]
    assert [t.id for t in select(TICKETS, ids)] == ids
