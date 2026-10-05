PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS itinerary_items;
DROP TABLE IF EXISTS itineraries;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS saved_places;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS users;

CREATE TABLE users (user_id INTEGER PRIMARY KEY, created_at TEXT NOT NULL);
CREATE TABLE trips (trip_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT NOT NULL,
  start_date TEXT NOT NULL, end_date TEXT NOT NULL, pace TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id));
CREATE TABLE saved_places (saved_place_id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL,
  poi_name TEXT NOT NULL, source TEXT, saved_at TEXT NOT NULL,
  FOREIGN KEY (trip_id) REFERENCES trips(trip_id));
CREATE TABLE bookings (booking_id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL,
  poi_name TEXT NOT NULL, booking_time TEXT NOT NULL,
  FOREIGN KEY (trip_id) REFERENCES trips(trip_id));
CREATE TABLE itineraries (itinerary_id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL,
  status TEXT NOT NULL, created_at TEXT NOT NULL, confirmed_at TEXT,
  FOREIGN KEY (trip_id) REFERENCES trips(trip_id));
CREATE TABLE itinerary_items (item_id INTEGER PRIMARY KEY, itinerary_id INTEGER NOT NULL,
  poi_name TEXT NOT NULL, visit_date TEXT NOT NULL, sequence_no INTEGER NOT NULL,
  FOREIGN KEY (itinerary_id) REFERENCES itineraries(itinerary_id));
CREATE TABLE events (event_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, trip_id INTEGER NOT NULL,
  event_name TEXT NOT NULL CHECK (event_name IN ('trip_opened','place_saved','plan_started',
  'itinerary_generated','conflict_detected','place_moved','reoptimized','itinerary_confirmed')),
  event_time TEXT NOT NULL, metadata_json TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (trip_id) REFERENCES trips(trip_id));
CREATE INDEX idx_events_trip_time ON events(trip_id, event_time);
