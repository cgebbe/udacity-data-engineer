CREATE EXTERNAL TABLE IF NOT EXISTS accelerometer_landing (
  user STRING,
  timeStamp BIGINT,
  x DOUBLE,
  y DOUBLE,
  z DOUBLE
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://udacity-dataengineer-lake-project-s3/data_from_github/accelerometer/landing';