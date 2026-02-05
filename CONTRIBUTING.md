# Contributing to Athena Business Hours Automation

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information**:
   - AWS region and account setup
   - CloudFormation template version
   - Error messages and logs
   - Steps to reproduce

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly** (see Testing section below)
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Submit a pull request**

## 🧪 Testing

### Local Testing

Before submitting changes, test your modifications:

1. **Validate CloudFormation template**:
   ```bash
   aws cloudformation validate-template --template-body file://athena-business-hours-automation.yaml
   ```

2. **Deploy to test environment**:
   ```bash
   ./examples/deploy-test.sh test-stack-name test-workgroup
   ```

3. **Verify functionality**:
   - Check Step Functions execution
   - Verify capacity reservation creation
   - Test auto-scaling deployment
   - Confirm cleanup process

### Test Checklist

- [ ] CloudFormation template validates successfully
- [ ] All parameters work as expected
- [ ] IAM permissions are minimal and functional
- [ ] Step Functions execute without errors
- [ ] Auto-scaling integration works
- [ ] Cleanup process completes successfully
- [ ] Documentation is updated

## 📝 Code Standards

### CloudFormation Templates

- Use consistent indentation (2 spaces)
- Include comprehensive parameter descriptions
- Add meaningful resource names with `!Sub` references
- Include proper IAM permissions (least privilege)
- Add helpful outputs

### Documentation

- Update README.md for new features
- Include examples for new parameters
- Add troubleshooting steps for common issues
- Keep documentation clear and concise

### Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Custom timezone support for business hours

- Add timezone parameter to template
- Update EventBridge cron expressions
- Include timezone examples in documentation
- Add validation for timezone format
```

## 🏷️ Pull Request Guidelines

### Before Submitting

- [ ] Code follows project standards
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive information in code

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested locally
- [ ] CloudFormation validation passed
- [ ] Step Functions execution verified

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🐛 Bug Reports

When reporting bugs, include:

1. **Environment details**:
   - AWS region
   - CloudFormation template version
   - Parameter values used

2. **Steps to reproduce**:
   - Exact commands run
   - Configuration used
   - Expected vs actual behavior

3. **Error information**:
   - CloudFormation events
   - Step Functions execution logs
   - Lambda function logs

## 💡 Feature Requests

For new features:

1. **Describe the use case** clearly
2. **Explain the benefit** to users
3. **Suggest implementation** approach
4. **Consider backward compatibility**

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **AWS Documentation**: For Athena and CloudFormation specifics

## 🎯 Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/athena-business-hours-automation.git
   cd athena-business-hours-automation
   ```

2. **Set up AWS CLI** with appropriate permissions

3. **Create test workgroup** for development:
   ```bash
   aws athena create-work-group --name test-workgroup
   ```

4. **Test deployment**:
   ```bash
   ./examples/deploy-test.sh dev-test test-workgroup
   ```

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
