#!/bin/bash

export SRC="./data_from_github"
export DST=s3://udacity-dataengineer-lake-project-s3/data_from_github
aws s3 sync ${SRC}/customer/ ${DST}/customer/landing
aws s3 sync ${SRC}/accelerometer/ ${DST}/accelerometer/landing
aws s3 sync ${SRC}/step_trainer/ ${DST}/step_trainer/landing

