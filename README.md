# Highly Available 3-Tier Architecture for Web Applications in AWS

## 📝 Project Overview

This project demonstrates the creation and implementation of a **Highly Available 3-Tier Architecture** on **Amazon Web Services (AWS)** for a scalable, fault-tolerant, and resilient web application. The architecture is designed to provide high availability, fault tolerance, and scalability across different AWS services.


### 🏗️ Architecture Components
<img width="720" height="617" alt="image" src="https://github.com/user-attachments/assets/7911ebef-0bd7-4acb-928a-65ebe4b46007" />

The architecture is divided into **three layers**:

1. **Web Tier (Presentation Layer)**:
   - **Amazon EC2 Instances**: Hosts the web application.
   - **Auto Scaling Group**: Ensures automatic scaling of EC2 instances based on incoming traffic.
   - **Application Load Balancer (ALB)**: Distributes the incoming web traffic across multiple EC2 instances.
   - **Security Groups**: Controls the inbound and outbound traffic for EC2 instances.

2. **Application Tier**:
   - **Amazon EC2 Instances**: Hosts the business logic and application code.
   - **Auto Scaling Group**: Ensures automatic scaling based on resource demand.
   - **Security Groups**: Restricts access from the web tier to application instances.

3. **Database Tier**:
   - **Amazon RDS (MySQL)**: Manages the relational database layer to handle dynamic data.
   - **Security Groups**: Ensures that only application-tier instances can access the database.


### 🌐 Networking and Security

- **VPC (Virtual Private Cloud)**: Isolated network environment for all AWS resources.
- **Subnets**: Divided into public and private subnets across multiple availability zones.
- **Route Tables**: Ensures proper routing between subnets and the internet.
- **Internet Gateway**: Allows public subnets to communicate with the internet.
- **NAT Gateway**: Enables instances in private subnets to access the internet for updates or patches.
- **Security Groups and NACLs**: Controls access and traffic flow between different layers.

---

## ⚙️ Architecture Setup
to create this Architecture use the source code is divide by the 5-parts :
1. **Create a Virtual Private Cloud (VPC) and Subnets**:
   - Define the CIDR block :10.0.0.0/16.
   - Enable DNS hostnames for the VPC.
   - Create **public subnets** (10.0.0.0/20, 10.0.16.0/20) in multiple Availability Zones.
   - Create **private subnets** (10.0.128.0/20, 10.0.160.0/20, 10.0.144.0/20, 10.0.176.0/20) for application and database tiers.

2. **Set Up Security Groups and launch EC2 instance with user data**:
   - Define security groups for each tier to manage inbound and outbound traffic.
   - Launch EC2 instances for the web .

3. **Create the lunch template and auto scaling in web ASG**:
   in this section we will: 
   - Create the **lunch template**.
   - Create **Target Group**.
   - Create **Load Balancer**.
   - Create **Listener**.
   - Create **Auto Scaling Group**
   - Enable **CloudWatch Group Metrics**.
   - Create **Scaling Policy**.
   all this Set up the ALB to distribute traffic across the EC2 instances in the web app and Ensure proper listener rules and health checks.

4. **Creating an application Tier**:
   in this section we will: 
   - Create **Security Group**.
   - Create **Launch Template**.
   - Create **Target Group**.
   - Create **Load Balancer**.
   - Create **Listener**.
   - Create **Auto Scaling Group**.
   - Enable **CloudWatch Group Metrics**.
   - Create **Scaling Policy**.
    all this Set up the ALB to distribute traffic across the EC2 instances in the app tier and Ensure proper listener rules and health checks.


5. **Set Up RDS Instance**:
   - Create DB Subnet Group to add the subnets private.
   - Launch an **Amazon RDS (MySQL)** instance for the database tier.
   - Set up **security groups** to only allow access from the application tier.

---

## 🧰 Tools and Services Used

- **Amazon EC2**: Elastic Compute Cloud instances for the web and application tiers.
- **Amazon RDS (MySQL)**: Relational database for dynamic application data.
- **Amazon VPC**: Virtual Private Cloud to isolate resources.
- **Amazon ALB (Application Load Balancer)**: Distributes traffic across multiple EC2 instances.
- **Amazon Auto Scaling**: Automatically adjusts the number of EC2 instances based on traffic.
- **Amazon Route 53**: Managed DNS service for routing traffic to the application.
- **Amazon CloudWatch**: For monitoring and logging resource utilization and health.

---

## 🌍 Features and Achievements

- **High Availability**: The architecture is deployed across multiple Availability Zones to ensure fault tolerance.
- **Scalability**: Auto Scaling allows the application to handle sudden traffic spikes efficiently.
- **Security**: Security groups and NACLs ensure that only authorized traffic can reach each layer.
- **Resilience**: Load balancing and automatic failover mechanisms provide continuous uptime for users.
- **Automation**: Use of AWS services automates resource provisioning, scaling, and monitoring.

---

## 📦 Deployment Steps

Here is a high-level overview of the deployment process:

### 1. **VPC Creation**:
   - Create the VPC with a suitable CIDR block (e.g., `10.0.0.0/16`).
   - Enable DNS support and hostnames for the VPC.

### 2. **Subnets**:
   - Create public subnets in two or more Availability Zones for the web tier.
   - Create private subnets for the application and database tiers.

### 3. **Security Groups**:
   - Configure security groups for web, application, and database tiers, ensuring only allowed traffic is permitted.

### 4. **EC2 Instances and Auto Scaling**:
   - Launch EC2 instances for the web and application tiers.
   - Set up **Auto Scaling Groups** with appropriate scaling policies.

### 5. **Application Load Balancer (ALB)**:
   - Set up an ALB to balance incoming traffic to web-tier EC2 instances.

### 6. **RDS Database Instance**:
   - Launch a MySQL RDS instance.
   - Ensure it is deployed in a private subnet and only accessible from the application tier.

### 7. **Testing**:
   - Test the application to ensure it is accessible and functions correctly through the ALB.
   - Test auto-scaling to see if it adjusts based on load.

---

## 📚 References

- [Creating a Highly Available 3-Tier Architecture for Web Applications in AWS](https://medium.com/@abach06/creating-a-highly-available-3-tier-architecture-for-web-applications-in-aws-23f37d49bd25)
- [AWS Documentation: VPC](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [AWS Documentation: EC2](https://docs.aws.amazon.com/ec2/)
- [AWS Documentation: RDS](https://docs.aws.amazon.com/rds/)
- [AWS Documentation: Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

---

## 🚀 Future Improvements

- **Continuous Integration/Continuous Deployment (CI/CD)**: Implement an automated pipeline using AWS CodePipeline for seamless deployments.
- **Multi-Region Setup**: Extend the architecture to multiple AWS regions for even higher availability.
- **Monitoring and Logging**: Enhance monitoring and logging with AWS CloudWatch and AWS X-Ray.

---

## 🏷️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
