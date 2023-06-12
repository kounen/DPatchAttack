# -*- coding: utf-8 -*-
"""Assignment3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CEb75vwTr5gZXuSIsSCA34jMBxhhk-rA
"""

# -q for quiet (display only important logs)
!pip install -q adversarial-robustness-toolbox

# To use my Google Drive resources
from google.colab import drive
import os

# To use FRCNN and DPatch from ART library
# https://adversarial-robustness-toolbox.readthedocs.io/en/latest/modules/estimators/object_detection.html#object-detector-pytorch-faster-rcnn
from art.estimators.object_detection import PyTorchFasterRCNN
# https://adversarial-robustness-toolbox.readthedocs.io/en/latest/modules/attacks/evasion.html#dpatch
from art.attacks.evasion import DPatch

# To manipulate image
from PIL import Image

# For numpy computation
import numpy as np

# Create the ART PyTorchFasterRCNN estimator
frcnn = PyTorchFasterRCNN(
    # 3 channels (RGB) and size 640x640
    input_shape=(3, 640, 640),
    # Pixel values should be clipped between 0 and 255
    clip_values=(0, 255),
    # Color channels are the last dimension
    channels_first=False,
    # Use all the losses provided by Faster R-CNN model
    attack_losses=("loss_classifier", "loss_box_reg", "loss_objectness", "loss_rpn_box_reg"),
    # Use the GPU for computation
    device_type="gpu"
)

# Create the RobustDPatch attack
attack = DPatch(
    # Our trained object detector, here Faster R-CNN model
    estimator=frcnn,
    # (height, width, nb_channels)
    patch_shape=(100, 100, 3),
    # Number of optimization steps
    max_iter=5
)

# GoogleDrive Mount
drive.mount('/content/drive')

image_path = '/content/drive/MyDrive/{EPITECH}/tek4/Korea/CAU/SpringCourses/CyberPhysicalSystem/A3/image.jpg'

# Common Objects in Context (COCO) dataset for Faster R-CNN model
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

def extract_predictions(predictions):
    # Get the predicted class
    predictions_class = [COCO_INSTANCE_CATEGORY_NAMES[i] for i in list(predictions[0]["labels"])]

    # Get the predicted bounding boxes
    predictions_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(predictions[0]["boxes"])]

    # Get the predicted score
    predictions_score = list(predictions[0]["scores"])

    # Get a list of index with score greater than threshold
    threshold = 0.6
    predictions_t = [predictions_score.index(x) for x in predictions_score if x > threshold][-1]

    # Trim the predictions to include only the high-scoring objects
    predictions_boxes = predictions_boxes[: predictions_t + 1]
    predictions_class = predictions_class[: predictions_t + 1]

    return predictions_class, predictions_boxes, predictions_score

with Image.open(image_path).convert('RGB').resize((640, 640)) as image:
    # Display original image
    image.show()
    # Image pre-processing
    image = np.expand_dims(image, axis=0).astype(np.float32)
    # Get original predictions
    original_predictions = extract_predictions(frcnn.predict(image))

    # Generate patch using DPatch attack
    patch = attack.generate(image)
    # Apply Patch
    adversarial_image = attack.apply_patch(image, patch)
    # Get adversarial predictions
    adversarial_predictions = extract_predictions(frcnn.predict(adversarial_image))
    # Generate adversarial image
    adversarial_image = Image.fromarray(np.squeeze(adversarial_image.astype(np.uint8)))
    # Display adversarial image
    adversarial_image.show()