"""
We used a SQL-query here instead of a Filter
because the Filter returned no rows (job was successful).
I assume it has something to do with NaNs in the rows.
Regex filters on columns with strings worked fine.
"""
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

# Script generated for node customer_landing
customer_landing_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="default",
    table_name="customer_landing",
    transformation_ctx="customer_landing_node1",
)

# Script generated for node SQL Query
SqlQuery0 = """
SELECT *
FROM myDataSource
WHERE sharewithresearchasofdate>0
"""
SQLQuery_node1686608550869 = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={"myDataSource": customer_landing_node1},
    transformation_ctx="SQLQuery_node1686608550869",
)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1686608704103 = glueContext.write_dynamic_frame.from_catalog(
    frame=SQLQuery_node1686608550869,
    database="default",
    table_name="customer_trusted",
    transformation_ctx="AWSGlueDataCatalog_node1686608704103",
)

job.commit()
