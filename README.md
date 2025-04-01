**** Gesture-Driven 3D Object Interaction Using Hand Tracking and Rigid Body ****

A project that combines Mediapipe's real-time pose detection with Blender's 3D animation tools. This enables users to create dynamic and interactive 3D physics simulations effortlessly by using hand gestures.

--------Tech Stack --------

Python IDE: PyCharm (for Python main file)

3D Software: Blender 3D (for 3D modeling and animation)

--------Prerequisites--------

Set up a 3D environment in Blender 3D:

Create and name the objects in the scene appropriately.

Configure physics settings:

Set the movable object as a passive rigid body.

Set all interacting objects as active rigid bodies.

--------Libraries Used--------

mediapipe (for hand tracking and gesture recognition)

bpy (Blender's Python API for automation)

opencv (for image processing and real-time tracking)

socket (for network communication if required)

math (for mathematical operations)

--------Installation--------

To set up the environment, install the required dependencies using pip:

                         pip install mediapipe opencv-python numpy

Ensure that you have Blender installed and configured to work with Python scripting.

--------How It Works--------

The Mediapipe library detects and tracks hand gestures in real-time using OpenCV.

The tracked gestures are interpreted into movement commands.

The bpy library communicates with Blender to move the specified object based on user gestures.

Blender's rigid body physics handles object interactions and collisions dynamically.

--------Usage--------

Run the Python script in PyCharm (or any Python IDE of your choice).

Open Blender and load the prepared 3D scene.

Use hand gestures in front of the camera to move objects within the Blender environment.

--------Future Enhancements--------

Improve accuracy of hand gesture recognition.

Implement voice commands alongside gestures for enhanced control.

Add more complex physics interactions like gravity manipulation.

Enable multi-object control using different gestures.

--------Contributing--------

If you'd like to contribute, feel free to fork the repository, create a feature branch, and submit a pull request.

--------License--------
Anyone can use and contribute 

--------Author--------

Arpan Sharm
