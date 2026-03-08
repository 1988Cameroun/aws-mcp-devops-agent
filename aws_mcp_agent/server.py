import boto3
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

mcp = FastMCP("AWS DevOps Agent")

@mcp.tool()
def list_ec2_instances() -> str:
    """List all EC2 instances and their current state"""
    ec2 = session.client("ec2")
    response = ec2.describe_instances()
    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = "Unnamed"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
            instances.append({
                "id": instance["InstanceId"],
                "name": name,
                "state": instance["State"]["Name"],
                "type": instance["InstanceType"],
                "region": instance.get("Placement", {}).get("AvailabilityZone", "unknown")
            })
    return json.dumps(instances, indent=2)

@mcp.tool()
def list_s3_buckets() -> str:
    """List all S3 buckets in the account"""
    s3 = session.client("s3")
    response = s3.list_buckets()
    buckets = [{"name": b["Name"], "created": str(b["CreationDate"])}
               for b in response.get("Buckets", [])]
    return json.dumps(buckets, indent=2)

@mcp.tool()
def check_iam_roles() -> str:
    """List IAM roles and their attached policies"""
    iam = session.client("iam")
    response = iam.list_roles()
    roles = []
    for role in response["Roles"][:10]:
        policies = iam.list_attached_role_policies(RoleName=role["RoleName"])
        roles.append({
            "name": role["RoleName"],
            "arn": role["Arn"],
            "policies": [p["PolicyName"] for p in policies["AttachedPolicies"]]
        })
    return json.dumps(roles, indent=2)

@mcp.tool()
def describe_vpc_network() -> str:
    """Describe VPCs and subnet configuration"""
    ec2 = session.client("ec2")
    vpcs = ec2.describe_vpcs()["Vpcs"]
    subnets = ec2.describe_subnets()["Subnets"]
    result = {
        "vpcs": [{"id": v["VpcId"], "cidr": v["CidrBlock"],
                  "default": v["IsDefault"]} for v in vpcs],
        "subnets": [{"id": s["SubnetId"], "cidr": s["CidrBlock"],
                     "az": s["AvailabilityZone"]} for s in subnets]
    }
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()