#!/bin/bash
# aws s3 sync ./data/customers/ s3://udacity-dataengineer-lake-project-s3/customer/landing
# aws s3 sync ./data/accelerometer/ s3://udacity-dataengineer-lake-project-s3/accelerometer/landing
# aws s3 sync ./data/step_trainer/ s3://udacity-dataengineer-lake-project-s3/step_trainer/landing

aws s3 sync ./data_correct/accelerometer/ s3://udacity-dataengineer-lake-project-s3/accelerometer/landing_correct
aws s3 sync ./data_correct/step_trainer/ s3://udacity-dataengineer-lake-project-s3/step_trainer/landing_correct
aws s3 sync ./data_correct/customers/ s3://udacity-dataengineer-lake-project-s3/customer/landing_correct

# aws s3 sync ./data/dummy/ s3://udacity-dataengineer-lake-project-s3/dummy/landing