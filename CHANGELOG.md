# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-05

### Added
- Initial release of Athena Business Hours Automation
- CloudFormation template for automated capacity management
- Step Functions orchestration for lifecycle management
- EventBridge scheduling for business hours (8 AM - 5 PM weekdays)
- Integration with official AWS Athena auto-scaling template
- Lambda functions for capacity reservation management
- SNS notifications for status updates
- Immediate start option for testing (`StartImmediately` parameter)
- Comprehensive IAM roles with least-privilege permissions
- Support for custom business hours via cron expressions
- Cost optimization through business-hours-only operation
- Complete documentation and examples

### Features
- **Business Hours Scheduling**: Automatic start/stop during configurable hours
- **Auto-scaling Integration**: Dynamic capacity adjustment based on utilization
- **Testing Support**: Immediate start capability for validation
- **Lifecycle Management**: Complete create → attach → scale → cleanup workflow
- **Monitoring**: CloudWatch metrics and Step Functions visibility
- **Flexibility**: Configurable capacity limits and schedules

### Technical Details
- Minimum capacity: 24 DPUs (AWS requirement)
- Default capacity range: 24-64 DPUs
- Auto-scaling thresholds: 75% scale-up, 25% scale-down
- Evaluation frequency: Every 5 minutes
- Supported regions: All AWS regions with Athena capacity reservations

### Documentation
- Comprehensive README with setup instructions
- Deployment examples for different use cases
- Troubleshooting guide for common issues
- Cost calculation examples
- Security best practices
- Contributing guidelines

### Examples
- Default deployment script
- Test deployment with immediate start
- Custom schedule deployment (Pacific Time example)
- Production-ready configuration

## [Unreleased]

### Planned
- Multi-region support
- Custom notification channels (Slack, Teams)
- Advanced scheduling patterns
- Cost reporting integration
- Terraform version of templates
