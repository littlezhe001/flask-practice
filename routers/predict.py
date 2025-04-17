import traceback

from flask import Blueprint, request, jsonify, current_app
import os

from ultralytics import YOLO

predict_bp = Blueprint('predict', __name__)

# 模型检测核心
@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. 验证请求
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Missing filename"}), 400

        # 2. 验证文件路径
        target_folder = "photo"
        full_path = os.path.join(target_folder, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "File not found"}), 404

        # 3. 执行预测
        model = YOLO(r"E:\Anaconda3\Lib\site-packages\nudenet\640m.pt")
        output_dir = r"E:\毕业设计\flask\predict_res"
        results = model.predict(full_path)

        detections = []
        for result in results:
            image_result = {
                "filename": getattr(result, 'path', 'unknown'),
                "objects": [],
                "time": getattr(result, 'speed', {}).get('inference', 0)
            }

            for box in result.boxes:
                image_result["objects"].append({
                    "class_id": int(box.cls[0].item()),
                    "class_name": result.names[box.cls[0].item()],
                    "confidence": float(box.conf[0].item()),
                    "bbox": {
                        "xmin": float(box.xyxy[0][0]),
                        "ymin": float(box.xyxy[0][1]),
                        "xmax": float(box.xyxy[0][2]),
                        "ymax": float(box.xyxy[0][3])
                    }
                })
            detections.append(image_result)

        # 5. 返回成功响应
        return jsonify({
            "success": True,
            "detections": detections
        }),200

    except Exception as e:
        # 6. 捕获所有异常并返回错误响应
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc() if current_app.debug else None
        }), 500