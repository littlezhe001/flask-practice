import cv2

from flask import jsonify
from ultralytics import YOLO
from tqdm import tqdm

# 初始化模型
model = YOLO(r"E:\Anaconda3\Lib\site-packages\nudenet\640m.pt")

# 敏感类别定义（可根据需要调整）
SENSITIVE_CLASSES = [
    "FEMALE_GENITALIA_COVERED", "FEMALE_BREAST_EXPOSED",
    "FEMALE_BREAST_COVERED", "BUTTOCKS_EXPOSED",
    "MALE_GENITALIA_EXPOSED", "ANUS_EXPOSED"
]


def process_frame(frame, conf_threshold=0.5):
    """处理单帧并返回检测结果"""
    results = model(frame, verbose=False)
    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            conf = float(box.conf[0].item())

            if class_name in SENSITIVE_CLASSES and conf >= conf_threshold:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": {
                        "xmin": x1,
                        "ymin": y1,
                        "xmax": x2,
                        "ymax": y2
                    }
                })

    # 在帧上绘制检测框
    for det in detections:
        bbox = det["bbox"]
        cv2.rectangle(frame,
                      (int(bbox["xmin"]), int(bbox["ymin"])),
                      (int(bbox["xmax"]), int(bbox["ymax"])),
                      (0, 0, 255), 2)
        label = f"{det['class_name']} {det['confidence']:.2f}"
        cv2.putText(frame, label,
                    (int(bbox["xmin"]), int(bbox["ymin"]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return frame, detections


def video_to_json(video_path, output_path=None, frame_skip=5, conf_threshold=0.5):
    """处理视频并生成检测报告"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 初始化输出视频
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 准备检测结果
    report = {
        "video_info": {
            "path": video_path,
            "fps": fps,
            "duration": duration,
            "resolution": f"{width}x{height}"
        },
        "detections": [],
        "sensitive_frames_count": 0
    }

    # 使用进度条
    pbar = tqdm(total=total_frames, desc="处理视频")

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % frame_skip == 0:
            processed_frame, detections = process_frame(frame.copy(), conf_threshold)

            if detections:
                report["sensitive_frames_count"] += 1
                report["detections"].append({
                    "frame_index": frame_index,
                    "timestamp": frame_index / fps,
                    "detection": detections
                })

            if output_path:
                out.write(processed_frame)

        frame_index += 1
        pbar.update(1)

    cap.release()
    if output_path:
        out.release()
    pbar.close()

    return report
