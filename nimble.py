import nimblephysics as nimble
import os


# Load the model
custom_opensim: nimble.biomechanics.OpenSimFile = nimble.biomechanics.OpenSimParser.parseOsim(os.path.join(
    os.path.dirname(__file__), "./assets/models/3D/Fullbody_TLModels_v2.0_OS4x/MaleFullBodyModel_v2.0_OS4.osim"))
skeleton: nimble.dynamics.Skeleton = custom_opensim.skeleton

# Print the skeleton's position vector
print(skeleton.getPositions())

# Print the names of the skeleton's degrees of freedom
print([skeleton.getDofByIndex(i).getName() for i in range(skeleton.getNumDofs())])

# Change the knee position
positions = skeleton.getPositions()
positions[16] = 3.14 / 4
skeleton.setPositions(positions)

velocities = skeleton.getVelocities()
velocities[9] = 1.0
skeleton.setVelocities(velocities)

# Create a GUI
gui = nimble.NimbleGUI()

# Serve the GUI on port 8080
gui.serve(8080)

# Render the skeleton to the GUI
gui.nativeAPI().renderSkeleton(skeleton)

# Block until the GUI is closed
gui.blockWhileServing()