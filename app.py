#!/usr/bin/env python3
import os
from aws_cdk import App

from common.conf import EnvConf, EnvType, PipelineConf
from pipeline.pipeline_stack import Pipeline


class Main:

    def _get_context(self, key: str) -> any:
        return self._app.node.get_context(key)

    def _get_optional_context(self, key: str, default: any) -> any:
        value = self._app.node.try_get_context(key)

        return value if value else default

    def _get_optional_env_var(self, key: str, default: str) -> str:
        value = os.environ.get(key)
        return value if value else default

    def __init__(self):
        self._app = App()

        connection_arn = self._get_context("pipeline_connection_arn")
        repo = self._get_context("pipeline_repo")
        branch = self._get_context("pipeline_branch")
        resource_prefix = self._get_optional_context(
            "resource_prefix", PipelineConf.RESOURCE_PREFIX_DEFAULT
        )

        pipeline_conf = PipelineConf(
            "SamplePipeline",
            [
                EnvConf(
                    EnvType.DEV,
                    "Dev",
                    self._app.account,
                    self._app.region,
                    resource_prefix,
                ),
            ],
            repo,
            branch,
            connection_arn,
        )

        Pipeline(
            self._app,
            "Pipeline",
            pipeline_conf,
            env={"account": self._app.account, "region": self._app.region},
        )
        self._app.synth()


if __name__ == "__main__":
    Main()
