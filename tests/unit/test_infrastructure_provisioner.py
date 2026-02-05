#!/usr/bin/env python3
"""
Unit tests for InfrastructureProvisioner module.
"""

from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import boto3
import pytest

from src.infrastructure.provisioner import InfrastructureProvisioner


class TestInfrastructureProvisioner:
    """Test suite for InfrastructureProvisioner class."""

    @pytest.fixture
    def provisioner(self, mock_boto3_ec2, mock_boto3_s3):
        """Create an InfrastructureProvisioner instance with mocked boto3."""
        with patch("boto3.client") as mock_client:

            def client_side_effect(service, **kwargs):
                if service == "ec2":
                    return mock_boto3_ec2
                elif service == "s3":
                    return mock_boto3_s3
                return MagicMock()

            mock_client.side_effect = client_side_effect
            provisioner = InfrastructureProvisioner(region="us-west-2")
            yield provisioner

    def test_initialization(self):
        """Test InfrastructureProvisioner initialization."""
        with patch("boto3.client") as mock_client:
            mock_client.return_value = MagicMock()
            provisioner = InfrastructureProvisioner(region="us-east-1")
            assert provisioner is not None
            assert mock_client.call_count >= 2  # EC2 and S3 clients

    def test_initialization_default_region(self):
        """Test initialization with default region."""
        with patch("boto3.client") as mock_client:
            mock_client.return_value = MagicMock()
            provisioner = InfrastructureProvisioner()
            # Should use default us-west-2
            assert provisioner is not None

    def test_create_ec2_instance_success(self, provisioner, mock_boto3_ec2):
        """Test creating EC2 instance successfully."""
        instance_config = {
            "image_id": "ami-0c55b159cbfafe1f0",
            "instance_type": "t2.micro",
            "name": "TestServer",
            "key_name": "my-key",
            "security_group_ids": ["sg-12345"],
            "subnet_id": "subnet-12345",
        }

        result = provisioner.create_ec2_instance(instance_config)

        assert result is not None
        assert "InstanceId" in result
        mock_boto3_ec2.run_instances.assert_called_once()

    def test_create_ec2_instance_minimal_config(self, provisioner, mock_boto3_ec2):
        """Test creating EC2 instance with minimal configuration."""
        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
        }

        result = provisioner.create_ec2_instance(instance_config)

        assert result is not None
        call_args = mock_boto3_ec2.run_instances.call_args
        assert call_args[1]["ImageId"] == "ami-12345"
        assert call_args[1]["InstanceType"] == "t2.micro"
        assert call_args[1]["MinCount"] == 1
        assert call_args[1]["MaxCount"] == 1

    def test_create_ec2_instance_with_tags(self, provisioner, mock_boto3_ec2):
        """Test creating EC2 instance with custom name tag."""
        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
            "name": "WebServer",
        }

        result = provisioner.create_ec2_instance(instance_config)

        call_args = mock_boto3_ec2.run_instances.call_args
        tag_specs = call_args[1]["TagSpecifications"]
        assert len(tag_specs) == 1
        assert tag_specs[0]["ResourceType"] == "instance"
        assert tag_specs[0]["Tags"][0]["Key"] == "Name"
        assert tag_specs[0]["Tags"][0]["Value"] == "WebServer"

    def test_create_ec2_instance_default_name(self, provisioner, mock_boto3_ec2):
        """Test creating EC2 instance with default name."""
        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
        }

        result = provisioner.create_ec2_instance(instance_config)

        call_args = mock_boto3_ec2.run_instances.call_args
        tag_specs = call_args[1]["TagSpecifications"]
        assert tag_specs[0]["Tags"][0]["Value"] == "DevOps-Instance"

    def test_create_ec2_instance_error(self, provisioner, mock_boto3_ec2):
        """Test handling error during EC2 instance creation."""
        mock_boto3_ec2.run_instances.side_effect = Exception("AWS API Error")

        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
        }

        result = provisioner.create_ec2_instance(instance_config)

        assert result == {}

    def test_list_instances_success(self, provisioner, mock_boto3_ec2):
        """Test listing EC2 instances successfully."""
        provisioner.list_instances()

        mock_boto3_ec2.describe_instances.assert_called_once()

    def test_list_instances_with_filters(self, provisioner, mock_boto3_ec2):
        """Test listing EC2 instances with filters."""
        filters = [{"Name": "instance-state-name", "Values": ["running"]}]

        provisioner.list_instances(filters=filters)

        mock_boto3_ec2.describe_instances.assert_called_once_with(Filters=filters)

    def test_list_instances_display_format(self, provisioner, mock_boto3_ec2):
        """Test that list_instances displays data in table format."""
        # Mock response already set in fixture
        provisioner.list_instances()

        # Should not raise any exceptions
        assert True

    def test_list_instances_no_name_tag(self, provisioner, mock_boto3_ec2):
        """Test listing instances without Name tag."""
        mock_boto3_ec2.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-12345",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "PublicIpAddress": "1.2.3.4",
                            "Tags": [],  # No tags
                        }
                    ]
                }
            ]
        }

        provisioner.list_instances()
        # Should handle missing Name tag gracefully

    def test_list_instances_no_public_ip(self, provisioner, mock_boto3_ec2):
        """Test listing instances without public IP."""
        mock_boto3_ec2.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-12345",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Name", "Value": "Private"}],
                            # No PublicIpAddress
                        }
                    ]
                }
            ]
        }

        provisioner.list_instances()
        # Should handle missing public IP gracefully

    def test_list_instances_error(self, provisioner, mock_boto3_ec2):
        """Test handling error when listing instances."""
        mock_boto3_ec2.describe_instances.side_effect = Exception("AWS Error")

        # Should handle error gracefully
        provisioner.list_instances()

    def test_create_s3_bucket_success(self, provisioner, mock_boto3_s3):
        """Test creating S3 bucket successfully."""
        provisioner.create_s3_bucket("my-test-bucket", region="us-west-2")

        mock_boto3_s3.create_bucket.assert_called_once()
        call_args = mock_boto3_s3.create_bucket.call_args
        assert call_args[1]["Bucket"] == "my-test-bucket"
        assert (
            call_args[1]["CreateBucketConfiguration"]["LocationConstraint"]
            == "us-west-2"
        )

    def test_create_s3_bucket_default_region(self, provisioner, mock_boto3_s3):
        """Test creating S3 bucket with default region."""
        provisioner.create_s3_bucket("my-bucket")

        call_args = mock_boto3_s3.create_bucket.call_args
        assert (
            call_args[1]["CreateBucketConfiguration"]["LocationConstraint"]
            == "us-west-2"
        )

    def test_create_s3_bucket_different_region(self, provisioner, mock_boto3_s3):
        """Test creating S3 bucket in different region."""
        provisioner.create_s3_bucket("my-bucket", region="eu-west-1")

        call_args = mock_boto3_s3.create_bucket.call_args
        assert (
            call_args[1]["CreateBucketConfiguration"]["LocationConstraint"]
            == "eu-west-1"
        )

    def test_create_s3_bucket_error(self, provisioner, mock_boto3_s3):
        """Test handling error during S3 bucket creation."""
        mock_boto3_s3.create_bucket.side_effect = Exception("Bucket already exists")

        # Should handle error gracefully
        provisioner.create_s3_bucket("existing-bucket")

    def test_list_s3_buckets_success(self, provisioner, mock_boto3_s3):
        """Test listing S3 buckets successfully."""
        provisioner.list_s3_buckets()

        mock_boto3_s3.list_buckets.assert_called_once()

    def test_list_s3_buckets_empty(self, provisioner, mock_boto3_s3):
        """Test listing S3 buckets when none exist."""
        mock_boto3_s3.list_buckets.return_value = {"Buckets": []}

        provisioner.list_s3_buckets()
        # Should handle empty list gracefully

    def test_list_s3_buckets_error(self, provisioner, mock_boto3_s3):
        """Test handling error when listing S3 buckets."""
        mock_boto3_s3.list_buckets.side_effect = Exception("AWS Error")

        # Should handle error gracefully
        provisioner.list_s3_buckets()

    def test_provision_from_yaml_success(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, sample_infrastructure_config
    ):
        """Test provisioning infrastructure from YAML file."""
        provisioner.provision_from_yaml(str(sample_infrastructure_config))

        # Should create EC2 instance
        mock_boto3_ec2.run_instances.assert_called()

        # Should create S3 buckets
        assert mock_boto3_s3.create_bucket.call_count >= 1

    def test_provision_from_yaml_ec2_only(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, temp_dir
    ):
        """Test provisioning only EC2 instances from YAML."""
        config_file = temp_dir / "ec2_only.yaml"
        config_content = """ec2_instances:
  - name: WebServer
    image_id: ami-12345
    instance_type: t2.micro
"""
        config_file.write_text(config_content)

        provisioner.provision_from_yaml(str(config_file))

        mock_boto3_ec2.run_instances.assert_called()
        mock_boto3_s3.create_bucket.assert_not_called()

    def test_provision_from_yaml_s3_only(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, temp_dir
    ):
        """Test provisioning only S3 buckets from YAML."""
        config_file = temp_dir / "s3_only.yaml"
        config_content = """s3_buckets:
  - name: my-bucket
    region: us-west-2
"""
        config_file.write_text(config_content)

        provisioner.provision_from_yaml(str(config_file))

        mock_boto3_ec2.run_instances.assert_not_called()
        mock_boto3_s3.create_bucket.assert_called()

    def test_provision_from_yaml_empty_config(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, temp_dir
    ):
        """Test provisioning with empty YAML config."""
        config_file = temp_dir / "empty.yaml"
        config_file.write_text("")

        provisioner.provision_from_yaml(str(config_file))

        # Should handle empty config gracefully
        mock_boto3_ec2.run_instances.assert_not_called()
        mock_boto3_s3.create_bucket.assert_not_called()

    def test_provision_from_yaml_invalid_file(self, provisioner):
        """Test provisioning with invalid YAML file."""
        # Should handle file not found gracefully
        provisioner.provision_from_yaml("/nonexistent/file.yaml")

    def test_provision_from_yaml_malformed(self, provisioner, temp_dir):
        """Test provisioning with malformed YAML."""
        config_file = temp_dir / "malformed.yaml"
        config_file.write_text("this is not: valid: yaml: content:")

        # Should handle malformed YAML gracefully
        provisioner.provision_from_yaml(str(config_file))

    def test_provision_from_yaml_multiple_instances(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, temp_dir
    ):
        """Test provisioning multiple EC2 instances."""
        config_file = temp_dir / "multi_instance.yaml"
        config_content = """ec2_instances:
  - name: WebServer1
    image_id: ami-12345
    instance_type: t2.micro
  - name: WebServer2
    image_id: ami-12345
    instance_type: t2.small
  - name: Database
    image_id: ami-67890
    instance_type: t2.medium
"""
        config_file.write_text(config_content)

        provisioner.provision_from_yaml(str(config_file))

        assert mock_boto3_ec2.run_instances.call_count == 3

    def test_provision_from_yaml_multiple_buckets(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, temp_dir
    ):
        """Test provisioning multiple S3 buckets."""
        config_file = temp_dir / "multi_bucket.yaml"
        config_content = """s3_buckets:
  - name: bucket-1
    region: us-west-2
  - name: bucket-2
    region: us-east-1
  - name: bucket-3
    region: eu-west-1
"""
        config_file.write_text(config_content)

        provisioner.provision_from_yaml(str(config_file))

        assert mock_boto3_s3.create_bucket.call_count == 3

    def test_provision_from_yaml_mixed_resources(
        self, provisioner, mock_boto3_ec2, mock_boto3_s3, sample_infrastructure_config
    ):
        """Test provisioning mixed EC2 and S3 resources."""
        provisioner.provision_from_yaml(str(sample_infrastructure_config))

        # Both EC2 and S3 should be provisioned
        assert mock_boto3_ec2.run_instances.called
        assert mock_boto3_s3.create_bucket.called

    def test_list_instances_multiple_reservations(self, provisioner, mock_boto3_ec2):
        """Test listing instances across multiple reservations."""
        mock_boto3_ec2.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "PublicIpAddress": "1.1.1.1",
                            "Tags": [{"Key": "Name", "Value": "Server1"}],
                        }
                    ]
                },
                {
                    "Instances": [
                        {
                            "InstanceId": "i-2",
                            "InstanceType": "t2.small",
                            "State": {"Name": "stopped"},
                            "Tags": [{"Key": "Name", "Value": "Server2"}],
                        }
                    ]
                },
            ]
        }

        provisioner.list_instances()
        # Should display instances from all reservations

    def test_ec2_instance_config_security_groups(self, provisioner, mock_boto3_ec2):
        """Test EC2 instance creation with security groups."""
        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
            "security_group_ids": ["sg-123", "sg-456"],
        }

        provisioner.create_ec2_instance(instance_config)

        call_args = mock_boto3_ec2.run_instances.call_args
        assert call_args[1]["SecurityGroupIds"] == ["sg-123", "sg-456"]

    def test_ec2_instance_config_subnet(self, provisioner, mock_boto3_ec2):
        """Test EC2 instance creation with subnet."""
        instance_config = {
            "image_id": "ami-12345",
            "instance_type": "t2.micro",
            "subnet_id": "subnet-abc123",
        }

        provisioner.create_ec2_instance(instance_config)

        call_args = mock_boto3_ec2.run_instances.call_args
        assert call_args[1]["SubnetId"] == "subnet-abc123"

    def test_different_region_initialization(self):
        """Test provisioner can be initialized with different regions."""
        regions = ["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"]

        with patch("boto3.client") as mock_client:
            mock_client.return_value = MagicMock()

            for region in regions:
                provisioner = InfrastructureProvisioner(region=region)
                assert provisioner is not None
