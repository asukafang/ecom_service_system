from functools import partial

from app.agent.tools.refund import confirm_refund, prepare_refund
from app.agent.tools import refund as refund_module
from app.agent.tools import refund_store


def test_refund_requires_confirmation_and_is_idempotent(tmp_path, monkeypatch):
    path = tmp_path / "refund_requests.json"
    monkeypatch.setattr(refund_module, "create_request", partial(refund_store.create_request, path=path))
    monkeypatch.setattr(refund_module, "get_request", partial(refund_store.get_request, path=path))
    monkeypatch.setattr(refund_module, "update_status", partial(refund_store.update_status, path=path))

    preview = prepare_refund("ORD-20240110-003", "质量问题")
    assert preview["success"] is True
    assert preview["requires_confirmation"] is True
    request_id = preview["request_id"]

    completed = confirm_refund(request_id)
    assert completed["success"] is True
    assert completed["status"] == "completed"

    repeated = confirm_refund(request_id)
    assert repeated["success"] is True
    assert repeated["already_completed"] is True


def test_refund_unknown_order_does_not_create_request(tmp_path, monkeypatch):
    path = tmp_path / "refund_requests.json"
    monkeypatch.setattr(refund_module, "create_request", partial(refund_store.create_request, path=path))
    result = prepare_refund("ORD-404", "不想要了")
    assert result["success"] is False
    assert not path.exists()
