"""
Pi Camera reader + (optional) object classification.

If the MobileNet-SSD model files are present in models/, this will actually
tell you WHAT it saw - pedestrian, two-wheeler, or vehicle. If those files
aren't there yet, it safely falls back to reporting "unknown" so everything
else keeps working - the near-miss rule can still fire off the IMU +
ultrasonic alone. Adding the real model is optional, do it later (see
README.md).
"""
import cv2
import os
import config

CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
    "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
    "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor",
]

RELEVANT_CLASSES = {
    "person": "pedestrian",
    "motorbike": "two-wheeler",
    "bicycle": "two-wheeler",
    "car": "vehicle",
    "bus": "vehicle",
}

_net = None
_model_available = False

if config.USE_OBJECT_DETECTION_MODEL and os.path.exists(config.MODEL_PROTOTXT) and os.path.exists(config.MODEL_WEIGHTS):
    _net = cv2.dnn.readNetFromCaffe(config.MODEL_PROTOTXT, config.MODEL_WEIGHTS)
    _model_available = True
else:
    print("[Camera] Object detection model not found in models/ - camera will report 'unknown' for now.")
    print("[Camera] This is fine - near-miss detection still works using IMU + ultrasonic. See README.md to add it later.")

_picam = None


def _get_camera():
    global _picam
    if _picam is None:
        from picamera2 import Picamera2

        _picam = Picamera2()
        cam_config = _picam.create_preview_configuration(main={"size": (320, 240)})
        _picam.configure(cam_config)
        _picam.start()
    return _picam


def classify_frame():
    """Grabs one frame and returns (object_class, confidence). object_class is
    one of: 'pedestrian', 'two-wheeler', 'vehicle', 'none', or 'unknown'."""
    cam = _get_camera()
    frame = cam.capture_array()

    if not _model_available:
        return "unknown", 0.0

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    _net.setInput(blob)
    detections = _net.forward()

    best_label, best_conf = "none", 0.0
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > config.DETECTION_CONFIDENCE:
            class_id = int(detections[0, 0, i, 1])
            class_name = CLASSES[class_id] if class_id < len(CLASSES) else "unknown"
            if class_name in RELEVANT_CLASSES and confidence > best_conf:
                best_label = RELEVANT_CLASSES[class_name]
                best_conf = float(confidence)

    return best_label, best_conf
