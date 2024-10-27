import boto3
import time
import json

# change region if needed
ssm_client = boto3.client('ssm', region_name='eu-west-3')
ec2_client = boto3.client('ec2', region_name='eu-west-3')

# get instance id from file
with open('instance_id.json', 'r') as f:
    data = json.load(f)
    instance_id = data['instance_id']


def install_cloudwatch(instance_id):
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        # replace command with appropriate for yours EC2 system
        Parameters={
            'commands': ["wget https://amazoncloudwatch-agent-eu-west-3.s3.eu-west-3.amazonaws.com/ubuntu/amd64"
                         "/latest/amazon-cloudwatch-agent.deb"]
        }
    )

    command_id = response['Command']['CommandId']
    print(f"Sent install command, waiting for completion... Command ID: {command_id}")
    wait_for_command(instance_id, command_id)


def configure_cloudwatch(instance_id):
    cloudwatch_config = {
        "metrics": {
            "metrics_collected": {
                "mem": {
                    "measurement": ["mem_used_percent"],
                    "metrics_collection_interval": 60
                },
                "cpu": {
                    "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
                    "metrics_collection_interval": 60
                }
            }
        }
    }

    # Upload configuration file to the instance
    ssm_client.put_parameter(
        Name="/AmazonCloudWatchAgent/instance_config",
        Description="CloudWatch configuration for memory and CPU",
        Value=json.dumps(cloudwatch_config),
        Type="String",
        Overwrite=True
    )

    start_agent_command = [
        "sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config "
        "-m ec2 -c ssm:/AmazonCloudWatchAgent/instance_config -s"
    ]

    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': start_agent_command}
    )

    command_id = response['Command']['CommandId']
    print(f"Sent start command, waiting for completion... Command ID: {command_id}")
    wait_for_command(instance_id, command_id)


def wait_for_command(instance_id, command_id):
    while True:
        output = ssm_client.get_command_invocation(
            InstanceId=instance_id,
            CommandId=command_id
        )

        if output['Status'] in ['Success', 'Failed']:
            print(f"Command completed with status: {output['Status']}")
            break
        time.sleep(5)


if __name__ == "__main__":
    install_cloudwatch(instance_id)
    configure_cloudwatch(instance_id)
    print(f"CloudWatch installation and configuration for instance with ID:{instance_id} completed")