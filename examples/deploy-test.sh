#!/bin/bash

# Deploy with immediate start for testing
# Usage: ./deploy-test.sh [stack-name] [workgroup-name]

STACK_NAME=${1:-"athena-business-hours-test"}
WORKGROUP_NAME=${2:-"primary"}

echo "🧪 Deploying Athena Business Hours Automation for TESTING..."
echo "Stack Name: $STACK_NAME"
echo "Workgroup: $WORKGROUP_NAME"
echo "⚡ Capacity will start IMMEDIATELY for testing"

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue="$WORKGROUP_NAME" \
    ParameterKey=StartImmediately,ParameterValue=true \
    ParameterKey=InitialCapacity,ParameterValue=24 \
    ParameterKey=MaxCapacity,ParameterValue=48 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags \
    Key=Project,Value=AthenaBusinessHours \
    Key=Environment,Value=Test

if [ $? -eq 0 ]; then
  echo "✅ Test stack creation initiated!"
  echo "🔍 Check Step Functions console for immediate execution"
  echo "📊 Monitor: https://console.aws.amazon.com/states/home"
  echo "⚠️  Remember to delete test stack when done to avoid costs"
else
  echo "❌ Test stack creation failed!"
  exit 1
fi
