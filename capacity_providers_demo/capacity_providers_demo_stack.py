from aws_cdk import (
    core as cdk,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling
)


class CPDemo(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC")

        autoscaling_group = autoscaling.AutoScalingGroup(
            self, "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType('t3.medium'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            min_capacity=0,
            max_capacity=100
        )
        
        capacity_provider = ecs.AsgCapacityProvider(
            self, "CapacityProvider",
            auto_scaling_group=autoscaling_group,
        )

        cluster = ecs.Cluster(
            self, "ECSCluster",
            vpc=vpc
        )
        
        cluster.add_asg_capacity_provider(capacity_provider)
        
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
                    capacity_provider=capacity_provider.capacity_provider_name,
                    weight=1
                )
            ]
        )