import boto3
from pprint import pprint

# ---------------- AWS Session ----------------
# Use your AWS CLI profile and set the region explicitly
session = boto3.session.Session(profile_name="boto3-user")
ec2 = session.client(service_name="ec2", region_name="us-east-1")

# ---------------- CONFIG ----------------
VPC_CIDR = "10.0.0.0/16"
VPC_NAME = "project-vpc"
AVAILABILITY_ZONES = ["us-east-1a", "us-east-1b"]

# Public Subnets (1 subnet per AZ)
PUBLIC_SUBNETS = {
    "us-east-1a": "10.0.0.0/20",  # Public subnet for us-east-1a
    "us-east-1b": "10.0.16.0/20",  # Public subnet for us-east-1b
}

# Private Subnets (2 subnets per AZ)
PRIVATE_SUBNETS = {
    "us-east-1a": ["10.0.128.0/20", "10.0.160.0/20"],  # Private subnets for us-east-1a
    "us-east-1b": ["10.0.144.0/20", "10.0.176.0/20"],  # Private subnets for us-east-1b
}

# ---------------- FUNCTIONS ----------------
def create_vpc():
    vpc = ec2.create_vpc(CidrBlock=VPC_CIDR, InstanceTenancy="default")
    vpc_id = vpc["Vpc"]["VpcId"]

    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})

    ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": VPC_NAME}])
    print(f"✅ Created VPC {VPC_NAME} ({vpc_id})")
    return vpc_id


def create_internet_gateway(vpc_id):
    igw = ec2.create_internet_gateway()
    igw_id = igw["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
    ec2.create_tags(Resources=[igw_id], Tags=[{"Key": "Name", "Value": f"{VPC_NAME}-igw"}])
    print(f"✅ Created and attached Internet Gateway {igw_id}")
    return igw_id


def create_route_table(vpc_id, name, igw_id=None):
    rtb = ec2.create_route_table(VpcId=vpc_id)
    rtb_id = rtb["RouteTable"]["RouteTableId"]

    ec2.create_tags(Resources=[rtb_id], Tags=[{"Key": "Name", "Value": name}])

    if igw_id:
        ec2.create_route(RouteTableId=rtb_id, DestinationCidrBlock="0.0.0.0/0", GatewayId=igw_id)
        print(f"✅ Created Public Route Table {name} ({rtb_id})")
    else:
        print(f"✅ Created Private Route Table {name} ({rtb_id})")

    return rtb_id


def create_subnet(vpc_id, cidr, az, name, map_public_ip=False, rtb_id=None):
    subnet = ec2.create_subnet(VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az)
    subnet_id = subnet["Subnet"]["SubnetId"]

    ec2.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": name}])

    if map_public_ip:
        ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": True})

    if rtb_id:
        ec2.associate_route_table(SubnetId=subnet_id, RouteTableId=rtb_id)

    print(f"✅ Created Subnet {name} ({subnet_id}) in {az} with {cidr}")
    return subnet_id


# ---------------- MAIN ----------------
if __name__ == "__main__":
    vpc_id = create_vpc()
    igw_id = create_internet_gateway(vpc_id)

    # Create route tables
    rtb_public = create_route_table(vpc_id, f"{VPC_NAME}-rtb-public", igw_id)
    
    # Create private route tables (unique for each AZ)
    rtb_private = {
        "us-east-1a": create_route_table(vpc_id, f"{VPC_NAME}-rtb-private1-us-east-1a"),
        "us-east-1b": create_route_table(vpc_id, f"{VPC_NAME}-rtb-private2-us-east-1b"),
        "us-east-1a": create_route_table(vpc_id, f"{VPC_NAME}-rtb-private3-us-east-1a"),
        "us-east-1b": create_route_table(vpc_id, f"{VPC_NAME}-rtb-private4-us-east-1b"),
    }

    # Create public subnets (1 per AZ) and associate with the public route table
    for az, cidr in PUBLIC_SUBNETS.items():
        create_subnet(
            vpc_id,
            cidr,  # Public subnet CIDR
            az,
            f"{VPC_NAME}-subnet-public-{az}",
            map_public_ip=True,
            rtb_id=rtb_public,  # Associate with the public route table
        )

    # Create private subnets (2 per AZ) and associate with their respective private route tables
    for az, cidrs in PRIVATE_SUBNETS.items():
        for i, cidr in enumerate(cidrs, start=1):
            create_subnet(
                vpc_id,
                cidr,
                az,
                f"{VPC_NAME}-subnet-private{i}-{az}",
                map_public_ip=False,
                rtb_id=rtb_private[az],
            )
