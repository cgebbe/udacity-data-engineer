CREATE EXTERNAL TABLE IF NOT EXISTS accelerometer_landing (
    user STRING,
    timeStamp BIGINT,
    x FLOAT,
    y FLOAT,
    z FLOAT
)
--ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://udacity-dataengineer-lake-project-s3/accelerometer/landing_correct';
