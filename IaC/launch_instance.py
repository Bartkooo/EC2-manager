import boto3

ec2 = boto3.resource('ec2')

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
    KeyName='pycharm',
)

instance_id = instance[0].id
print(f'EC2 Instance Launched: {instance_id}')

