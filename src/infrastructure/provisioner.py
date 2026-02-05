#!/usr/bin/env python3
from typing import Dict, List, Optional

import boto3
import yaml
from rich.console import Console
from rich.table import Table


class InfrastructureProvisioner:
    def __init__(self, region: str = "us-west-2"):
        self.console = Console()
        self.ec2 = boto3.client("ec2", region_name=region)
        self.s3 = boto3.client("s3")

    def create_ec2_instance(self, instance_config: Dict) -> Dict:
        """Create an EC2 instance with the specified configuration."""
        try:
            response = self.ec2.run_instances(
                ImageId=instance_config["image_id"],
                InstanceType=instance_config["instance_type"],
                MinCount=1,
                MaxCount=1,
                KeyName=instance_config.get("key_name"),
                SecurityGroupIds=instance_config.get("security_group_ids", []),
                SubnetId=instance_config.get("subnet_id"),
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": instance_config.get("name", "DevOps-Instance"),
                            }
                        ],
                    }
                ],
            )
            instance_id = response["Instances"][0]["InstanceId"]
            self.console.print(
                f"[green]Successfully created EC2 instance: {instance_id}[/green]"
            )
            return response["Instances"][0]
        except Exception as e:
            self.console.print(f"[red]Error creating EC2 instance: {str(e)}[/red]")
            return {}

    def list_instances(self, filters: Optional[List[Dict]] = None):
        """List EC2 instances and their details."""
        try:
            if filters:
                response = self.ec2.describe_instances(Filters=filters)
            else:
                response = self.ec2.describe_instances()

            table = Table(title="EC2 Instances")
            table.add_column("Instance ID", style="cyan")
            table.add_column("State", style="magenta")
            table.add_column("Instance Type", style="green")
            table.add_column("Public IP", style="yellow")
            table.add_column("Name", style="blue")

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    name = next(
                        (
                            tag["Value"]
                            for tag in instance.get("Tags", [])
                            if tag["Key"] == "Name"
                        ),
                        "N/A",
                    )
                    table.add_row(
                        instance["InstanceId"],
                        instance["State"]["Name"],
                        instance["InstanceType"],
                        instance.get("PublicIpAddress", "N/A"),
                        name,
                    )

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error listing instances: {str(e)}[/red]")

    def create_s3_bucket(self, bucket_name: str, region: str = "us-west-2"):
        """Create an S3 bucket."""
        try:
            location = {"LocationConstraint": region}
            self.s3.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=location
            )
            self.console.print(
                f"[green]Successfully created S3 bucket: {bucket_name}[/green]"
            )
        except Exception as e:
            self.console.print(f"[red]Error creating S3 bucket: {str(e)}[/red]")

    def list_s3_buckets(self):
        """List all S3 buckets."""
        try:
            response = self.s3.list_buckets()

            table = Table(title="S3 Buckets")
            table.add_column("Bucket Name", style="cyan")
            table.add_column("Creation Date", style="magenta")

            for bucket in response["Buckets"]:
                table.add_row(
                    bucket["Name"], bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S")
                )

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error listing S3 buckets: {str(e)}[/red]")

    def provision_from_yaml(self, yaml_file: str):
        """Provision infrastructure from a YAML configuration file."""
        try:
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)

            # Process EC2 instances
            if "ec2_instances" in config:
                for instance in config["ec2_instances"]:
                    self.create_ec2_instance(instance)

            # Process S3 buckets
            if "s3_buckets" in config:
                for bucket in config["s3_buckets"]:
                    self.create_s3_bucket(
                        bucket["name"], bucket.get("region", "us-west-2")
                    )

            self.console.print("[green]Infrastructure provisioning completed![/green]")
        except Exception as e:
            self.console.print(
                f"[red]Error provisioning infrastructure: {str(e)}[/red]"
            )


if __name__ == "__main__":
    provisioner = InfrastructureProvisioner()

    # Example usage:
    # List current EC2 instances
    print("\nListing EC2 instances:")
    provisioner.list_instances()

    # List S3 buckets
    print("\nListing S3 buckets:")
    provisioner.list_s3_buckets()
