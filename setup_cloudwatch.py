import boto3
import json

# Change region if needed
ssm_client = boto3.client('ssm', region_name='eu-west-3')
ec2_client = boto3.client('ec2', region_name='eu-west-3')

# Get instance id from file
with open('instance_id.json', 'r') as f:
    data = json.load(f)
    INSTANCE_ID = data['instance_id']


def install_cloudwatch(instance_id):
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        # Replace command with appropriate for yours EC2 system
        Parameters={
            'commands': ["wget https://amazoncloudwatch-agent-eu-west-3.s3.eu-west-3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb",
                         "sudo dpkg -i -E ./amazon-cloudwatch-agent.deb"
            ]
        }
    )

    command_id = response['Command']['CommandId']

    output = try_output(command_id, instance_id)

    print("Command output:", output)


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
        "sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:/AmazonCloudWatchAgent/instance_config -s"
    ]

    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': start_agent_command}
    )

    command_id = response['Command']['CommandId']
    print(f"Sent start command, waiting for completion... Command ID: {command_id}")

    output = try_output(command_id, instance_id)
    print("Command output:", output)


def try_output(command_id, instance_id):
    while True:
        try:
            output = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            if output['Status'] == 'Success':
                return output
            else: continue
        except:
            continue


if __name__ == "__main__":
    install_cloudwatch(INSTANCE_ID)
    configure_cloudwatch(INSTANCE_ID)
    print(f"CloudWatch installation and configuration for instance with ID:{INSTANCE_ID} completed")