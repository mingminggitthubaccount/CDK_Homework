import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
    # aws_sqs as sqs,
)

from constructs import Construct

from aws_cdk import aws_ec2 as ec2, Stack
from constructs import Construct

class HwCdkNetworkStack(Stack):
    @property
    def vpc(self):
        return self._vpc

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._vpc = ec2.Vpc(
            self, "VPC",
            max_azs=2,  # Default is all AZs in region
            subnet_configuration=[
                ec2.SubnetConfiguration(name="PublicSubnet", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24),
                ec2.SubnetConfiguration(name="PrivateSubnet", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT, cidr_mask=24)
            ]
        )
