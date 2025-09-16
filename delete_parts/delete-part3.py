import boto3
from botocore.exceptions import ClientError
import time

# ---------------- AWS Session ----------------
session = boto3.Session(profile_name="boto3-user", region_name="us-east-1")
ec2 = session.client('ec2')
elbv2 = session.client('elbv2')
autoscaling = session.client('autoscaling')

# ---------------- Parameters (Match Your Previous Setup) ----------------
base_name = "My Company Web Server Auto Scaling Group"
sanitized_name = base_name.replace(" ", "-")[:28]

asg_name = f"{sanitized_name}"
launch_template_name = "Company-Web-Tier-Server"
target_group_name = f"{sanitized_name}-TG"
lb_name = f"{sanitized_name}-LB"[:32]

# ---------------- Delete Auto Scaling Group ----------------
try:
    autoscaling.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        MinSize=0,
        MaxSize=0,
        DesiredCapacity=0
    )
    autoscaling.delete_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        ForceDelete=True
    )
    print(f"🗑️ Auto Scaling Group '{asg_name}' deletion initiated.")
except ClientError as e:
    print("⚠️ Error deleting ASG:", e.response['Error']['Message'])

# ---------------- Delete Launch Template ----------------
try:
    ec2.delete_launch_template(LaunchTemplateName=launch_template_name)
    print(f"🗑️ Launch Template '{launch_template_name}' deleted.")
except ClientError as e:
    print("⚠️ Error deleting Launch Template:", e.response['Error']['Message'])

# ---------------- Delete Load Balancer ----------------
try:
    lbs = elbv2.describe_load_balancers(Names=[lb_name])
    lb_arn = lbs['LoadBalancers'][0]['LoadBalancerArn']
    elbv2.delete_load_balancer(LoadBalancerArn=lb_arn)
    print(f"🗑️ Load Balancer '{lb_name}' deletion initiated.")
    time.sleep(20)  # Wait for LB to fully delete before deleting the target group
except ClientError as e:
    print("⚠️ Error deleting Load Balancer:", e.response['Error']['Message'])
    lb_arn = None

# ---------------- Delete Listener ----------------
if lb_arn:
    try:
        listeners = elbv2.describe_listeners(LoadBalancerArn=lb_arn)
        for listener in listeners['Listeners']:
            elbv2.delete_listener(ListenerArn=listener['ListenerArn'])
        print(f"🗑️ All Listeners for LB '{lb_name}' deleted.")
    except ClientError as e:
        print("⚠️ Error deleting listener:", e.response['Error']['Message'])

# ---------------- Delete Target Group ----------------
try:
    tgs = elbv2.describe_target_groups(Names=[target_group_name])
    target_group_arn = tgs['TargetGroups'][0]['TargetGroupArn']
    elbv2.delete_target_group(TargetGroupArn=target_group_arn)
    print(f"🗑️ Target Group '{target_group_name}' deleted.")
except ClientError as e:
    print("⚠️ Error deleting Target Group:", e.response['Error']['Message'])
