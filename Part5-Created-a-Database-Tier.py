import boto3
from botocore.exceptions import ClientError

# ---------------- AWS Session Setup ----------------
session = boto3.session.Session(profile_name="boto3-user", region_name="us-east-1")
rds = session.client('rds')
ec2 = session.client('ec2')

# ---------------- Parameters ----------------
vpc_id = 'vpc-03225bf494db6ecc2'

# Subnet group (must be in private subnets)
subnet_ids = ['subnet-079fe0a7a068f58fe', 'subnet-045f95cf0c41e11ad']
db_subnet_group_name = 'DatabaseTierSubnetGroup'

# Security group names
db_sg_name = 'DataTierSG'
app_sg_name = 'Application-Tier-SG'  # Application tier security group name

# RDS DB parameters
db_identifier = 'datatier-db'
db_name = 'mydatabase'
db_username = 'admin'
db_password = 'SecurePassword123!'
db_instance_class = 'db.t3.micro'
engine = 'mysql'
engine_version = '8.4.6'  # valid MySQL engine version for RDS
allocated_storage = 20  # GB

# ---------------- Create DB Subnet Group ----------------
try:
    rds.create_db_subnet_group(
        DBSubnetGroupName=db_subnet_group_name,
        DBSubnetGroupDescription='Private subnet group for RDS MySQL',
        SubnetIds=subnet_ids
    )
    print(f"✅ Subnet group created: {db_subnet_group_name}")
except ClientError as e:
    if "DBSubnetGroupAlreadyExists" in e.response['Error']['Code']:
        print(f"ℹ️ Subnet group {db_subnet_group_name} already exists.")
    else:
        print("❌ Failed to create DB Subnet Group:", e.response['Error']['Message'])
        exit(1)

# ---------------- Create DB Security Group ----------------
try:
    sg_response = ec2.create_security_group(
        GroupName=db_sg_name,
        Description='Allows MySQL access to DB tier',
        VpcId=vpc_id
    )
    db_sg_id = sg_response['GroupId']
    print(f"✅ Security group created: {db_sg_name} with ID {db_sg_id}")
except ClientError as e:
    if "InvalidGroup.Duplicate" in e.response['Error']['Code']:
        print(f"ℹ️ Security group '{db_sg_name}' already exists. Fetching ID...")
        sg_existing = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [db_sg_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        db_sg_id = sg_existing['SecurityGroups'][0]['GroupId']
        print(f"✅ Found existing security group {db_sg_name} with ID {db_sg_id}")
    else:
        print("❌ Failed to create or get security group:", e.response['Error']['Message'])
        exit(1)

# ---------------- Create App Security Group ----------------
try:
    sg_response = ec2.create_security_group(
        GroupName=app_sg_name,
        Description='Application tier security group',
        VpcId=vpc_id
    )
    app_sg_id = sg_response['GroupId']
    print(f"✅ Security group created: {app_sg_name} with ID {app_sg_id}")
except ClientError as e:
    if "InvalidGroup.Duplicate" in e.response['Error']['Code']:
        print(f"ℹ️ Security group '{app_sg_name}' already exists. Fetching ID...")
        sg_existing = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [app_sg_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        app_sg_id = sg_existing['SecurityGroups'][0]['GroupId']
        print(f"✅ Found existing security group {app_sg_name} with ID {app_sg_id}")
    else:
        print("❌ Failed to create or get app security group:", e.response['Error']['Message'])
        exit(1)

# ---------------- Add inbound rule: Allow MySQL from App SG to DB SG ----------------
try:
    ec2.authorize_security_group_ingress(
        GroupId=db_sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 3306,
                'ToPort': 3306,
                'UserIdGroupPairs': [{'GroupId': app_sg_id}]
            }
        ]
    )
    print(f"🔐 Inbound rule added: Allow MySQL (3306) from App SG to DB SG")
except ClientError as e:
    if 'InvalidPermission.Duplicate' in e.response['Error']['Code']:
        print("ℹ️ Inbound rule already exists.")
    else:
        print("❌ Failed to add inbound rule:", e.response['Error']['Message'])

# ---------------- Create RDS Instance ----------------
try:
    rds.create_db_instance(
        DBName=db_name,
        DBInstanceIdentifier=db_identifier,
        AllocatedStorage=allocated_storage,
        DBInstanceClass=db_instance_class,
        Engine=engine,
        EngineVersion=engine_version,
        MasterUsername=db_username,
        MasterUserPassword=db_password,
        VpcSecurityGroupIds=[db_sg_id],
        DBSubnetGroupName=db_subnet_group_name,
        PubliclyAccessible=False,
        BackupRetentionPeriod=7,
        MultiAZ=False,
        StorageType='gp2',
        Tags=[
            {'Key': 'Name', 'Value': 'DataTierDB'}
        ]
    )
    print(f"✅ RDS MySQL instance '{db_identifier}' creation started.")
except ClientError as e:
    if "DBInstanceAlreadyExists" in e.response['Error']['Code']:
        print(f"ℹ️ RDS instance '{db_identifier}' already exists.")
    else:
        print("❌ Failed to create RDS instance:", e.response['Error']['Message'])
