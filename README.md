# Athena Business Hours Automation

Automate Amazon Athena capacity reservations for business hours with integrated auto-scaling using AWS Step Functions, EventBridge, and CloudFormation.

## 🚀 Features

- **Business Hours Scheduling**: Automatically start/stop Athena capacity reservations during business hours (8 AM - 5 PM weekdays)
- **Auto-scaling Integration**: Deploys official AWS Athena auto-scaling template for dynamic capacity management
- **Immediate Testing**: Optional parameter to start capacity immediately for testing
- **Complete Lifecycle Management**: Creates → Attaches → Auto-scales → Cleans up
- **Cost Optimization**: Only runs capacity during business hours, scales based on utilization

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- CloudFormation deployment permissions
- Existing Athena workgroup (default: `primary`)

## 🏗️ Architecture

```
EventBridge Rules → Step Functions → Lambda Functions → Athena Capacity
                                  ↓
                    CloudFormation → Auto-scaling Template
```

### Components

1. **Step Functions State Machine**: Orchestrates the entire lifecycle
2. **EventBridge Rules**: Trigger start/stop at business hours
3. **Lambda Functions**: Handle Athena API calls for capacity management
4. **Auto-scaling Integration**: Deploys official AWS template for utilization-based scaling
5. **SNS Notifications**: Status updates and alerts

## 🚀 Quick Start

### 1. Deploy the Template

```bash
aws cloudformation create-stack \
  --stack-name athena-business-hours \
  --template-body file://athena-business-hours-automation.yaml \
  --parameters ParameterKey=WorkgroupName,ParameterValue=primary \
               ParameterKey=StartImmediately,ParameterValue=true \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### 2. Monitor Deployment

```bash
aws cloudformation describe-stacks --stack-name athena-business-hours
```

### 3. Test Step Functions

Check the Step Functions console for execution status when `StartImmediately=true`.

## ⚙️ Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `WorkgroupName` | `primary` | Existing Athena workgroup to attach capacity |
| `InitialCapacity` | `24` | Initial DPU capacity (minimum 24) |
| `MaxCapacity` | `64` | Maximum DPU capacity for auto-scaling |
| `StartTime` | `0 8 ? * MON-FRI *` | Business start time (8 AM weekdays) |
| `EndTime` | `0 17 ? * MON-FRI *` | Business end time (5 PM weekdays) |
| `StartImmediately` | `false` | Start capacity immediately for testing |

## 📅 Schedule Configuration

The default schedule uses EventBridge cron expressions:

- **Start**: `0 8 ? * MON-FRI *` (8:00 AM, Monday-Friday)
- **Stop**: `0 17 ? * MON-FRI *` (5:00 PM, Monday-Friday)

### Custom Schedule Examples

```yaml
# 9 AM - 6 PM Pacific Time
StartTime: '0 16 ? * MON-FRI *'  # 9 AM PST = 4 PM UTC
EndTime: '0 1 ? * TUE-SAT *'     # 6 PM PST = 1 AM UTC next day

# 24/7 operation
StartTime: '0 0 ? * * *'         # Every day at midnight
EndTime: '59 23 ? * * *'         # Every day at 11:59 PM
```

## 🔧 Auto-scaling Configuration

The template integrates with the official AWS Athena auto-scaling template with these defaults:

- **High Utilization Threshold**: 75%
- **Low Utilization Threshold**: 25%
- **Scale Out Amount**: 16 DPUs
- **Scale In Amount**: 8 DPUs
- **Evaluation Frequency**: Every 5 minutes

## 💰 Cost Considerations

### Capacity Reservation Costs
- **Minimum**: 24 DPUs × business hours × DPU rate
- **Maximum**: 64 DPUs × business hours × DPU rate
- **Auto-scaling**: Adjusts capacity based on actual utilization

### Example Cost Calculation (US East 1)
```
Base Cost: 24 DPUs × 9 hours × 5 days × $0.30/DPU-hour = $324/week
Max Cost:  64 DPUs × 9 hours × 5 days × $0.30/DPU-hour = $864/week
```

## 🔍 Monitoring

### CloudWatch Metrics
- `AWS/Athena/DPUAllocated`: Current capacity allocation
- `AWS/Athena/DPUConsumed`: Actual utilization
- `AWS/StepFunctions/ExecutionsFailed`: Failed executions

### Step Functions Console
Monitor execution status and troubleshoot failures:
```
https://console.aws.amazon.com/states/home?region=us-east-1#/statemachines
```

## 🛠️ Troubleshooting

### Common Issues

1. **Minimum DPU Error**: Athena requires minimum 24 DPUs
2. **IAM Permissions**: Ensure CloudFormation has necessary IAM permissions
3. **Workgroup Not Found**: Verify workgroup exists before deployment
4. **Auto-scaling Deployment Fails**: Check Step Functions role permissions

### Debug Steps

1. **Check Step Functions Execution**:
   ```bash
   aws stepfunctions list-executions --state-machine-arn <arn>
   ```

2. **View CloudFormation Events**:
   ```bash
   aws cloudformation describe-stack-events --stack-name athena-business-hours
   ```

3. **Check Capacity Reservation Status**:
   ```bash
   aws athena get-capacity-reservation --name primary
   ```

## 🔒 Security

### IAM Permissions Required

The template creates IAM roles with minimal required permissions:

- **Step Functions Role**: CloudFormation, IAM, Athena, EventBridge, SNS
- **Lambda Execution Role**: Athena capacity management
- **EventBridge Role**: Step Functions execution

### Best Practices

- Use least-privilege IAM policies
- Enable CloudTrail for audit logging
- Monitor capacity usage and costs
- Set up billing alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/athena-business-hours-automation/issues)
- **AWS Documentation**: [Athena Capacity Reservations](https://docs.aws.amazon.com/athena/latest/ug/capacity-reservations.html)
- **Auto-scaling Template**: [Official AWS Template](https://athena-downloads.s3.us-east-1.amazonaws.com/templates/capacity-reservation-scaling/state-machine/athena-capacity-reservation-scaling-template-v1.0.yaml)

## 🏷️ Tags

`aws` `athena` `cloudformation` `step-functions` `eventbridge` `auto-scaling` `cost-optimization` `business-hours` `serverless`
