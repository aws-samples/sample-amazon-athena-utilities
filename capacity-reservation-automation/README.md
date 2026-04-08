# Amazon Athena Capacity Reservation Automation

Automate Amazon Athena capacity reservations for business hours with integrated auto-scaling using AWS Step Functions, EventBridge, and CloudFormation.

## Features

- **Business Hours Scheduling**: Automatically start/stop Athena capacity reservations during configurable business hours
- **Timezone-Aware**: Native timezone support — configure in your local time, no UTC conversion needed
- **Auto-scaling Integration**: Dynamic capacity management based on utilization thresholds
- **Complete Lifecycle Management**: Creates → Attaches → Auto-scales → Cleans up (including stack deletion)
- **Cost Optimization**: Only runs capacity during business hours, scales based on utilization
- **Security**: VPC-isolated Lambda functions, KMS-encrypted SNS and SQS, dead letter queues

## Important

This sample is intended as an educational example to help you implement Athena capacity reservation automation. Any applications you integrate this example into should be thoroughly tested, secured, and optimized according to your organization's security standards and policies before deploying to production or handling production workloads.

## Prerequisites

- AWS CLI configured with appropriate permissions
- CloudFormation deployment permissions (including IAM, VPC, Lambda, Step Functions)
- Existing Athena workgroup (default: `primary`)

## Architecture

```
EventBridge Rule (EvaluationFrequency)
        │
        ▼
Step Functions State Machine
        │
        ├── Lambda: Check Business Hours (timezone-aware)
        ├── SDK Integration: Create/Check Capacity Reservation
        ├── SDK Integration: Auto-scale (CloudWatch metrics → update capacity)
        └── Lambda: Stop Capacity (cancel + delete outside hours)
        │
        ├── VPC (public + private subnets, NAT Gateway)
        ├── SNS Topic (KMS-encrypted notifications)
        └── SQS Dead Letter Queue (KMS-encrypted)
```

### Components

1. **Step Functions State Machine**: Orchestrates the entire lifecycle — business hours check, capacity creation/assignment via SDK integrations, CloudWatch-based auto-scaling, and cleanup
2. **EventBridge Rule**: Triggers the state machine on a configurable schedule (default: every 5 minutes)
3. **Lambda Functions**: VPC-isolated functions for business hours checking (`BusinessHoursCheck`), capacity cleanup (`StopCapacity`), and stack deletion cleanup (`CapacityCleanup` custom resource)
4. **VPC Infrastructure**: Private subnet with NAT Gateway for secure Lambda execution
5. **SNS Notifications**: KMS-encrypted status updates and alerts
6. **Custom Resource**: Automatic capacity cleanup on stack deletion

## Quick Start

### 1. Deploy with Defaults

```bash
aws cloudformation create-stack \
  --stack-name athena-business-hours \
  --template-body file://athena-capacity-reservation-automation.yaml \
  --parameters ParameterKey=WorkgroupName,ParameterValue=primary \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### 2. Deploy with Custom Schedule and Capacity

```bash
aws cloudformation create-stack \
  --stack-name athena-business-hours \
  --template-body file://athena-capacity-reservation-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue=primary \
    ParameterKey=InitialCapacity,ParameterValue=16 \
    ParameterKey=MaxCapacity,ParameterValue=64 \
    ParameterKey=CapacityReservationStartTime,ParameterValue=09:00 \
    ParameterKey=CapacityReservationEndTime,ParameterValue=18:00 \
    ParameterKey=TimeZone,ParameterValue=America/Los_Angeles \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### 3. Monitor Deployment

```bash
aws cloudformation describe-stacks --stack-name athena-business-hours
```

## Parameters

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `WorkgroupName` | `primary` | Existing Athena workgroup to attach capacity |
| `CapacityReservationName` | *(auto-generated)* | Name for the capacity reservation (leave empty to auto-generate as `{stack}-{workgroup}-capacity`) |
| `InitialCapacity` | `8` | Initial DPU capacity (minimum 4) |
| `MaxCapacity` | `32` | Maximum DPU capacity for auto-scaling (minimum 4) |

### Schedule Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CapacityReservationStartTime` | `08:00` | Start time in HH:MM format (24-hour) |
| `CapacityReservationEndTime` | `17:00` | End time in HH:MM format (24-hour) |
| `BusinessDays` | `MON-FRI` | Business days. Allowed: `MON-FRI`, `MON-SAT`, `MON-SUN`, `SAT-SUN` |
| `TimeZone` | `America/New_York` | Timezone for schedule (e.g., `UTC`, `America/Los_Angeles`, `Europe/London`, `Asia/Tokyo`) |

### Auto-scaling Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MinTargetDpus` | `4` | Minimum DPUs for auto-scaling (must be ≥ 4) |
| `ScaleOutDpuAmount` | `8` | DPUs to add when scaling up (must be ≥ 4) |
| `ScaleInDpuAmount` | `4` | DPUs to remove when scaling down (must be ≥ 4) |
| `HighUtilizationThreshold` | `75` | Scale up when utilization exceeds this % (0-100) |
| `LowUtilizationThreshold` | `25` | Scale down when utilization drops below this % (0-100) |
| `EvaluationLookbackWindow` | `300` | Evaluation window in seconds |
| `EvaluationFrequency` | `rate(5 minutes)` | How often to evaluate (EventBridge schedule expression) |

## Schedule Configuration

The template uses human-readable HH:MM time format with timezone support — no need to manually convert to UTC cron expressions.

### Examples

