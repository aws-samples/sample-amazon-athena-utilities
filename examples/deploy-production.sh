#!/bin/bash

# Deploy with production-ready settings and optimized auto-scaling
# Usage: ./deploy-production.sh [stack-name] [workgroup-name]

STACK_NAME=${1:-"athena-business-hours-prod"}
WORKGROUP_NAME=${2:-"primary"}

echo "🏭 Deploying Production Athena Business Hours Automation..."
echo "Stack Name: $STACK_NAME"
echo "Workgroup: $WORKGROUP_NAME"
echo "Schedule: 8 AM - 5 PM (Monday-Friday)"
echo "Auto-scaling: Optimized for production workloads"

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue="$WORKGROUP_NAME" \
    ParameterKey=InitialCapacity,ParameterValue=32 \
    ParameterKey=MaxCapacity,ParameterValue=128 \
    ParameterKey=MinTargetDpus,ParameterValue="32" \
    ParameterKey=HighUtilizationThreshold,ParameterValue=70 \
    ParameterKey=LowUtilizationThreshold,ParameterValue=30 \
    ParameterKey=ScaleOutDpuAmount,ParameterValue=24 \
    ParameterKey=ScaleInDpuAmount,ParameterValue=12 \
    ParameterKey=EvaluationFrequency,ParameterValue="rate(3 minutes)" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags \
    Key=Project,Value=AthenaBusinessHours \
    Key=Environment,Value=Production \
    Key=CostCenter,Value=DataAnalytics

if [ $? -eq 0 ]; then
  echo "✅ Production stack creation initiated successfully!"
  echo "📊 Configuration:"
  echo "   • Initial Capacity: 32 DPUs"
  echo "   • Max Capacity: 128 DPUs"
  echo "   • Scale Up: +24 DPUs when >70% utilization"
  echo "   • Scale Down: -12 DPUs when <30% utilization"
  echo "   • Evaluation: Every 3 minutes"
  echo "📈 Monitor: https://console.aws.amazon.com/cloudformation/home#/stacks"
else
  echo "❌ Production stack creation failed!"
  exit 1
fi
