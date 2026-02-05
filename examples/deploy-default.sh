#!/bin/bash

# Deploy Athena Business Hours Automation with default settings
# Usage: ./deploy-default.sh [stack-name] [workgroup-name]

STACK_NAME=${1:-"athena-business-hours"}
WORKGROUP_NAME=${2:-"primary"}

echo "🚀 Deploying Athena Business Hours Automation..."
echo "Stack Name: $STACK_NAME"
echo "Workgroup: $WORKGROUP_NAME"
echo "Schedule: 8 AM - 5 PM (Monday-Friday)"

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue="$WORKGROUP_NAME" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags \
    Key=Project,Value=AthenaBusinessHours \
    Key=Environment,Value=Production

if [ $? -eq 0 ]; then
  echo "✅ Stack creation initiated successfully!"
  echo "📊 Monitor progress: https://console.aws.amazon.com/cloudformation/home#/stacks"
  echo "⏱️  This may take 5-10 minutes to complete."
else
  echo "❌ Stack creation failed!"
  exit 1
fi
