import boto3
from botocore.exceptions import ClientError

# ---------------- AWS Session Setup ----------------
session = boto3.session.Session(profile_name="boto3-user", region_name="us-east-1")
rds = session.client('rds')
ec2 = session.client('ec2')

# ---------------- Parameters ----------------
vpc_id = 'vpc-03225bf494db6ecc2'
db_identifier = 'datatier-db'
db_subnet_group_name = 'DatabaseTierSubnetGroup'
db_sg_name = 'DataTierSG'
app_sg_name = 'Application-Tier-SG'

# ---------------- Delete RDS DB Instance ----------------
try:
    print(f"🔄 Deleting RDS instance '{db_identifier}'...")
    rds.delete_db_instance(
        DBInstanceIdentifier=db_identifier,
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True
    )
    print(f"✅ RDS instance '{db_identifier}' deletion initiated.")
except ClientError as e:
    if "DBInstanceNotFound" in e.response['Error']['Code']:
        print(f"ℹ️ RDS instance '{db_identifier}' already deleted.")
    else:
        print("❌ Failed to delete RDS instance:", e.response['Error']['Message'])

# ---------------- Wait for RDS deletion to complete ----------------
print("⏳ Waiting for RDS instance to be fully deleted...")
waiter = rds.get_waiter('db_instance_deleted')
try:
    waiter.wait(DBInstanceIdentifier=db_identifier)
    print(f"✅ RDS instance '{db_identifier}' has been deleted.")
except ClientError as e:
    print("❌ Error while waiting for RDS deletion:", e.response['Error']['Message'])

# ---------------- Delete DB Subnet Group ----------------
try:
    rds.delete_db_subnet_group(DBSubnetGroupName=db_subnet_group_name)
    print(f"✅ Deleted DB subnet group: {db_subnet_group_name}")
except ClientError as e:
    if "DBSubnetGroupNotFoundFault" in e.response['Error']['Code']:
        print(f"ℹ️ Subnet group '{db_subnet_group_name}' already deleted.")
    else:
        print("❌ Failed to delete DB subnet group:", e.response['Error']['Message'])

# ---------------- Delete Security Groups ----------------
def delete_sg(sg_name):
    try:
        # Find SG ID by name
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [sg_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        sg_id = response['SecurityGroups'][0]['GroupId']

        # Delete SG
        ec2.delete_security_group(GroupId=sg_id)
        print(f"✅ Deleted security group '{sg_name}' (ID: {sg_id})")
    except ClientError as e:
        if "InvalidGroup.NotFound" in e.response['Error']['Code']:
            print(f"ℹ️ Security group '{sg_name}' already deleted.")
        elif "DependencyViolation" in e.response['Error']['Code']:
            print(f"⚠️ Security group '{sg_name}' is still attached to some resource.")
        else:
            print(f"❌ Failed to delete security group '{sg_name}':", e.response['Error']['Message'])

delete_sg(db_sg_name)
delete_sg(app_sg_name)
