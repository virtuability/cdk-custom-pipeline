from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
)
from constructs import Construct

from common.conf import EnvConf


class Sample(Stack):

    def __init__(
        self, scope: Construct, construct_id: str, env_conf: EnvConf, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._env_conf = env_conf
        self._build_bucket()

    def _build_bucket(self) -> s3.Bucket:

        bucket_name = f"{self._env_conf.resource_prefix}-sample-{self._env_conf.env_name.lower()}-{self.account}-{self.region}"

        return s3.Bucket(
            self,
            "Bucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
        )
