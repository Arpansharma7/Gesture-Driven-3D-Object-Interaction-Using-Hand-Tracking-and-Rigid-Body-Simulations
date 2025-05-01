import cv2
import mediapipe as mp
import socket
import math
import numpy as np

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,  # Lower detection confidence for better tracking
    min_tracking_confidence=0.5    # Lower tracking confidence for smoother tracking
)

# Socket Setup
server_ip = "127.0.0.1"  # used for Localhosting
server_port = 12347
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Position tracking
previous_positions = []
queue_size = 3  # Number of positions to average (for additional smoothing)

cap = cv2.VideoCapture(0)

# Make sure we have correct camera resolution for better tracking
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting webcam and sending hand position... Press ESC to exit.")

while True:
    success, image = cap.read()
    if not success:
        print("Webcam not detected or error in capture!")
        continue

    image = cv2.flip(image, 1)  # Flip image horizontally for mirror effect
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for MediaPipe
    
    # Process the image
    results = hands.process(image_rgb)

    # Data to send
    wrist_data = "0.5,0.5,0.0|0.0"  # Default value if no hand detected
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Get wrist position
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        
        # Get finger points for gesture recognition
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
        
        # Calculate finger spread as average distance between fingertips
        finger_distances = [
            math.dist([thumb_tip.x, thumb_tip.y], [index_tip.x, index_tip.y]),
            math.dist([index_tip.x, index_tip.y], [middle_tip.x, middle_tip.y]),
            math.dist([middle_tip.x, middle_tip.y], [ring_tip.x, ring_tip.y]),
            math.dist([ring_tip.x, ring_tip.y], [pinky_tip.x, pinky_tip.y])
        ]
        
        avg_finger_spread = sum(finger_distances) / len(finger_distances)
        
        # Create position data
        position = [wrist.x, wrist.y, wrist.z]
        
        # Add to position queue for averaging
        previous_positions.append(position)
        if len(previous_positions) > queue_size:
            previous_positions.pop(0)
        
        # Average positions for additional smoothing if needed
        if len(previous_positions) > 1:
            avg_position = np.mean(previous_positions, axis=0)
            x, y, z = avg_position
        else:
            x, y, z = position
        
        # Format data to send
        wrist_data = f"{x:.5f},{y:.5f},{z:.5f}|{avg_finger_spread:.5f}"
        
        # Send the data
        sock.sendto(wrist_data.encode(), (server_ip, server_port))

        # Visual feedback
        img_height, img_width, _ = image.shape
        x_min = min([lm.x for lm in hand_landmarks.landmark]) * img_width
        y_min = min([lm.y for lm in hand_landmarks.landmark]) * img_height
        x_max = max([lm.x for lm in hand_landmarks.landmark]) * img_width
        y_max = max([lm.y for lm in hand_landmarks.landmark]) * img_height

        # Draw rectangle around hand
        cv2.rectangle(
            image,
            (int(x_min), int(y_min)),
            (int(x_max), int(y_max)),
            color=(0, 255, 0),  # Green color
            thickness=2,
        )

        # Add position info to display
        cv2.putText(
            image,
            f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        
        # Add spread info
        cv2.putText(
            image,
            f"Spread: {avg_finger_spread:.2f}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        # Draw hand landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                color=(0, 255, 255), thickness=2, circle_radius=2),
            connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                color=(0, 255, 0), thickness=2)
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
