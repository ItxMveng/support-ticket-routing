from support_ticket_routing.data import Ticket
from support_ticket_routing.tfidf import TfidfClassifier, TfidfSettings


def _ticket(i: int, text: str, queue: str, priority: str) -> Ticket:
    return Ticket(
        id=f"t{i}",
        subject="",
        body=text,
        answer="",
        queue=queue,
        priority=priority,
        type="Incident",
        language="en",
    )


TRAIN = [
    _ticket(i, text, queue, priority)
    for i, (text, queue, priority) in enumerate(
        [
            ("invoice charged twice refund payment", "Billing and Payments", "medium"),
            ("payment failed credit card invoice", "Billing and Payments", "medium"),
            ("refund my payment invoice error", "Billing and Payments", "low"),
            ("server down outage cannot connect vpn", "IT Support", "high"),
            ("vpn connection outage server error", "IT Support", "high"),
            ("cannot connect server vpn urgent", "IT Support", "high"),
        ]
        * 3
    )
]


def test_learns_queue_and_gives_a_confidence() -> None:
    model = TfidfClassifier(TRAIN, TfidfSettings(min_df=1))
    [billing, it] = model.predict(
        [
            _ticket(100, "refund invoice payment", "?", "?"),
            _ticket(101, "vpn server down", "?", "?"),
        ]
    )
    assert billing.queue == "Billing and Payments" and it.queue == "IT Support"
    assert it.priority == "high"
    assert billing.confidence is not None and 0.5 < billing.confidence <= 1
    assert not billing.used_llm and billing.input_tokens == 0 and billing.latency_ms > 0
