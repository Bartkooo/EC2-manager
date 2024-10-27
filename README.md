# EC2-manager


## First Steps

Activate virtual environment:

```source venv/bin/activate```

Install requirements:

```pip install -r requirements.txt```


## Configuration

Configure EC2 instance setup - `launch_instance.py`:
- name
- AMI
- instance type
- key name

```python
instance = ec2.create_instances(
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'your_instance_name'
                    },
                ]
            },
        ],
        # e.g. 'ami-045a8ab02aadf4f88' - Ubuntu Server 24.04 LTS (HVM)
        ImageId='ami-****************',    
        MinCount=1,
        MaxCount=1,
        # e.g. 't2.micro'
        InstanceType='xx.xxxx',
        KeyName='xxxxxx'
    )[0]
```

## App Usage

### Launch instance

Run: ```python3 launch_instance.py```

Note: file ```instance_id.json``` should be created

### Add IAM Role for the EC2 Instance (CloudWatch)

In order to request CloudWatch metrics (CPU usage etc.) you need to create IAM Role with listed services and attach it to your EC2 instance

- ```AmazonSSMManagedInstanceCore``` 
- ```CloudWatchAgentServerPolicy```

### CloudWatch setup

After adding IAM Role, when instance is running:

Run: ```setup_cloudwatch.py```

###  Boot app

Run: ```python3 ec2_manager_gui.py```

