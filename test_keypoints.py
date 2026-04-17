import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(0)
frame_count = 0

with mp_holistic.Holistic(min_detection_confidence=0.7,
                           min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = holistic.process(image)
        image.flags.writeable = True

        
        lh = np.array([[lm.x, lm.y, lm.z]
            for lm in results.left_hand_landmarks.landmark]).flatten() \
            if results.left_hand_landmarks else np.zeros(63)

        rh = np.array([[lm.x, lm.y, lm.z]
            for lm in results.right_hand_landmarks.landmark]).flatten() \
            if results.right_hand_landmarks else np.zeros(63)

        pose = np.array([[lm.x, lm.y, lm.z]
            for lm in results.pose_landmarks.landmark]).flatten() \
            if results.pose_landmarks else np.zeros(99)

        keypoints = np.concatenate([lh, rh, pose])

        
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"Shape: {keypoints.shape} | "
                  f"Left hand detected: {results.left_hand_landmarks is not None} | "
                  f"Right hand detected: {results.right_hand_landmarks is not None}")
            print("Right hand values:", keypoints[63:72].round(3))
            print("---")

        cv2.imshow("Keypoint Test - Press Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()