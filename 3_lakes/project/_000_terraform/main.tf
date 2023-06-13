# Run by
# - source .env to export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# - terraform init
# - terraform plan to see applied changes
# - terraform apply

# Define input variables
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
  default     = "udacity-dataengineer-lake-project-vpc"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "udacity-dataengineer-lake-project-s3"
}


# Create the VPC
resource "aws_vpc" "custom_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = var.vpc_name
  }
}

# Create the subnet within the VPC
resource "aws_subnet" "custom_subnet" {
  vpc_id            = aws_vpc.custom_vpc.id
  cidr_block        = "10.0.0.0/24"
  availability_zone = "${var.aws_region}a"
  tags = {
    Name = "${var.vpc_name}-subnet"
  }
}

# Create a route table for the S3 endpoint
resource "aws_route_table" "s3_endpoint_route_table" {
  vpc_id = aws_vpc.custom_vpc.id
}

# Associate the route table with the subnet
resource "aws_route_table_association" "s3_endpoint_route_table_association" {
  subnet_id      = aws_subnet.custom_subnet.id
  route_table_id = aws_route_table.s3_endpoint_route_table.id
}

# Create VPC endpoint for S3
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id              = aws_vpc.custom_vpc.id
  service_name        = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type   = "Gateway"
  route_table_ids     = [aws_route_table.s3_endpoint_route_table.id]
  policy              = <<POLICY
{
  "Statement": [
    {
      "Action": "*",
      "Effect": "Allow",
      "Resource": "*",
      "Principal": "*"
    }
  ]
}
POLICY
}


# Create S3 bucket
resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name
  tags = {
    Name        = var.bucket_name
  }
}

# Block public access to the S3 bucket 
# This was not specified in tutorial?!
# resource "aws_s3_bucket_public_access_block" "access_block" {
#   bucket = aws_s3_bucket.bucket.id

#   block_public_acls   = true
#   block_public_policy = true
#   ignore_public_acls  = true
#   restrict_public_buckets = true
# }

# Create the IAM role that can be assumed by Glue
resource "aws_iam_role" "glue_service_role" {
  name               = "glue-service-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}
data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

# Attach Policy to allows S3 access
resource "aws_iam_role_policy" "s3_access" {
  name   = "S3Access"
  role   = aws_iam_role.glue_service_role.id
  policy = data.aws_iam_policy_document.s3_access.json
}
data "aws_iam_policy_document" "s3_access" {
  statement {
    sid    = "ListObjectsInBucket"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.bucket.arn,
    ]
  }

  statement {
    sid    = "AllObjectActions"
    effect = "Allow"
    actions = [
      "s3:*Object",
    ]
    resources = [
      "${aws_s3_bucket.bucket.arn}/*",
    ]
  }
}


# WARNING: Added later manually: AmazonS3FullAccess" and "AWSGlueConsoleFullAccess
# according to https://knowledge.udacity.com/questions/989390
# but I don't think this was necessary.

# Grant Glue policy for special Glue-specific S3 buckets 
resource "aws_iam_role_policy" "glue_access" {
  name   = "GlueAccess"
  role   = aws_iam_role.glue_service_role.id
  policy = data.aws_iam_policy_document.glue_access.json
}
data "aws_iam_policy_document" "glue_access" {
  statement {
    effect = "Allow"
    actions = [
      "glue:*",
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:ListAllMyBuckets",
      "s3:GetBucketAcl",
      "ec2:DescribeVpcEndpoints",
      "ec2:DescribeRouteTables",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcAttribute",
      "iam:ListRolePolicies",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "cloudwatch:PutMetricData"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:CreateBucket",
      "s3:PutBucketPublicAccessBlock"
    ]
    resources = ["arn:aws:s3:::aws-glue-*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::aws-glue-*/*",
      "arn:aws:s3:::*/*aws-glue-*/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::crawler-public*",
      "arn:aws:s3:::aws-glue-*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:AssociateKmsKey"
    ]
    resources = ["arn:aws:logs:*:*:/aws-glue/*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateTags",
      "ec2:DeleteTags"
    ]
    resources = [
      "arn:aws:ec2:*:*:network-interface/*",
      "arn:aws:ec2:*:*:security-group/*",
      "arn:aws:ec2:*:*:instance/*"
    ]
    condition {
      test     = "ForAllValues:StringEquals"
      variable = "aws:TagKeys"
      values   = ["aws-glue-service-resource"]
    }
  }
}