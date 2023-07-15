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

# Script generated for node customer_trusted
customer_trusted_node1689420954353 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="customer_trusted",
    transformation_ctx="customer_trusted_node1689420954353",
)

# Script generated for node accel_trusted
accel_trusted_node1689420956122 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="accelerometer_trusted",
    transformation_ctx="accel_trusted_node1689420956122",
)

# Script generated for node SQL Query
SqlQuery0 = """
SELECT *
FROM c
WHERE email in (SELECT user from a)
"""
SQLQuery_node1689420989781 = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={
        "c": customer_trusted_node1689420954353,
        "a": accel_trusted_node1689420956122,
    },
    transformation_ctx="SQLQuery_node1689420989781",
)

# Script generated for node Amazon S3
AmazonS3_node1689421055640 = glueContext.getSink(
    path="s3://udacity-dataengineer-lake-project-s3/customer/curated/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1689421055640",
)
AmazonS3_node1689421055640.setCatalogInfo(
    catalogDatabase="default", catalogTableName="customer_curated"
)
AmazonS3_node1689421055640.setFormat("json")
AmazonS3_node1689421055640.writeFrame(SQLQuery_node1689420989781)
job.commit()
