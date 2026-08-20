import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Camera opened:", cap.isOpened())

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    cv2.putText(frame, "SensAI Test - Press Q to quit",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow("SensAI Camera Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Webcam test passed!")