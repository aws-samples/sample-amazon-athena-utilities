# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create Public Issues

Please **do not** create public GitHub issues for security vulnerabilities. This could put users at risk.

### 2. Report Privately

Send security reports to: [security@yourproject.com] or create a private security advisory on GitHub.

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (1-30 days)

## Security Best Practices

### AWS IAM Permissions

The CloudFormation template follows least-privilege principles:

- **Step Functions Role**: Only necessary CloudFormation, IAM, and AWS service permissions
- **Lambda Execution Role**: Limited to Athena capacity management
- **EventBridge Role**: Only Step Functions execution permissions

### Recommended Security Measures

1. **Enable CloudTrail**: Monitor all API calls
2. **Use IAM Roles**: Avoid long-term access keys
3. **Enable MFA**: For administrative accounts
4. **Monitor Costs**: Set up billing alerts
5. **Regular Reviews**: Audit IAM permissions periodically

### Template Security Features

- No hardcoded credentials
- Minimal IAM permissions
- Resource-specific access controls
- CloudFormation drift detection support
- Proper resource tagging for governance

### Known Security Considerations

1. **IAM Permissions**: The template requires broad IAM permissions to create nested resources
2. **Cross-Service Access**: Step Functions needs access to multiple AWS services
3. **Auto-scaling Template**: Deploys third-party AWS template with its own permissions

### Mitigation Strategies

- Deploy in isolated AWS accounts for testing
- Use AWS Organizations SCPs to limit permissions
- Monitor CloudTrail logs for unexpected activity
- Implement resource-based policies where possible

## Vulnerability Disclosure

We follow responsible disclosure practices:

1. **Private Report**: Security issues reported privately
2. **Investigation**: We investigate and develop fixes
3. **Coordinated Release**: Fix released with security advisory
4. **Public Disclosure**: Details shared after fix is available

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 1.0.1)
- Documented in CHANGELOG.md
- Announced via GitHub releases
- Tagged with security labels

## Contact

For security-related questions or concerns:
- Email: [security@yourproject.com]
- GitHub Security Advisories: [Create Private Advisory]
- Response Time: 48 hours maximum
