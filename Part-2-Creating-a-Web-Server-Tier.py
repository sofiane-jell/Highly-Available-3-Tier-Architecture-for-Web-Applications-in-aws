import boto3
from pprint import pprint

# ---------------- AWS Session ----------------
# Use your AWS CLI profile and set the region explicitly
session = boto3.session.Session(profile_name="boto3-user")
ec2 = session.client(service_name="ec2", region_name="us-east-1")

# ---------------- CONFIG ----------------
AMI_ID = "ami-04823729c75214919"  # Amazon Linux 2 AMI (for example)
INSTANCE_TYPE = "t2.micro"
KEY_PAIR_NAME = "KeyVMBackup"  # Make sure this key pair exists in your AWS account
SECURITY_GROUP_NAME = "Company-Web-Tier-SG"
SUBNET_ID = "subnet-0cca8c905692ebebb"  # Replace with your existing subnet ID

# ---------------- FUNCTIONS ----------------

# Function to create a security group with required rules
def create_security_group(vpc_id):
    response = ec2.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description="Security group for 3-tier architecture EC2 instance",
        VpcId=vpc_id
    )
    security_group_id = response['GroupId']
    print(f"✅ Created Security Group {SECURITY_GROUP_NAME} with ID: {security_group_id}")
    
    # Add inbound rules
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            # SSH Rule (Port 22)
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Open to all IPs
            },
            # HTTP Rule (Port 80)
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Open to all IPs
            },
            # HTTPS Rule (Port 443)
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Open to all IPs
            }
        ]
    )
    return security_group_id

# Function to launch EC2 instance with user data
def launch_ec2_instance(subnet_id, security_group_id):
    user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>My Company Website</h1>" | sudo tee /var/www/html/index.html
"""

    instance = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_PAIR_NAME,
        SubnetId=subnet_id,
        SecurityGroupIds=[security_group_id],
        MinCount=1,
        MaxCount=1,
        UserData=user_data_script,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': '3-tier-architecture-ec2'}]
        }],
        # Optional: Use default network interface settings, public IP should be enabled in subnet setting
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"✅ Launched EC2 instance with ID: {instance_id}")
    return instance_id



# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Assume VPC ID is available from your existing setup
    vpc_id = "vpc-03225bf494db6ecc2"  # Replace with your VPC ID

    # Step 1: Create security group with inbound rules
    security_group_id = create_security_group(vpc_id)

    # Step 2: Launch EC2 instance in the specified subnet with the created security group
    launch_ec2_instance(SUBNET_ID, security_group_id)
