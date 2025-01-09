import cv2
import mediapipe as mp
import socket
import math

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

# Socket Setup
server_ip = "127.0.0.1"  # used for Localhosting
server_port = 12347
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)

print("Starting webcam and sending hand position... Press ESC to exit.")

while True:
    success, image = cap.read()
    if not success:
        print("Webcam not detected or error in capture!")
        continue

    image = cv2.flip(image, 1)  # Flip image horizontally for mirror effect
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for MediaPipe
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Wrist co-ordinates (x, y, z)
        wrist = hand_landmarks.landmark[0]

        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        finger_distance = math.dist([thumb_tip.x, thumb_tip.y], [index_tip.x, index_tip.y])

        wrist_data = f"{wrist.x:.5f},{wrist.y:.5f},{wrist.z:.5f}|{finger_distance:.5f}"
        sock.sendto(wrist_data.encode(), (server_ip, server_port))

        img_height, img_width, _ = image.shape
        x_min = min([lm.x for lm in hand_landmarks.landmark]) * img_width
        y_min = min([lm.y for lm in hand_landmarks.landmark]) * img_height
        x_max = max([lm.x for lm in hand_landmarks.landmark]) * img_width
        y_max = max([lm.y for lm in hand_landmarks.landmark]) * img_height

        # Draw rectangle
        cv2.rectangle(
            image,
            (int(x_min), int(y_min)),
            (int(x_max), int(y_max)),
            color=(0, 255, 0),  # Green color
            thickness=2,
        )

        # Label bounding box
        cv2.putText(
            image,
            "Hand Detected",
            (int(x_min), int(y_min) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

    # Show the image with hand tracking
    cv2.imshow("Hand Tracking", image)

    # Break the loop if ESC is pressed
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