```bash
# 9 AM - 6 PM Pacific Time, weekdays only
ParameterKey=CapacityReservationStartTime,ParameterValue=09:00
ParameterKey=CapacityReservationEndTime,ParameterValue=18:00
ParameterKey=TimeZone,ParameterValue=America/Los_Angeles
ParameterKey=BusinessDays,ParameterValue=MON-FRI

# 7 AM - 11 PM Tokyo Time, including Saturdays
ParameterKey=CapacityReservationStartTime,ParameterValue=07:00
ParameterKey=CapacityReservationEndTime,ParameterValue=23:00
ParameterKey=TimeZone,ParameterValue=Asia/Tokyo
ParameterKey=BusinessDays,ParameterValue=MON-SAT
```

### Supported Timezones

UTC, Americas (New_York, Chicago, Denver, Los_Angeles, Anchorage, Phoenix, Toronto, Vancouver, Mexico_City, Sao_Paulo, Buenos_Aires), Europe (London, Paris, Berlin, Rome, Madrid, Amsterdam, Brussels, Vienna, Stockholm, Dublin, Zurich, Warsaw, Prague, Budapest, Athens, Istanbul, Moscow), Asia (Tokyo, Seoul, Shanghai, Hong_Kong, Singapore, Bangkok, Mumbai, Dubai, Tel_Aviv, Jakarta, Manila, Taipei), Pacific (Sydney, Melbourne, Brisbane, Perth, Auckland, Fiji), Africa (Johannesburg, Cairo, Lagos).

## Auto-scaling Configuration

### Scaling Behavior
- **High Utilization Threshold**: 75% (configurable) — adds DPUs when exceeded
- **Low Utilization Threshold**: 25% (configurable) — removes DPUs when below
- **Scale Out Amount**: 8 DPUs (configurable)
- **Scale In Amount**: 4 DPUs (configurable)
- **Evaluation Window**: 5 minutes (configurable)
- **Evaluation Frequency**: Every 5 minutes (configurable)

### Custom Auto-scaling Example

```bash
aws cloudformation create-stack \
  --stack-name athena-business-hours \
  --template-body file://athena-capacity-reservation-automation.yaml \
  --parameters \
    ParameterKey=WorkgroupName,ParameterValue=primary \
    ParameterKey=InitialCapacity,ParameterValue=16 \
    ParameterKey=MaxCapacity,ParameterValue=64 \
    ParameterKey=HighUtilizationThreshold,ParameterValue=80 \
    ParameterKey=LowUtilizationThreshold,ParameterValue=20 \
    ParameterKey=ScaleOutDpuAmount,ParameterValue=12 \
    ParameterKey=ScaleInDpuAmount,ParameterValue=8 \
    ParameterKey=EvaluationFrequency,ParameterValue="rate(3 minutes)" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### Scaling Logic
1. **Evaluate**: State machine runs on `EvaluationFrequency` schedule
2. **Business Hours Check**: Lambda checks if current time is within configured business hours (timezone-aware)
3. **Scale Up**: When utilization > threshold and current capacity < `MaxCapacity`
4. **Scale Down**: When utilization < threshold and current capacity > `MinTargetDpus`
5. **Outside Hours**: Capacity reservation is cancelled and cleaned up

## Cost Considerations

### Capacity Reservation Costs
- **Minimum**: 8 DPUs × business hours × DPU rate (with defaults)
- **Maximum**: 32 DPUs × business hours × DPU rate (with defaults)
- **Auto-scaling**: Adjusts capacity based on actual utilization

### Example Cost Calculation (US East 1, default settings)
```
Base Cost: 8 DPUs × 9 hours × 5 days × $0.30/DPU-hour = $108/week
Max Cost:  32 DPUs × 9 hours × 5 days × $0.30/DPU-hour = $432/week
```

> **Note**: Pricing varies by region. See the [Amazon Athena pricing page](https://aws.amazon.com/athena/pricing/) for current rates.

### Additional Infrastructure Costs
- NAT Gateway: ~$0.045/hour + data processing charges
- Step Functions: State transitions (minimal)
- Lambda: Invocations (minimal)
- SNS/SQS: Messages (minimal)

## Monitoring

### CloudWatch Metrics
- `AWS/Athena/DPUAllocated`: Current capacity allocation
- `AWS/Athena/DPUConsumed`: Actual utilization
- `AWS/StepFunctions/ExecutionsFailed`: Failed executions

### Stack Outputs

After deployment, the stack provides these outputs:
- `StateMachineArn`: The Step Functions state machine ARN
- `CapacityReservationName`: The name of the capacity reservation
- `NotificationTopicArn`: SNS topic for notifications
- `BusinessHoursSchedule`: Human-readable schedule summary
- `EvaluationFrequency`: Auto-scaling evaluation frequency

## Security

### What the Template Creates

- **VPC**: Isolated network with public/private subnets and NAT Gateway
- **Lambda Functions**: Run in private subnet, access AWS APIs via NAT Gateway
- **KMS Key**: Encrypts SNS topic and SQS dead letter queue
- **Security Group**: Restricts Lambda network access
- **IAM Roles**: Least-privilege roles for Step Functions, Lambda, and EventBridge

### Best Practices

- Enable CloudTrail for audit logging
- Monitor capacity usage and costs
- Set up billing alerts
- Review IAM roles created by the stack

## Contributing

See [CONTRIBUTING](../CONTRIBUTING.md) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../LICENSE) file.

## Support

- **Issues**: [GitHub Issues](https://github.com/aws-samples/sample-amazon-athena-utilities/issues)
- **AWS Documentation**: [Athena Capacity Reservations](https://docs.aws.amazon.com/athena/latest/ug/capacity-reservations.html)
