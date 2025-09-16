import boto3 
from  pprint import pprint
session = boto3.session.Session(profile_name='boto3-user')
ec2 = session.client(service_name='ec2', region_name='us-east-1')

#delete all the vpc and subnets and all the regions


# Replace with your VPC ID
vpc_id = "vpc-0004213b5210e77fc"

def delete_vpc(vpc_id):
    # 1. Detach and delete Internet Gateways
    igws = ec2.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
    )["InternetGateways"]

    for igw in igws:
        igw_id = igw["InternetGatewayId"]
        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"✅ Deleted Internet Gateway {igw_id}")

    # 2. Delete Route Tables (except main)
    rtbs = ec2.describe_route_tables(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )["RouteTables"]

    for rtb in rtbs:
        main = False
        for assoc in rtb.get("Associations", []):
            if assoc.get("Main"):
                main = True
        if not main:
            rtb_id = rtb["RouteTableId"]
            # Delete associations
            for assoc in rtb.get("Associations", []):
                if "RouteTableAssociationId" in assoc:
                    ec2.disassociate_route_table(
                        AssociationId=assoc["RouteTableAssociationId"]
                    )
            ec2.delete_route_table(RouteTableId=rtb_id)
            print(f"✅ Deleted Route Table {rtb_id}")

    # 3. Delete Subnets
    subnets = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )["Subnets"]

    for subnet in subnets:
        subnet_id = subnet["SubnetId"]
        ec2.delete_subnet(SubnetId=subnet_id)
        print(f"✅ Deleted Subnet {subnet_id}")

    # 4. Delete Security Groups (except default)
    sgs = ec2.describe_security_groups(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )["SecurityGroups"]

    for sg in sgs:
        if sg["GroupName"] != "default":
            sg_id = sg["GroupId"]
            ec2.delete_security_group(GroupId=sg_id)
            print(f"✅ Deleted Security Group {sg_id}")

    # 5. Finally, delete the VPC
    ec2.delete_vpc(VpcId=vpc_id)
    print(f"✅ Deleted VPC {vpc_id}")

if __name__ == "__main__":
    delete_vpc(vpc_id)

