# Managing Autoscaling Group updates with Amazon ECS Capacity Providers

## Why

For those who need or decide to run their containers on self managed EC2 instead of AWS Fargate, they have to consider how to roll out updates to their AMI's.
This process can be cumbersome and a bit of a headache to manage. 
With Capacity Providers and cluster autoscaling, the headache can be lessened drastically.
This walkthrough will showcase how one can seamlessly upgrade their autoscaling groups while maintaining availability and stability with their ECS services.

## Pre-requisites

This demo will use the [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk/) to build our environment as well as our ECS service.

## Walkthrough

1) Let's get a Python virtual environment setup and install all of the packages needed to get to deployin'!

```bash
npm i -g aws-cdk
virtualenv .env
source .env/bin/activate
pip3 install -r requirements.txt
```

2) In the code we are creating all of necessary resources to spin up our ECS cluster and service. 
We are creating a single capacity provider and our service will use that as the strategy. So let's get our container deployed!

```bash
cdk deploy --require-approval never
```

