# sim — connection:self-tap-m2-pla

**NOTHING IS SIMULATED HERE, and that is a statement not a placeholder.**

The one number this joint needs — the load at which a M2 screw strips the thread it formed in FDM PLA — is not a simulation question we can answer honestly. An FEA of a formed thread in a layered, anisotropic, void-containing printed boss needs a material model calibrated on the SAME resin, layer height, wall count and infill, and no such calibration exists in this workshop. A simulation run without it would produce a number with three decimal places and no truth in it, which is worse than the `null` this folder currently reports.

## What would go here

1. **First the coupon**: printed samples, screw driven to a recorded torque, pulled to failure on a force gauge, n >= 5, mean and spread. That is the calibration.
2. **Then** an FEA that reproduces the coupon before it is trusted on the real bosses.

Order matters. The test comes first; the simulation earns its right to speak by matching it. See `connection.json` `record.open_questions`.
