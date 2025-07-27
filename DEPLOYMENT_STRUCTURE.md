# AWS Lambda Deployment Structure - Updated

## Overview
The project has been reorganized to properly separate Lambda function code from dependencies, reducing deployment package size and following AWS Lambda best practices.

## Directory Structure

### `line-bot-deployment/` - Lambda Function Code (96KB)
Contains only the Lambda function code files:
- `lambda_function.py` - Main Lambda function entry point
- `funcs.py` - Custom function modules
- `weekly-notify.py` - Weekly notification functionality
- `__pycache__/` - Python cache files (automatically generated)

### `python/` - Lambda Layer Libraries (33.6MB)
Contains all third-party dependencies and libraries:
- All Python packages and their dependencies
- boto3, azure, linebot, PIL, pydantic, requests, etc.
- This becomes the Lambda Layer

## Deployment Process

### 1. Deploy Lambda Layer
```bash
# Create layer zip file
zip-command-for-layer.bat
# This creates layer.zip (33.6MB) containing all libraries
```

### 2. Deploy Lambda Function
```bash
# Create function zip file
zip-command.bat  
# This creates line-bot-deployment.zip (96KB) containing only function code
```

## Benefits

### Before Reorganization:
- Lambda function package: **40+ MB**
- Contained both function code and all libraries
- Slow deployment and updates
- Hit Lambda deployment size limits

### After Reorganization:
- Lambda function package: **96 KB** (417x smaller!)
- Lambda layer package: **33.6 MB**
- Fast deployment and updates for function code
- Efficient separation of concerns
- Better version management

## AWS Lambda Layer Setup

1. **Create Layer**: Upload `layer.zip` as a new Lambda Layer
2. **Attach Layer**: Configure your Lambda function to use the layer
3. **Deploy Function**: Upload `line-bot-deployment.zip` as your function code

## Key Changes Made

1. **Removed libraries from function directory**: All third-party packages moved to layer
2. **Updated zip commands**: 
   - Layer command no longer copies from function directory
   - Function command creates lightweight package
3. **Size optimization**: 99.7% reduction in function package size

## Files Modified
- `zip-command.bat` - Updated to show it creates function-only package
- `zip-command-for-layer.bat` - Simplified to only zip the python/ directory
- `cleanup-lambda-function.py` - Script used to remove libraries from function directory

## Notes
- Libraries are now shared across all Lambda functions that use the same layer
- Function code updates are much faster (96KB vs 40MB)
- Layer updates are separate from function updates
- This follows AWS Lambda best practices for dependency management
