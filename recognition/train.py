import os
import json
import cv2
import numpy as np

DATASET_PATH = os.path.join(
    "recognition",
    "dataset"
)

TRAINER_DIR = os.path.join(
    "recognition",
    "trainer"
)

MODEL_PATH = os.path.join(
    TRAINER_DIR,
    "trainer.yml"
)

LABELS_PATH = os.path.join(
    TRAINER_DIR,
    "labels.json"
)


def train_model():

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    faces = []
    labels = []

    employee_labels = {}

    current_label = 0

    if not os.path.exists(DATASET_PATH):
        print("Dataset folder not found.")
        return

    for employee_id in sorted(os.listdir(DATASET_PATH)):

        employee_folder = os.path.join(
            DATASET_PATH,
            employee_id
        )

        if not os.path.isdir(employee_folder):
            continue

        employee_labels[current_label] = employee_id

        for image_name in os.listdir(employee_folder):

            image_path = os.path.join(
                employee_folder,
                image_name
            )

            image = cv2.imread(
                image_path,
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                continue

            faces.append(image)
            labels.append(current_label)

        current_label += 1

    if len(faces) == 0:

        print("No training images found.")
        return

    recognizer.train(
        faces,
        np.array(labels)
    )

    os.makedirs(
        TRAINER_DIR,
        exist_ok=True
    )

    recognizer.save(
        MODEL_PATH
    )

    with open(
        LABELS_PATH,
        "w"
    ) as file:

        json.dump(
            employee_labels,
            file,
            indent=4
        )

    print("=" * 40)
    print("Training Completed")
    print("=" * 40)
    print(f"Employees : {len(employee_labels)}")
    print(f"Images    : {len(faces)}")
    print(f"Model     : {MODEL_PATH}")
    print(f"Labels    : {LABELS_PATH}")
    print("=" * 40)