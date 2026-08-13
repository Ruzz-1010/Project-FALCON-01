# SEALED_POD_THERMAL_SYSTEM

Adds a sealed thermal-management assembly to `UPPER_ALL_ELECTRONICS_POD`:
two internal 80 mm recirculation fans, internal airflow baffles, an aluminum
thermal bridge, an external rear heat-sink base with eight fins, and a combined
temperature/humidity sensor bracket.

The design does not create an outside-air opening into the dry pod. Heat crosses
the sealed wall through a clamped thermal interface. Existing components are not
moved, hidden, or deleted.

The shutdown threshold is stored as the unitless parameter
`pod_thermal_shutdown_C = 65` because some Fusion builds reject `degC` in user
parameter expressions.
