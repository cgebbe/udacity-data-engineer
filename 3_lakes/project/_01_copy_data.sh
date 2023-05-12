#!/bin/bash
BUCKET="udacity-dataengineer-lake-project-s3"

aws s3 sync ./data/customers/ s3://${BUCKET}/customer/landing
aws s3 sync ./data/accelerometer/ s3://${BUCKET}/accelerometer/landing
aws s3 sync ./data/step_trainer/ s3://${BUCKET}/step_trainer/landing