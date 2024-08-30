import jsii
from constructs import Construct
from aws_cdk import (
    Stack,
    Stage,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    pipelines,
)

from common.conf import EnvConf, EnvType, PipelineConf

from sample.sample_stack import Sample


@jsii.implements(pipelines.ICodePipelineActionFactory)
class CloudFormationDeleteStackStep(pipelines.Step):
    """
    Custom pipeline action that deletes a CloudFormation stack
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
    ):
        super().__init__(id)

        self._discover_referenced_outputs({"env": {}})

        self._action_name = id
        self._stack_name = stack_name

        self._destroy_role = iam.Role.from_role_arn(
            scope,
            f"{id}DestroyRole",
            f"arn:{scope.partition}:iam::{scope.account}:role/cdk-{scope.synthesizer.bootstrap_qualifier}-deploy-role-{scope.account}-{scope.region}",
        )
        self._exec_role = iam.Role.from_role_arn(
            scope,
            f"{id}ExecRole",
            f"arn:{scope.partition}:iam::{scope.account}:role/cdk-{scope.synthesizer.bootstrap_qualifier}-cfn-exec-role-{scope.account}-{scope.region}",
        )

    def produce_action(
        self,
        stage,
        scope: pipelines.ProduceActionOptions,
        action_name=None,
        run_order=None,
        variables_namespace=None,
        artifacts=None,
        fallbackArtifact=None,
        pipeline=None,
        codeBuildDefaults=None,
        beforeSelfMutation=None,
        stackOutputsMap=None,
    ):
        action = codepipeline_actions.CloudFormationDeleteStackAction(
            action_name=scope.action_name,
            run_order=scope.run_order,
            admin_permissions=False,
            stack_name=self._stack_name,
            role=self._destroy_role,
            deployment_role=self._exec_role,
        )

        stage.add_action(action)

        return pipelines.CodePipelineActionFactoryResult(run_orders_consumed=1)

    def bind(self, stage, bucket, role) -> codepipeline.ActionConfig:

        return codepipeline.ActionConfig(
            configuration={
                "ActionMode": "DELETE_ONLY",
                "StackName": self._stack_name,
            }
        )


class DeployStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        env_conf: EnvConf,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        Sample(
            self,
            "Sample",
            stack_name=f"Sample{env_conf.env_name}",
            env_conf=env_conf,
            env={"account": env_conf.account, "region": env_conf.region},
        )


class Pipeline(Stack):
    def __init__(
        self, scope: Construct, id: str, pipeline_conf: PipelineConf, **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self._pipeline_conf = pipeline_conf
        self._pipeline = self._build_cdk_pipeline()

    def _build_cdk_pipeline(self) -> pipelines.CodePipeline:

        self._input_source = pipelines.CodePipelineSource.connection(
            self._pipeline_conf.repo,
            self._pipeline_conf.branch,
            connection_arn=self._pipeline_conf.connection_arn,
            trigger_on_push=True,
        )

        synth_step = pipelines.ShellStep(
            "Synth",
            input=self._input_source,
            env={
                "RESOURCE_PREFIX": "#{variables.resource_prefix}",
                "PIPELINE_EXECUTION_ID": "#{codepipeline.PipelineExecutionId}",
            },
            commands=[
                "echo RESOURCE_PREFIX: $RESOURCE_PREFIX",
                "echo PIPELINE_EXECUTION_ID: $PIPELINE_EXECUTION_ID",
                "python3 -m pip install -r requirements.txt",
                "python3 -m pytest",
                # Carry over the cdk.context.json settings as the file is not checked in
                f"cdk synth -c pipeline_repo={self._pipeline_conf.repo} -c pipeline_branch={self._pipeline_conf.branch} -c pipeline_connection_arn={self._pipeline_conf.connection_arn} -c resource_prefix=$RESOURCE_PREFIX",
            ],
        )

        cdk_pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            pipeline_name=f"CustomPipeline",
            synth=synth_step,
            publish_assets_in_parallel=False,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM_3,
                    compute_type=codebuild.ComputeType.LARGE,
                ),
                partial_build_spec=codebuild.BuildSpec.from_object(
                    {
                        "phases": {
                            "install": {
                                "runtime-versions": {"python": "3.12"},
                                "commands": [
                                    "pip3 install pytest",
                                    "npm install -g aws-cdk",
                                ],
                            }
                        }
                    }
                ),
            ),
            cross_account_keys=True,
        )

        for env_conf in self._pipeline_conf.env_confs:

            cdk_pipeline.add_stage(
                DeployStage(
                    self,
                    f"Deploy{env_conf.env_name}",
                    env_conf,
                ),
                pre=(
                    [pipelines.ManualApprovalStep("PromoteToProd")]
                    if env_conf.env_type == EnvType.PROD
                    else None
                ),
                post=(
                    [
                        CloudFormationDeleteStackStep(
                            self,
                            f"Sample{env_conf.env_name}.Destroy",
                            f"Sample{env_conf.env_name}",
                        )
                    ]
                    if env_conf.env_type != EnvType.PROD
                    else None
                ),
            )

        # Materialize the pipeline to allow us to override pipeline configuration
        cdk_pipeline.build_pipeline()

        cfn_pipeline = cdk_pipeline.pipeline.node.default_child

        # Override the pipeline type to a V2
        cfn_pipeline.pipeline_type = "V2"

        # Add a pipeline variable
        cfn_pipeline.add_property_override(
            "Variables",
            [
                {
                    "Name": "resource_prefix",
                    "Description": "Resource prefix",
                    "DefaultValue": PipelineConf.RESOURCE_PREFIX_DEFAULT,
                },
            ],
        )

        cfn_bucket = cdk_pipeline.pipeline.node.find_child(
            "ArtifactsBucket"
        ).node.default_child

        # Include a lifecycle configuration for the pipeline artifacts bucket
        cfn_bucket.add_property_override(
            "LifecycleConfiguration",
            {
                "Rules": [
                    {
                        "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
                        "ExpirationInDays": 365,
                        "NoncurrentVersionExpiration": {"NoncurrentDays": 365},
                        "Status": "Enabled",
                    }
                ]
            },
        )

        cfn_bucket.add_override(
            "UpdateReplacePolicy",
            "Delete",
        )
        cfn_bucket.add_override(
            "DeletionPolicy",
            "Delete",
        )
        return cdk_pipeline
