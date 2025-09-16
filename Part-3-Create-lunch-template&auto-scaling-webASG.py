import boto3
import base64
from botocore.exceptions import ClientError

# ---------------- AWS Session ----------------
session = boto3.session.Session(profile_name="boto3-user", region_name="us-east-1")
ec2 = session.client('ec2')
elbv2 = session.client('elbv2')
autoscaling = session.client('autoscaling')

# ---------------- Parameters ----------------
launch_template_name = 'Company-Web-Tier-Server'
ami_id = 'ami-04823729c75214919'
instance_type = 't2.micro'
key_name = 'KeyVMBackup'
security_group_ids = ['sg-00542f430b19aa6d5']        
vpc_id = 'vpc-03225bf494db6ecc2'
subnet_ids = ['subnet-0cca8c905692ebebb', 'subnet-0268d403454d12f89']

base_name = "My Company Web Server Auto Scaling Group"
sanitized_name = base_name.replace(" ", "-")[:28]

target_group_name = f"{sanitized_name}-TG"
lb_name = f"{sanitized_name}-LB"[:32]
asg_name = f"{sanitized_name}"

# ---------------- User Data ----------------
user_data_script = '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
cd /var/www/html
echo "<h1>My Company Website</h1>" > index.html
'''
user_data_encoded = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

# ---------------- Create Launch Template ----------------
try:
    response = ec2.create_launch_template(
        LaunchTemplateName=launch_template_name,
        VersionDescription='Web tier server template',
        LaunchTemplateData={
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'KeyName': key_name,
            'SecurityGroupIds': security_group_ids,
            'UserData': user_data_encoded
        }
    )
    print("✅ Launch template created successfully.")
    print("Launch Template ID:", response['LaunchTemplate']['LaunchTemplateId'])

except ClientError as e:
    if "already exists" in e.response['Error']['Message']:
        print("ℹ️ Launch template already exists, proceeding...")
    else:
        print("❌ Failed to create launch template:")
        print(e.response['Error']['Message'])

# ---------------- Create Target Group ----------------
try:
    tg_response = elbv2.create_target_group(
        Name=target_group_name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        TargetType='instance',
        HealthCheckProtocol='HTTP',
        HealthCheckPort='80',
        HealthCheckPath='/',
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=2,
        UnhealthyThresholdCount=2,
        Matcher={'HttpCode': '200'}
    )
    target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
    print("✅ Target group created:", target_group_arn)
except ClientError as e:
    print("❌ Failed to create target group:")
    print(e.response['Error']['Message'])
    target_group_arn = None

# ---------------- Create Load Balancer ----------------
try:
    lb_response = elbv2.create_load_balancer(
        Name=lb_name,
        Subnets=subnet_ids,
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
    lb_dns = lb_response['LoadBalancers'][0]['DNSName']
    print("✅ Load balancer created:", lb_arn)
except ClientError as e:
    print("❌ Failed to create load balancer:")
    print(e.response['Error']['Message'])
    lb_arn = None

# ---------------- Create Listener ----------------
if lb_arn and target_group_arn:
    try:
        listener_response = elbv2.create_listener(
            LoadBalancerArn=lb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[{
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            }]
        )
        print("✅ Listener created on port 80.")
    except ClientError as e:
        print("❌ Failed to create listener:")
        print(e.response['Error']['Message'])
else:
    print("⚠️ Listener creation skipped due to previous errors.")

# ---------------- Create Auto Scaling Group ----------------
try:
    asg_response = autoscaling.create_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchTemplate={
            'LaunchTemplateName': launch_template_name,
            'Version': '$Latest'
        },
        MinSize=2,
        MaxSize=3,
        DesiredCapacity=2,
        VPCZoneIdentifier=",".join(subnet_ids),
        TargetGroupARNs=[target_group_arn],
        HealthCheckType="ELB",
        HealthCheckGracePeriod=300,
        NewInstancesProtectedFromScaleIn=False,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'WebServer-ASG-Instance',
                'PropagateAtLaunch': True
            }
        ]
    )
    print("✅ Auto Scaling Group created:", asg_name)
except ClientError as e:
    print("❌ Failed to create Auto Scaling Group:")
    print(e.response['Error']['Message'])

# ---------------- Enable CloudWatch Group Metrics ----------------
try:
    autoscaling.enable_metrics_collection(
        AutoScalingGroupName=asg_name,
        Granularity='1Minute',
        Metrics=['GroupMinSize', 'GroupMaxSize', 'GroupDesiredCapacity']
    )
    print("📊 CloudWatch group metrics collection enabled.")
except ClientError as e:
    print("⚠️ Failed to enable CloudWatch metrics:", e.response['Error']['Message'])

# ---------------- Create Scaling Policy ----------------
try:
    policy_response = autoscaling.put_scaling_policy(
        AutoScalingGroupName=asg_name,
        PolicyName="TargetTrackingPolicy",
        PolicyType="TargetTrackingScaling",
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0,
            'DisableScaleIn': False
        },
        EstimatedInstanceWarmup=300
    )
    print("📈 Target tracking scaling policy created.")
except ClientError as e:
    print("⚠️ Failed to create scaling policy:", e.response['Error']['Message'])

# ---------------- Output ALB DNS Name ----------------
if lb_dns:
    print("\n🌐 Access your site using this ALB DNS name:")
    print(f"http://{lb_dns}")
