import cv2
import os

def is_blurry(image, threshold=30):

    variance = cv2.Laplacian(
        image,
        cv2.CV_64F
    ).var()

    return variance < threshold

def capture_faces(employee_id):

    cascade_path = os.path.join(
        cv2.data.haarcascades,
        "haarcascade_frontalface_default.xml"
    )

    detector = cv2.CascadeClassifier(cascade_path)

    dataset_path = os.path.join(
        "recognition",
        "dataset",
        employee_id
    )

    os.makedirs(
        dataset_path,
        exist_ok=True
    )

    camera = cv2.VideoCapture(0)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    count = 0

    while True:

        success, frame = camera.read()

        if not success:
            break

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:

            if w < 120 or h < 120:
                continue

            face = gray[y:y + h, x:x + w]

            if is_blurry(face):
                cv2.putText(
                    frame,
                    "Blurry Face",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )
                continue

            face = cv2.resize(
                face,
                (200, 200)
            )

            count += 1

            filename = os.path.join(
                dataset_path,
                f"{count}.jpg"
            )

            cv2.imwrite(
                filename,
                face
            )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{count}/100",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            break

        cv2.imshow(
            "Face Registration",
            frame
        )

        key = cv2.waitKey(1)

        if key == 27:
            break

        if count >= 100:
            break

    camera.release()
    cv2.destroyAllWindows()

    return True