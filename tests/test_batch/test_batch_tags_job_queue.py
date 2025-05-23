from uuid import uuid4

import pytest

from moto import mock_aws

from . import _get_clients, _setup


@mock_aws
@pytest.mark.parametrize("use_compute_env_arn", [True, False])
def test_create_job_queue_with_tags(use_compute_env_arn):
    ec2_client, iam_client, _, _, batch_client = _get_clients()
    _, _, _, iam_arn = _setup(ec2_client, iam_client)

    compute_name = str(uuid4())
    resp = batch_client.create_compute_environment(
        computeEnvironmentName=compute_name,
        type="UNMANAGED",
        state="ENABLED",
        serviceRole=iam_arn,
    )
    compute_env_identifier = (
        resp["computeEnvironmentArn"] if use_compute_env_arn else compute_name
    )

    jq_name = str(uuid4())[0:6]
    resp = batch_client.create_job_queue(
        jobQueueName=jq_name,
        state="ENABLED",
        priority=123,
        computeEnvironmentOrder=[
            {"order": 123, "computeEnvironment": compute_env_identifier}
        ],
        tags={"k1": "v1", "k2": "v2"},
    )
    assert "jobQueueArn" in resp
    assert "jobQueueName" in resp
    queue_arn = resp["jobQueueArn"]

    my_queue = batch_client.describe_job_queues(jobQueues=[queue_arn])["jobQueues"][0]
    assert my_queue["tags"] == {"k1": "v1", "k2": "v2"}


@mock_aws
def test_list_tags():
    ec2_client, iam_client, _, _, batch_client = _get_clients()
    _, _, _, iam_arn = _setup(ec2_client, iam_client)

    compute_name = str(uuid4())
    resp = batch_client.create_compute_environment(
        computeEnvironmentName=compute_name,
        type="UNMANAGED",
        state="ENABLED",
        serviceRole=iam_arn,
    )
    arn = resp["computeEnvironmentArn"]

    jq_name = str(uuid4())[0:6]
    resp = batch_client.create_job_queue(
        jobQueueName=jq_name,
        state="ENABLED",
        priority=123,
        computeEnvironmentOrder=[{"order": 123, "computeEnvironment": arn}],
        tags={"k1": "v1", "k2": "v2"},
    )
    assert "jobQueueArn" in resp
    assert "jobQueueName" in resp
    queue_arn = resp["jobQueueArn"]

    my_queue = batch_client.list_tags_for_resource(resourceArn=queue_arn)
    assert my_queue["tags"] == {"k1": "v1", "k2": "v2"}


@mock_aws
def test_tag_job_queue():
    ec2_client, iam_client, _, _, batch_client = _get_clients()
    _, _, _, iam_arn = _setup(ec2_client, iam_client)

    compute_name = str(uuid4())
    resp = batch_client.create_compute_environment(
        computeEnvironmentName=compute_name,
        type="UNMANAGED",
        state="ENABLED",
        serviceRole=iam_arn,
    )
    arn = resp["computeEnvironmentArn"]

    jq_name = str(uuid4())[0:6]
    resp = batch_client.create_job_queue(
        jobQueueName=jq_name,
        state="ENABLED",
        priority=123,
        computeEnvironmentOrder=[{"order": 123, "computeEnvironment": arn}],
    )
    queue_arn = resp["jobQueueArn"]

    batch_client.tag_resource(resourceArn=queue_arn, tags={"k1": "v1", "k2": "v2"})

    my_queue = batch_client.list_tags_for_resource(resourceArn=queue_arn)
    assert my_queue["tags"] == {"k1": "v1", "k2": "v2"}


@mock_aws
def test_untag_job_queue():
    ec2_client, iam_client, _, _, batch_client = _get_clients()
    _, _, _, iam_arn = _setup(ec2_client, iam_client)

    compute_name = str(uuid4())
    resp = batch_client.create_compute_environment(
        computeEnvironmentName=compute_name,
        type="UNMANAGED",
        state="ENABLED",
        serviceRole=iam_arn,
    )
    arn = resp["computeEnvironmentArn"]

    jq_name = str(uuid4())[0:6]
    resp = batch_client.create_job_queue(
        jobQueueName=jq_name,
        state="ENABLED",
        priority=123,
        computeEnvironmentOrder=[{"order": 123, "computeEnvironment": arn}],
        tags={"k1": "v1", "k2": "v2"},
    )
    queue_arn = resp["jobQueueArn"]

    batch_client.tag_resource(resourceArn=queue_arn, tags={"k3": "v3"})
    batch_client.untag_resource(resourceArn=queue_arn, tagKeys=["k2"])

    my_queue = batch_client.list_tags_for_resource(resourceArn=queue_arn)
    assert my_queue["tags"] == {"k1": "v1", "k3": "v3"}
