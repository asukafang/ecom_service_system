"""退款申请的轻量持久化存储。

用 JSON 保存退款申请，便于本地演示幂等、状态流转和审计追踪。
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4


DEFAULT_PATH = Path(__file__).resolve().parents[2] / "sessions" / "refund_requests.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _write(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def create_request(order_id: str, reason: str, path: Path = DEFAULT_PATH) -> dict:
    records = _read(path)
    existing = next(
        (r for r in reversed(records)
         if r["order_id"] == order_id and r["status"] in {"pending_confirmation", "completed"}),
        None,
    )
    if existing:
        return existing

    record = {
        "request_id": f"REF-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
        "order_id": order_id,
        "reason": reason,
        "status": "pending_confirmation",
        "created_at": _now(),
        "confirmed_at": None,
    }
    records.append(record)
    _write(path, records)
    return record


def get_request(request_id: str, path: Path = DEFAULT_PATH) -> Optional[dict]:
    return next((r for r in _read(path) if r["request_id"] == request_id), None)


def update_status(request_id: str, status: str, path: Path = DEFAULT_PATH) -> Optional[dict]:
    records = _read(path)
    for record in records:
        if record["request_id"] == request_id:
            record["status"] = status
            if status == "completed":
                record["confirmed_at"] = _now()
            _write(path, records)
            return record
    return None
