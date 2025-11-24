from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.qr_service import QRService
from app.extensions.extensions import db

qr_api = Blueprint("qr_api", __name__, url_prefix="/api/qr")
qr_service = QRService()


@qr_api.route("/create", methods=["POST"])
@jwt_required()
def create_qr():
    from app.models.qr_code import QRCode

    data = request.get_json() or {}
    user_id = get_jwt_identity()

    qr_type = data.get("qr_type", "text")
    qr_format = data.get("format", "svg")  # svg | png | jpg
    input_payload = data.get("payload")

    if not input_payload:
        return jsonify({"success": False, "error": "Missing payload"}), 400

    try:
        # 1) Генерираме payload от qr_type
        payload_str = qr_service.build_payload(qr_type, input_payload)

        # 2) Генерираме QR и качваме в R2
        result = qr_service.create_and_upload_qr(
            user_id=user_id,
            payload=payload_str,
            fmt=qr_format,
            size=512
        )

        # 3) Запис в базата
        qr_record = QRCode(
            user_id=user_id,
            qr_type=qr_type,
            payload=payload_str,
            file_path=result["filename"],
        )
        db.session.add(qr_record)
        db.session.commit()

        return jsonify({
            "success": True,
            "url": result["url"],
            "record_id": qr_record.id,
        })

    except Exception as e:
        current_app.logger.exception(f"QR GENERATION ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500



@qr_api.route("/list", methods=["GET"])
@jwt_required()
def list_qr_codes():
    user_id = get_jwt_identity()

    from app.models.qr_code import QRCode

    items = QRCode.query.filter_by(user_id=user_id).order_by(QRCode.created_at.desc()).all()

    result = []
    for qr in items:
        result.append({
            "id": qr.id,
            "qr_type": qr.qr_type,
            "payload": qr.payload,
            "url": qr.file_path,
            "scan_count": qr.scan_count,
            "created_at": qr.created_at.isoformat(),
        })

    return jsonify({"success": True, "items": result}), 200
