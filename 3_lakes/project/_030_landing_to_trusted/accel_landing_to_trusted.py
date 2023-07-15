"""
NOTE:
- The Glue table will be created automatically
- This will NOT overwrite data, see https://stackoverflow.com/q/52001781/2135504
- I tried to use the "Select Fields" Operator to reduce column-count, but it didn't work.
"""
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node customer_trusted
customer_trusted_node1686616822194 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="customer_trusted",
    transformation_ctx="customer_trusted_node1686616822194",
)

# Script generated for node accel_landing
accel_landing_node1686616824418 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="accelerometer_landing",
    transformation_ctx="accel_landing_node1686616824418",
)

# Script generated for node Join
Join_node1686616829981 = Join.apply(
    frame1=accel_landing_node1686616824418,
    frame2=customer_trusted_node1686616822194,
    keys1=["user"],
    keys2=["email"],
    transformation_ctx="Join_node1686616829981",
)

# Script generated for node Amazon S3
AmazonS3_node1689416443055 = glueContext.getSink(
    path="s3://udacity-dataengineer-lake-project-s3/accelerometer/trusted/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1689416443055",
)
AmazonS3_node1689416443055.setCatalogInfo(
    catalogDatabase="default", catalogTableName="accelerometer_trusted"
)
AmazonS3_node1689416443055.setFormat("json")
AmazonS3_node1689416443055.writeFrame(Join_node1686616829981)
job.commit()
