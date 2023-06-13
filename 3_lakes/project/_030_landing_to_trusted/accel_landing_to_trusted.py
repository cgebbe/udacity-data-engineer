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

# Script generated for node Select Fields
SelectFields_node1686616987929 = SelectFields.apply(
    frame=Join_node1686616829981,
    paths=["user", "x", "timestamp", "z", "y", "sharewithresearchasofdate"],
    transformation_ctx="SelectFields_node1686616987929",
)

# Script generated for node accel_trusted
accel_trusted_node1686616837684 = glueContext.write_dynamic_frame.from_catalog(
    frame=SelectFields_node1686616987929,
    database="default",
    table_name="accelerometer_trusted",
    transformation_ctx="accel_trusted_node1686616837684",
)

job.commit()
