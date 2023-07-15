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

# Script generated for node step_trainer_landing
step_trainer_landing_node1689420956122 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="step_trainer_landing",
    transformation_ctx="step_trainer_landing_node1689420956122",
)

# Script generated for node customer_curated
customer_curated_node1689420954353 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="customer_curated",
    transformation_ctx="customer_curated_node1689420954353",
)

# Script generated for node SQL Query
SqlQuery0 = """
SELECT *
FROM s
WHERE serialnumber in (SELECT serialnumber from c)
"""
SQLQuery_node1689420989781 = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={
        "c": customer_curated_node1689420954353,
        "s": step_trainer_landing_node1689420956122,
    },
    transformation_ctx="SQLQuery_node1689420989781",
)

# Script generated for node Amazon S3
AmazonS3_node1689421055640 = glueContext.getSink(
    path="s3://udacity-dataengineer-lake-project-s3/step_trainer/trusted/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1689421055640",
)
AmazonS3_node1689421055640.setCatalogInfo(
    catalogDatabase="default", catalogTableName="step_trainer_trusted"
)
AmazonS3_node1689421055640.setFormat("json")
AmazonS3_node1689421055640.writeFrame(SQLQuery_node1689420989781)
job.commit()
