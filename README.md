# cdk-custom-pipeline

## Background

An example of how to customise your AWS CDK pipelines.

The example demonstrates several points:

* Upgrades the CDK Pipeline to [CodePipeline V2](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipeline-types.html)
* Introduces simple CodePipeline (V2) parameters
* Introduces a custom CDK pipeline action (delete stack) and deriving the roles with which to delete the stack
* Amends the CodePipeline artifact S3 bucket with lifecycle configuration & Update/Deletion Policy
* Amends the CodeBuild project defaults (such as Python runtime version and installation of `pytest` and `aws-cdk`)
* Takes a configuration as code approach (PipelineConf & EnvConf) to describe pipeline and environment(s)

## Prerequisites

* Python 3.12+
* AWS account
* Configured AWS connection to GitHub
* GitHub repository with a forked version of this repository's contents

## Usage 

To use the sample, fork this repository into a new repository.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

Three context values are required for the CDK app and can be added to a file `cdk.context.json` in the root of this project. Example here:

```json
{
    "pipeline_repo": "github-org/cdk-custom-pipeline",
    "pipeline_branch": "main",
    "pipeline_connection_arn": "arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-1234-1234-1234-123456789012"
}
```

To manually create a virtualenv on MacOS and Linux:

```bash
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
$ pip install -r requirements.txt
```

You can list the stacks of the CDK app.

```bash
$ cdk ls
Pipeline
Pipeline/DeployDev/Sample (SampleDev)
```

At this point you can synthesize the CloudFormation template (Pipeline) for this code.

```bash
$ cdk synth
```

You can deploy the pipeline using the following command.

```bash
$ cdk deploy
```

## Configuration

Deploy-time configuration lives in the `common/conf.py` configuration file and consists of two classes `PipelineConf` and `EnvConf` with an additional `EnvType` enum that defines the type of environment used (whether Dev or Prod).
