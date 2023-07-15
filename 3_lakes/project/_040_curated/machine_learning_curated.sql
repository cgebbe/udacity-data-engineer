import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame


def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node step_trusted
step_trusted_node1689426962697 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="step_trainer_trusted",
    transformation_ctx="step_trusted_node1689426962697",
)

# Script generated for node customer_curated
customer_curated_node1689426961478 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="customer_curated",
    transformation_ctx="customer_curated_node1689426961478",
)

# Script generated for node accel_trusted
accel_trusted_node1689426962074 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="accelerometer_trusted",
    transformation_ctx="accel_trusted_node1689426962074",
)

# Script generated for node SQL Query
SqlQuery0 = """
SELECT *
FROM c
INNER JOIN a ON c.email = a.user
INNER JOIN s ON c.serialnumber = s.serialnumber
WHERE a.timestamp = s.sensorreadingtime
"""
SQLQuery_node1689427034697 = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={
        "c": customer_curated_node1689426961478,
        "a": accel_trusted_node1689426962074,
        "s": step_trusted_node1689426962697,
    },
    transformation_ctx="SQLQuery_node1689427034697",
)

# Script generated for node Amazon S3
AmazonS3_node1689427104817 = glueContext.getSink(
    path="s3://udacity-dataengineer-lake-project-s3/machine_learning_curated/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1689427104817",
)
AmazonS3_node1689427104817.setCatalogInfo(
    catalogDatabase="default", catalogTableName="machine_learning_curated"
)
AmazonS3_node1689427104817.setFormat("json")
AmazonS3_node1689427104817.writeFrame(SQLQuery_node1689427034697)
job.commit()
