# Measurement framework

All measures use trip-level event logic and the simulated demo events are not real telemetry.

Core KPIs:

1. Planning Conversion: trips with `plan_started` divided by trips with `trip_opened`.
2. Initial Plan Acceptance: generated itineraries confirmed without a `place_moved` event before first confirmation, divided by generated itineraries.
3. Adjustment Rate: generated trips containing `place_moved`, divided by generated trips.
4. Conflict Rate: generated trips containing `conflict_detected`, divided by generated trips.
5. Confirmation Rate: generated trips containing `itinerary_confirmed`, divided by generated trips.
6. Time to Confirmed Plan: first confirmation timestamp minus first planning-start timestamp.

Supporting diagnostics are Re-optimization Rate, Average Saved POIs, and Modifications Before Confirmation. The SQL definitions are executable in `sql/analytics.sql`.
