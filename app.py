#!/usr/bin/env python3
import os
from aws_cdk import core as cdk
from capacity_providers_demo.capacity_providers_demo_stack import CPDemo

app = cdk.App()
CPDemo(app, "CapacityProviderDemo")
app.synth()
