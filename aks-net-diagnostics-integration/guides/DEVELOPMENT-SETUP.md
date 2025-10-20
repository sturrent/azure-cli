# Development Setup Guide

**Date:** October 19, 2025  
**Purpose:** Step-by-step guide for setting up development environment with virtual environment

## Overview

This guide will help you set up a proper Python virtual environment for Azure CLI development and clone the aks-net-diagnostics repository.

## Prerequisites

- Python 3.8 or higher
- Git
- pip

## Step 1: Create Python Virtual Environment

### 1.1 Create Virtual Environment

```bash
# Navigate to project root
cd /home/sturrent/gitrepos/azure-cli

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show .venv path)
which python
which pip
```

**Expected Output:**
```
/home/sturrent/gitrepos/azure-cli/.venv/bin/python
/home/sturrent/gitrepos/azure-cli/.venv/bin/pip
```

### 1.2 Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

## Step 2: Install Azure CLI in Development Mode

### 2.1 Install azdev

```bash
pip install azdev
```

### 2.2 Setup Azure CLI Development Environment

```bash
# Setup azdev with azure-cli repository
azdev setup -c azure-cli

# This will:
# - Install Azure CLI modules in editable mode
# - Set up command table
# - Configure development environment
```

### 2.3 Verify Azure CLI Installation

```bash
# Check az command works
az --version

# Try an AKS command
az aks --help
```

## Step 3: Clone aks-net-diagnostics Repository

### 3.1 Navigate to Working Directory

```bash
# Create a workspace directory for both repos
mkdir -p /home/sturrent/gitrepos/workspace
cd /home/sturrent/gitrepos/workspace
```

### 3.2 Clone Repository

```bash
# Clone the repository
git clone https://github.com/sturrent/aks-net-diagnostics.git

# Navigate to repository
cd aks-net-diagnostics

# Checkout azure-sdk branch
git checkout azure-sdk

# Verify branch
git branch
# Should show: * azure-sdk
```

### 3.3 Review Structure

```bash
# List files
ls -la

# Key files to review:
# - aks-net-diagnostics.py (main script)
# - azure_sdk_client.py (SDK client we need to adapt)
# - aks_diagnostics/ directory (modules to integrate)
# - requirements.txt (dependencies)
```

## Step 4: Install aks-net-diagnostics Dependencies

**Note:** Install in the same virtual environment as Azure CLI

```bash
# Make sure you're in the azure-cli venv
cd /home/sturrent/gitrepos/azure-cli
source .venv/bin/activate

# Install aks-net-diagnostics dependencies
cd /home/sturrent/gitrepos/workspace/aks-net-diagnostics
pip install -r requirements.txt

# Verify key packages are installed
pip list | grep azure
```

## Step 5: Review Key Files

### 5.1 Review azure_sdk_client.py

```bash
cd /home/sturrent/gitrepos/workspace/aks-net-diagnostics
cat azure_sdk_client.py | head -100
```

**Key things to note:**
- How `DefaultAzureCredential` is initialized
- Which Azure SDK clients are created
- Methods that need CLI authentication context

### 5.2 Review Main Orchestrator

```bash
cat aks-net-diagnostics.py | head -150
```

**Key things to note:**
- How arguments are parsed
- How orchestrator is initialized
- Entry point structure

### 5.3 Review Modules

```bash
# List all analyzer modules
ls -la aks_diagnostics/analyzers/

# Review one analyzer as example
cat aks_diagnostics/analyzers/nsg_analyzer.py | head -50
```

## Step 6: Run Existing Tests

Verify the standalone tool works in our environment:

```bash
cd /home/sturrent/gitrepos/workspace/aks-net-diagnostics

# Run unit tests
python -m pytest tests/ -v

# Check test coverage
pytest --cov=aks_diagnostics tests/
```

## Step 7: Verify Environment

### 7.1 Check Python Environment

```bash
# Should show azure-cli venv
which python
python --version

# Check installed packages
pip list | grep -E "(azure-cli|azdev|azure-mgmt)"
```

### 7.2 Verify Both Repos Available

```bash
# Azure CLI repo
ls /home/sturrent/gitrepos/azure-cli/src/azure-cli/azure/cli/command_modules/acs/

# aks-net-diagnostics repo
ls /home/sturrent/gitrepos/workspace/aks-net-diagnostics/aks_diagnostics/
```

## Directory Structure After Setup

```
/home/sturrent/gitrepos/
├── azure-cli/                          # Azure CLI repository
│   ├── .venv/                          # Virtual environment (created)
│   ├── aks-net-diagnostics-integration/  # Planning docs
│   └── src/azure-cli/azure/cli/command_modules/acs/  # Target location
└── workspace/
    └── aks-net-diagnostics/            # Source tool (cloned)
        ├── azure_sdk_client.py         # Key file to adapt
        ├── aks-net-diagnostics.py      # Main script
        └── aks_diagnostics/            # Modules to integrate
```

## Common Issues & Solutions

### Issue 1: Virtual Environment Not Activated

**Symptom:** `which python` shows system Python, not .venv

**Solution:**
```bash
cd /home/sturrent/gitrepos/azure-cli
source .venv/bin/activate
```

### Issue 2: azdev setup fails

**Symptom:** Error during `azdev setup`

**Solution:**
```bash
# Make sure you're in azure-cli directory
cd /home/sturrent/gitrepos/azure-cli
source .venv/bin/activate

# Try with verbose output
azdev setup -c azure-cli -v
```

### Issue 3: Import errors when running tests

**Symptom:** `ModuleNotFoundError: No module named 'azure'`

**Solution:**
```bash
# Reinstall Azure CLI in development mode
pip install -e src/azure-cli
pip install -e src/azure-cli-core
```

### Issue 4: Can't clone private repository

**Symptom:** `Permission denied (publickey)`

**Solution:**
```bash
# Make sure you have SSH key configured
# Or use HTTPS with token:
git clone https://github.com/sturrent/aks-net-diagnostics.git
```

## Environment Variables

Useful environment variables for development:

```bash
# Add to ~/.bashrc or ~/.zshrc for convenience

# Azure CLI development
export AZURE_CLI_DEV_MODE=1

# Python
export PYTHONPATH=/home/sturrent/gitrepos/azure-cli/src:$PYTHONPATH

# Activate venv automatically when entering directory
alias azcli-dev='cd /home/sturrent/gitrepos/azure-cli && source .venv/bin/activate'
```

## Next Steps

After completing setup:

1. ✅ Review `azure_sdk_client.py` authentication flow
2. ✅ Map Azure SDK clients used
3. ✅ Identify credential initialization points
4. ✅ Begin designing authentication adapter
5. ✅ Start Phase 3: Authentication Adapter implementation

## Quick Reference Commands

```bash
# Activate virtual environment
cd /home/sturrent/gitrepos/azure-cli && source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Run Azure CLI from development
az --version

# Run aks-net-diagnostics tests
cd /home/sturrent/gitrepos/workspace/aks-net-diagnostics && pytest tests/

# Build Azure CLI
cd /home/sturrent/gitrepos/azure-cli && azdev linter && azdev test azure-cli-acs
```

## Verification Checklist

- [ ] Virtual environment created and activated
- [ ] pip upgraded
- [ ] azdev installed
- [ ] Azure CLI setup in development mode
- [ ] `az --version` works
- [ ] aks-net-diagnostics repository cloned
- [ ] azure-sdk branch checked out
- [ ] aks-net-diagnostics dependencies installed
- [ ] aks-net-diagnostics tests pass
- [ ] Can view both repositories' files
- [ ] Ready to begin Phase 3
