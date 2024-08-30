import pytest
from aws_cdk import (
    App,
)

from common.conf import EnvConf, EnvType, PipelineConf
from pipeline.pipeline_stack import Pipeline
from sample.sample_stack import Sample


@pytest.fixture(scope="function")
def cdk_app() -> App:
    app = App()
    return app


@pytest.fixture(scope="function")
def env_conf() -> EnvConf:
    return EnvConf(
        env_type=EnvType.DEV,
        env_name="Dev",
        account="123456789012",
        region="eu-west-1",
        resource_prefix="unittest",
    )


@pytest.fixture(scope="function")
def pipeline_conf(env_conf: EnvConf) -> PipelineConf:
    return PipelineConf(
        "SamplePipeline",
        [
            env_conf,
        ],
        "test/cdk-custom-pipeline",
        "test",
        "arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-1234-1234-1234-123456789012",
    )


@pytest.fixture(scope="function")
def pipeline(cdk_app, pipeline_conf) -> Pipeline:

    pipeline_stack = Pipeline(
        cdk_app,
        "Pipeline",
        pipeline_conf,
        env={"account": "123456789012", "region": "eu-west-1"},
    )
    return pipeline_stack


@pytest.fixture(scope="function")
def sample(cdk_app, env_conf) -> Sample:

    return Sample(
        cdk_app,
        "Sample",
        env_conf,
        env={"account": "123456789012", "region": "eu-west-1"},
    )
