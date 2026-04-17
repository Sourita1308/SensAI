import cv2
import mediapipe as mp

mp_holistic  = mp.solutions.holistic
mp_draw      = mp.solutions.drawing_utils
mp_draw_styles = mp.solutions.drawing_styles


hand_landmark_style = mp_draw.DrawingSpec(
    color=(0, 220, 100), thickness=2, circle_radius=3)
hand_connection_style = mp_draw.DrawingSpec(
    color=(255, 255, 255), thickness=1)
pose_landmark_style = mp_draw.DrawingSpec(
    color=(0, 150, 255), thickness=2, circle_radius=2)

cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5) as holistic:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = holistic.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        
        mp_draw.draw_landmarks(
            image, results.left_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            hand_landmark_style, hand_connection_style)

        
        mp_draw.draw_landmarks(
            image, results.right_hand_landmarks,
            mp_holistic.HAND_CONNECTIONS,
            hand_landmark_style, hand_connection_style)

        
        mp_draw.draw_landmarks(
            image, results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            pose_landmark_style)

        
        lh_status = "LEFT: YES" if results.left_hand_landmarks else "LEFT: NO"
        rh_status = "RIGHT: YES" if results.right_hand_landmarks else "RIGHT: NO"
        cv2.putText(image, lh_status, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0,220,100) if results.left_hand_landmarks else (80,80,80), 2)
        cv2.putText(image, rh_status, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0,220,100) if results.right_hand_landmarks else (80,80,80), 2)
        cv2.putText(image, "Press Q to quit", (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)

        cv2.imshow("SensAI - MediaPipe Landmarks", image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Landmark test complete!")