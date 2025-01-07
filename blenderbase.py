import bpy
import socket
import threading
#creating a link between main code and blender
server_ip = "127.0.0.1" 
server_port = 12347
buffer_size = 1024

# use the name which is of your object inside Blender
target_object_name = "Cube" 
target_object = bpy.data.objects.get(target_object_name)

if not target_object:
    raise ValueError(f"Object '{target_object_name}' not found in Blender.")

# for Smoother movement
last_position = [0.0, 0.0, 0.0]
velocity = [0.0, 0.0, 0.0] 
smooth_factor = 0.1  
filter_factor = 0.3  

# Object scale parameters
min_scale = 0.1  
max_scale = 2.0  

z_threshold = 0.1  

def low_pass_filter(new_value, previous_value, alpha):
    return previous_value + alpha * (new_value - previous_value)

def update_object_properties(data):
    global last_position, velocity
    try:
        wrist_data, finger_spread = data.split("|")
        x, y, z = map(float, wrist_data.split(","))
        finger_distance = float(finger_spread)
        
        smooth_x = low_pass_filter(x * 10 - 5, last_position[0], filter_factor)
        smooth_y = low_pass_filter(y * 10 - 5, last_position[1], filter_factor)
        smooth_z = low_pass_filter(z * 10 - 0, last_position[2], filter_factor)

        velocity[0] = smooth_x - last_position[0]
        velocity[1] = smooth_y - last_position[1]
        velocity[2] = smooth_z - last_position[2]

        target_object.location = (
            smooth_x + velocity[0] * smooth_factor,
            smooth_y + velocity[1] * smooth_factor,
            smooth_z + velocity[2] * smooth_factor,
        )

        if abs(velocity[2]) > z_threshold:
            print("Back-and-forth motion detected!")

        scale_factor = min(max_scale, max(min_scale, finger_distance * 10))
        target_object.scale = (scale_factor, scale_factor, scale_factor)

        # Update last position
        last_position = [smooth_x, smooth_y, smooth_z]

    except Exception as e:
        print(f"Error updating object properties: {e}")

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

listener_thread = threading.Thread(target=socket_listener, daemon=True)
listener_thread.start()

print("started")
