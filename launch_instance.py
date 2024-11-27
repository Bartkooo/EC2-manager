import boto3
import json


def launch_instance():
    ec2 = boto3.resource('ec2', region_name='eu-west-3')

    instance = ec2.create_instances(
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'ITPproject'
                    },
                ]
            },
        ],
        ImageId='ami-045a8ab02aadf4f88',    # Ubuntu Server 24.04 LTS (HVM) - SSD
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='pycharm'
    )[0]

    instance.wait_until_running()

    instance.load()

    save_instance_id(instance.id)

    print(f"Launched instance ID: {instance.id}")


def save_instance_id(instance_id):
    with open('instance_id.json', 'w') as f:
        json.dump({'instance_id': instance_id}, f)


if __name__ == "__main__":
    launch_instance()

