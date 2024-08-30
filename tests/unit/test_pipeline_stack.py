import aws_cdk.assertions as assertions

from pipeline.pipeline_stack import Pipeline


def test_pipeline_count(pipeline: Pipeline):

    template = assertions.Template.from_stack(pipeline)

    template.resource_count_is("AWS::KMS::Key", 1)
    template.resource_count_is("AWS::KMS::Alias", 1)
    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::S3::BucketPolicy", 1)
    template.resource_count_is("AWS::IAM::Role", 5)
    template.resource_count_is("AWS::IAM::Policy", 6)
    template.resource_count_is("AWS::CodePipeline::Pipeline", 1)
    template.resource_count_is("AWS::CodeBuild::Project", 2)


def test_pipeline_bucket(pipeline: Pipeline):

    template = assertions.Template.from_stack(pipeline)

    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [
                    {
                        "ServerSideEncryptionByDefault": {
                            "KMSMasterKeyID": {
                                "Fn::GetAtt": [
                                    "PipelineArtifactsBucketEncryptionKeyF5BF0670",
                                    "Arn",
                                ]
                            },
                            "SSEAlgorithm": "aws:kms",
                        }
                    }
                ],
            },
            "LifecycleConfiguration": {
                "Rules": [
                    {
                        "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
                        "ExpirationInDays": 365,
                        "NoncurrentVersionExpiration": {"NoncurrentDays": 365},
                        "Status": "Enabled",
                    }
                ]
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            },
        },
    )

    template.has_resource(
        "AWS::S3::Bucket",
        {
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete",
        },
    )


def test_pipeline(pipeline: Pipeline):

    template = assertions.Template.from_stack(pipeline)

    template.has_resource_properties(
        "AWS::CodePipeline::Pipeline",
        {
            "Variables": [
                {
                    "Name": "resource_prefix",
                    "Description": "Resource prefix",
                    "DefaultValue": "test",
                }
            ]
        },
    )
