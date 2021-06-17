# Managing Autoscaling Group updates with Amazon ECS Capacity Providers

## Why

For those who need or decide to run their containers on self managed EC2 instead of AWS Fargate, they have to consider how to roll out updates to their AMI's.
This process can be cumbersome and a bit of a headache to manage. 
With Capacity Providers and cluster autoscaling, the headache can be lessened drastically.
This walkthrough will showcase how one can seamlessly upgrade their autoscaling groups while maintaining availability and stability with their ECS services.

## Pre-requisites

This demo will use the [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk/) to build our environment as well as our ECS service.

## Walkthrough

To walk through this repo, check out this [post](https://aws.amazon.com/blogs/containers/rolling-ec2-ami-updates-with-capacity-providers-in-amazon-ecs/) on the AWS containers blog.

