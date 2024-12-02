import bpy
import socket
import threading

# Configuration
server_ip = "127.0.0.1"  # Blender listens on localhost
server_port = 12347
buffer_size = 1024

# Target object name in Blender
target_object_name = "Cube"  # Replace with your object's name
target_object = bpy.data.objects.get(target_object_name)

if not target_object:
    raise ValueError(f"Object '{target_object_name}' not found in Blender.")

# Smooth movement parameters
last_position = [0.0, 0.0, 0.0]
velocity = [0.0, 0.0, 0.0]  # Added velocity for stabilization
smooth_factor = 0.1  # Lower = smoother
filter_factor = 0.3  # Low-pass filter smoothing factor

# Object scale parameters
min_scale = 0.1  # Minimum scale
max_scale = 2.0  # Maximum scale

# Back-and-forth detection threshold
z_threshold = 0.1  # Adjust based on sensitivity for back-and-forth motion

# Function to apply low-pass filtering for smooth movement
def low_pass_filter(new_value, previous_value, alpha):
    return previous_value + alpha * (new_value - previous_value)

# Function to update object location, scale, and detect back-and-forth motion
def update_object_properties(data):
    global last_position, velocity
    try:
        # Parse wrist data (x, y, z) and finger spread (index-thumb distance)
        wrist_data, finger_spread = data.split("|")
        x, y, z = map(float, wrist_data.split(","))
        finger_distance = float(finger_spread)

        # Calculate smoothed position using low-pass filter
        smooth_x = low_pass_filter(x * 10 - 5, last_position[0], filter_factor)
        smooth_y = low_pass_filter(y * 10 - 5, last_position[1], filter_factor)
        smooth_z = low_pass_filter(z * 10 - 0, last_position[2], filter_factor)

        # Update velocity for stabilization (difference between smoothed and previous position)
        velocity[0] = smooth_x - last_position[0]
        velocity[1] = smooth_y - last_position[1]
        velocity[2] = smooth_z - last_position[2]

        # Apply position to the target object
        target_object.location = (
            smooth_x + velocity[0] * smooth_factor,
            smooth_y + velocity[1] * smooth_factor,
            smooth_z + velocity[2] * smooth_factor,
        )

        # Back-and-forth detection based on `z`-axis threshold
        if abs(velocity[2]) > z_threshold:
            print("Back-and-forth motion detected!")

        # Scale object based on finger spread
        scale_factor = min(max_scale, max(min_scale, finger_distance * 10))
        target_object.scale = (scale_factor, scale_factor, scale_factor)

        # Update last position
        last_position = [smooth_x, smooth_y, smooth_z]

    except Exception as e:
        print(f"Error updating object properties: {e}")

# Socket listener
def socket_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((server_ip, server_port))
        print(f"Listening on {server_ip}:{server_port}...")
        while True:
            try:
                data, _ = server_socket.recvfrom(buffer_size)
                update_object_properties(data.decode())
            except Exception as e:
                print(f"Socket error: {e}")
                break

# Start socket listener in a thread
listener_thread = threading.Thread(target=socket_listener, daemon=True)
listener_thread.start()

print("Blender script running. Move your hand to control the object!")
