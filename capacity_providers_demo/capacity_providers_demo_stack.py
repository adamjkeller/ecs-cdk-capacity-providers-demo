from aws_cdk import (
    core as cdk,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_kms as kms,
    aws_logs as logs,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling
)


class CPDemo(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creating a VPC and ECS Cluster
        vpc = ec2.Vpc(self, "VPC")

        cluster = ecs.Cluster(
            self, "ECSCluster",
            vpc=vpc
        )

        # Original ASG and Capacity Provider
        autoscaling_group_old = autoscaling.AutoScalingGroup(
            self, "ASGOld",
            vpc=vpc,
            instance_type=ec2.InstanceType('t3.medium'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(
                hardware_type=ecs.AmiHardwareType.STANDARD
            ),
            min_capacity=0,
            max_capacity=100
        )
        
        capacity_provider_old = ecs.AsgCapacityProvider(
            self, "CapacityProviderOld",
            auto_scaling_group=autoscaling_group_old,
        )
        
        cluster.add_asg_capacity_provider(capacity_provider_old)
        
        # Replacement ASG with new instance type. 
        #autoscaling_group_new = autoscaling.AutoScalingGroup(
        #    self, "ASGNew",
        #    vpc=vpc,
        #    instance_type=ec2.InstanceType('t3.medium'),
        #    machine_image=ecs.EcsOptimizedImage.amazon_linux2(
        #        hardware_type=ecs.AmiHardwareType.STANDARD
        #        #hardware_type=ecs.AmiHardwareType.ARM
        #    ),
        #    min_capacity=0,
        #    max_capacity=100
        #)
        #
        #capacity_provider_new = ecs.AsgCapacityProvider(
        #    self, "CapacityProviderNew",
        #    auto_scaling_group=autoscaling_group_new,
        #)

        #cluster.add_asg_capacity_provider(capacity_provider_new)
        
        # Building out our ECS task definition and service
        task_definition = ecs.Ec2TaskDefinition(self, "TaskDefinition")
        
        task_definition.add_container(
            "DemoApp",
            image=ecs.ContainerImage.from_registry('amazon/amazon-ecs-sample'),
            cpu=256,
            memory_limit_mib=512
        )
        
        ecs_service = ecs.Ec2Service(
            self, "DemoEC2Service",
            cluster=cluster,
            task_definition=task_definition,
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(
                    capacity_provider=capacity_provider_old.capacity_provider_name,
                    weight=1,
                    #base=0
                ),
                #ecs.CapacityProviderStrategy(
                #    capacity_provider=capacity_provider_new.capacity_provider_name,
                #    weight=1
                #)
            ]
        )
        
        ### ECS EXEC ###
        # Cluster level pre-requisites for logging and auditing
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html#ecs-exec-logging
        kms_key = kms.Key(self, "ExecKmsKey")
        exec_bucket = s3.Bucket(
            self, "ExecS3Bucket", 
            removal_policy=cdk.RemovalPolicy.DESTROY, 
        )
        
        log_group = logs.LogGroup(self, "ExecLogGroup")
        
        # We need to override the CFN template to enable exec functionality
        # More info on how to do this via "escape hatches": https://docs.aws.amazon.com/cdk/latest/guide/cfn_layer.html
        cluster.node.default_child.add_property_override(
            'Configuration.ExecuteCommandConfiguration',
            {
                "KmsKeyId": kms_key.key_id,
                "LogConfiguration": {
                    "CloudWatchLogGroupName": log_group.log_group_name,
                    "S3BucketName": exec_bucket.bucket_name,
                    "S3KeyPrefix": "exec-output"
                },
                "Logging": "OVERRIDE"
            }
        )
        
        # IAM policy required for task role
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html#ecs-exec-enabling-and-using
        ecs_exec_task_policy_statement = iam.PolicyStatement(
            actions=[
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"               
            ],
            resources=['*']
        )
        
        ecs_exec_task_policy = iam.Policy(self, "ExecPolicy", statements=[ecs_exec_task_policy_statement])
                
        ecs_service.node.find_child('Service').add_property_override(
            'EnableExecuteCommand', 'true'
        )
        
        ecs_service.task_definition.task_role.attach_inline_policy(
            policy=ecs_exec_task_policy
        )
        
        log_group.grant_write(ecs_service.task_definition.task_role)
        kms_key.grant_decrypt(ecs_service.task_definition.task_role)
        exec_bucket.grant_put(ecs_service.task_definition.task_role)
        
        cdk.CfnOutput(
            self,"ExecCommand",
            value=f"""aws ecs execute-command --region {cdk.Stack.of(self).region} --cluster {cluster.cluster_name} --task <TASKID> --container web --command "/bin/bash" --interactive"""
        )
        ### END ECS EXEC ###
        