
using ControlSystems
using GLMakie

println("⛺ [basecamp] TU Delft Julia Systems & Control Environment Init.")

# Define a standard continuous-time transfer function: G(s) = 1 / (s^2 + 2s + 1)
sys = tf(1, [1, 2, 1])

println("System Transfer Function:")
display(sys)

# Calculate step response metadata
y, t, x = step(sys, 10)

# Quick native GLMakie detached window plotting test
fig, ax, l = lines(t, y[:], color = :blue, linewidth = 2, 
                   axis = (title = "Step Response", xlabel = "Time (s)", ylabel = "Amplitude"))
display(fig)
