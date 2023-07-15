CREATE EXTERNAL TABLE IF NOT EXISTS step_trainer_landing (
  sensorReadingTime BIGINT,
  serialNumber VARCHAR(36),
  distanceFromObject INT
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://udacity-dataengineer-lake-project-s3/data_from_github/step_trainer/landing';
