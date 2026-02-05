# Deployment Examples

This directory contains example deployment scripts and configurations for different use cases.

## Quick Deploy

Deploy with default settings (8 AM - 5 PM weekdays):

```bash
./deploy-default.sh
```

## Custom Schedule Deploy

Deploy with custom business hours:

```bash
./deploy-custom-schedule.sh
```

## Test Deploy

Deploy with immediate start for testing:

```bash
./deploy-test.sh
```

## Production Deploy

Deploy with production-ready settings and custom auto-scaling:

```bash
./deploy-production.sh
```

## Auto-scaling Examples

### Aggressive Scaling (for high-traffic workloads)
```bash
aws cloudformation create-stack \
  --stack-name athena-aggressive-scaling \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=HighUtilizationThreshold,ParameterValue=60 \
    ParameterKey=LowUtilizationThreshold,ParameterValue=40 \
    ParameterKey=ScaleOutDpuAmount,ParameterValue=32 \
    ParameterKey=ScaleInDpuAmount,ParameterValue=16 \
    ParameterKey=EvaluationFrequency,ParameterValue="rate(2 minutes)" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### Conservative Scaling (for cost optimization)
```bash
aws cloudformation create-stack \
  --stack-name athena-conservative-scaling \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters \
    ParameterKey=HighUtilizationThreshold,ParameterValue=85 \
    ParameterKey=LowUtilizationThreshold,ParameterValue=15 \
    ParameterKey=ScaleOutDpuAmount,ParameterValue=8 \
    ParameterKey=ScaleInDpuAmount,ParameterValue=4 \
    ParameterKey=EvaluationFrequency,ParameterValue="rate(10 minutes)" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```
