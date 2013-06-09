CREATE TABLE reading_points (
  readingpointid integer primary key,
  rpcharttype integer,
  rplinetype integer,
  rpname text,
  rpdescription text,
  rplinecolor text,
  rpvisibility integer,
  unique(rpname)
)

CREATE TABLE sensor_readings (
  id integer primary key,
  sensorid integer not null,
  timestamp datetime not null,
  sensorvalue integer not null,
)
