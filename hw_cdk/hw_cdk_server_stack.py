import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
    aws_sqs as sqs
)

from constructs import Construct

dirname = os.path.dirname(__file__)

class HwCdkServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cdk_lab_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the security group for web servers
        web_server_sg = ec2.SecurityGroup(
            self, "WebServerSG",
            vpc=cdk_lab_vpc,
            description="Allow HTTP traffic to web servers",
            allow_all_outbound=True
        )
        web_server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic")

        # Define the security group for RDS
        rds_sg = ec2.SecurityGroup(
            self, "RDSSG",
            vpc=cdk_lab_vpc,
            description="Allow MySQL traffic to RDS",
            allow_all_outbound=True
        )

        # Use the web server security group to define ingress for RDS
        rds_sg.add_ingress_rule(web_server_sg, ec2.Port.tcp(3306), "Allow MySQL traffic from web servers")

        # UserData script for web server configuration
        userdata = ec2.UserData.for_linux()
        userdata.add_commands(
            "yum update -y",
            "amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2",
            "yum install -y httpd mariadb-server",
            "systemctl start httpd",
            "systemctl enable httpd"
        )

        # Launch web servers in each public subnet
        for i, subnet in enumerate(cdk_lab_vpc.public_subnets):
            ec2.Instance(
                self, f"WebServer{i+1}",
                instance_type=ec2.InstanceType("t3.micro"),
                machine_image=ec2.MachineImage.latest_amazon_linux(),
                vpc=cdk_lab_vpc,
                vpc_subnets=ec2.SubnetSelection(subnets=[subnet]),
                security_group=web_server_sg,
                user_data=userdata,
            )

        # RDS MySQL instance
        rds.DatabaseInstance(
            self, "RDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_35
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            vpc=cdk_lab_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            security_groups=[rds_sg],
            multi_az=True,
            allocated_storage=20,
            max_allocated_storage=100,
            delete_automated_backups=True,
            backup_retention=Duration.days(7),
        )
