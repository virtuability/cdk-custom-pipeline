import aws_cdk.assertions as assertions

from sample.sample_stack import Sample


def test_sample_count(sample: Sample):

    template = assertions.Template.from_stack(sample)

    template.resource_count_is("AWS::S3::Bucket", 1)

    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [
                    {
                        "ServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256",
                        }
                    }
                ],
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            },
            "BucketName": "unittest-sample-dev-123456789012-eu-west-1",
        },
    )

    template.has_resource(
        "AWS::S3::Bucket",
        {
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete",
        },
    )
