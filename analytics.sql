-- 01 Trip activity
SELECT trip_id, COUNT(*) AS events, MIN(event_time) AS first_event, MAX(event_time) AS last_event
FROM events GROUP BY trip_id;

-- 02 Planning starts
SELECT COUNT(DISTINCT trip_id) AS trips_started FROM events WHERE event_name = 'plan_started';

-- 03 Itinerary-generation status
SELECT t.trip_id, MAX(e.event_name = 'itinerary_generated') AS generated,
       MAX(e.event_name = 'itinerary_confirmed') AS confirmed
FROM trips t LEFT JOIN events e USING (trip_id) GROUP BY t.trip_id;

-- 04 Planning conversion
SELECT 1.0 * COUNT(DISTINCT CASE WHEN event_name='plan_started' THEN trip_id END) /
       NULLIF(COUNT(DISTINCT CASE WHEN event_name='trip_opened' THEN trip_id END), 0) AS planning_conversion
FROM events;

-- 05 Initial plan acceptance: no move before first confirmation
WITH first_confirm AS (SELECT trip_id, MIN(event_time) AS confirmed_at FROM events
  WHERE event_name='itinerary_confirmed' GROUP BY trip_id),
generated AS (SELECT DISTINCT trip_id FROM events WHERE event_name='itinerary_generated')
SELECT 1.0 * SUM(CASE WHEN fc.trip_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM events e WHERE e.trip_id=g.trip_id AND e.event_name='place_moved'
  AND e.event_time < fc.confirmed_at) THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS initial_plan_acceptance
FROM generated g LEFT JOIN first_confirm fc USING (trip_id);

-- 06 Adjustment behaviour
SELECT 1.0 * COUNT(DISTINCT CASE WHEN event_name='place_moved' THEN trip_id END) /
  NULLIF(COUNT(DISTINCT CASE WHEN event_name='itinerary_generated' THEN trip_id END),0) AS adjustment_rate
FROM events;

-- 07 Conflict and re-optimization behaviour
SELECT 1.0 * COUNT(DISTINCT CASE WHEN event_name='conflict_detected' THEN trip_id END) /
  NULLIF(COUNT(DISTINCT CASE WHEN event_name='itinerary_generated' THEN trip_id END),0) AS conflict_rate,
  1.0 * COUNT(DISTINCT CASE WHEN event_name='reoptimized' THEN trip_id END) /
  NULLIF(COUNT(DISTINCT CASE WHEN event_name IN ('plan_started','itinerary_generated','conflict_detected') THEN trip_id END),0) AS reoptimization_rate
FROM events;

-- 08 Average saved POIs
SELECT AVG(place_count) AS average_saved_pois FROM (
  SELECT trip_id, COUNT(*) AS place_count FROM saved_places GROUP BY trip_id
);

-- 09 Modifications before first confirmation
WITH first_confirm AS (SELECT trip_id, MIN(event_time) AS confirmed_at FROM events
  WHERE event_name='itinerary_confirmed' GROUP BY trip_id)
SELECT fc.trip_id, COUNT(e.event_id) AS modifications_before_confirmation
FROM first_confirm fc LEFT JOIN events e ON e.trip_id=fc.trip_id
 AND e.event_name='place_moved' AND e.event_time < fc.confirmed_at GROUP BY fc.trip_id;

-- 10 Time to confirmation and ordered event sequence
WITH milestones AS (SELECT trip_id,
  MIN(CASE WHEN event_name='plan_started' THEN event_time END) AS started_at,
  MIN(CASE WHEN event_name='itinerary_confirmed' THEN event_time END) AS confirmed_at
  FROM events GROUP BY trip_id)
SELECT trip_id, ROUND((julianday(confirmed_at)-julianday(started_at))*24*60,1) AS minutes_to_confirmation
FROM milestones WHERE started_at IS NOT NULL AND confirmed_at IS NOT NULL;
