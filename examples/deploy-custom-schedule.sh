#!/bin/bash

# Deploy with custom schedule (9 AM - 6 PM Pacific Time)
# Usage: ./deploy-custom-schedule.sh [stack-name] [workgroup-name]

STACK_NAME=${1:-"athena-business-hours-custom"}
WORKGROUP_NAME=${2:-"primary"}

# 9 AM PST = 5 PM UTC (during standard time)
# 6 PM PST = 2 AM UTC next day
START_TIME="0 17 ? * MON-FRI *"  # 5 PM UTC = 9 AM PST
END_TIME="0 2 ? * TUE-SAT *"     # 2 AM UTC = 6 PM PST previous day

echo "🕘 Deploying with Custom Schedule..."
echo "Stack Name: $STACK_NAME"
echo "Workgroup: $WORKGROUP_NAME"
echo "Schedule: 9 AM - 6 PM Pacific Time (Monday-Friday)"

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue="$WORKGROUP_NAME" \
    ParameterKey=StartTime,ParameterValue="$START_TIME" \
    ParameterKey=EndTime,ParameterValue="$END_TIME" \
    ParameterKey=InitialCapacity,ParameterValue=32 \
    ParameterKey=MaxCapacity,ParameterValue=96 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags \
    Key=Project,Value=AthenaBusinessHours \
    Key=Environment,Value=Production \
    Key=Schedule,Value=CustomPacific

if [ $? -eq 0 ]; then
  echo "✅ Custom schedule stack creation initiated!"
  echo "🌎 Timezone: Pacific Time (PST/PDT)"
  echo "📊 Monitor progress: https://console.aws.amazon.com/cloudformation/home#/stacks"
else
  echo "❌ Custom schedule stack creation failed!"
  exit 1
fi
