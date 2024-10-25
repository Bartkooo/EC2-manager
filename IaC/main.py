import boto3


def launch_instance():
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


if __name__ == '__main__':
    launch_instance()
    print('Done!')
