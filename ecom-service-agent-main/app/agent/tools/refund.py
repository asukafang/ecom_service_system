from app.agent.tools.mock_data import ORDERS
from app.agent.tools.refund_store import create_request, get_request, update_status


def prepare_refund(order_id: str, reason: str) -> dict:
    """校验订单并创建待确认退款申请，不会直接执行退款。"""
    order = ORDERS.get(order_id)
    if not order:
        return {"success": False, "error": f"未找到订单 {order_id}，请核实订单号"}
    if order["status"] == "refund_processing":
        return {"success": False, "error": "该订单已有退款申请正在处理中，请耐心等待"}

    request = create_request(order_id, reason)
    if request["status"] == "completed":
        return {
            "success": True,
            "already_completed": True,
            "request_id": request["request_id"],
            "message": "该订单已经完成退款，无需重复申请。",
        }
    return {
        "success": True,
        "requires_confirmation": True,
        "request_id": request["request_id"],
        "order_id": order_id,
        "reason": reason,
        "estimated_arrival": "1-3 个工作日",
        "message": "退款申请已生成，请向用户展示信息并等待用户明确确认。",
    }


def confirm_refund(request_id: str) -> dict:
    """在用户明确确认后执行退款，重复确认保持幂等。"""
    request = get_request(request_id)
    if not request:
        return {"success": False, "error": f"未找到退款申请 {request_id}"}
    if request["status"] == "completed":
        return {"success": True, "already_completed": True, "request_id": request_id,
                "message": "该退款申请已完成，不会重复扣款。"}
    if request["status"] != "pending_confirmation":
        return {"success": False, "error": f"退款申请当前状态为 {request['status']}，无法确认"}

    updated = update_status(request_id, "completed")
    return {
        "success": True,
        "request_id": request_id,
        "order_id": updated["order_id"],
        "status": "completed",
        "message": f"退款已提交，预计 {updated.get('estimated_arrival', '1-3 个工作日')} 原路到账。",
    }


def apply_refund(order_id: str, reason: str) -> dict:
    """兼容旧调用方：统一转为待确认申请，禁止直接退款。"""
    return prepare_refund(order_id, reason)
