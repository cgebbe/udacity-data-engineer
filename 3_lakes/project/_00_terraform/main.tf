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
resource "aws_s3_bucket_public_access_block" "access_block" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}
