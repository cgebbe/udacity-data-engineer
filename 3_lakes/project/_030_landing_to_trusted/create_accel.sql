CREATE EXTERNAL TABLE IF NOT EXISTS accelerometer_trusted (
  user STRING,
  timeStamp BIGINT,
  x DOUBLE,
  y DOUBLE,
  z DOUBLE,
  shareWithResearchAsOfDate BIGINT
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://udacity-dataengineer-lake-project-s3/accelerometer/trusted';