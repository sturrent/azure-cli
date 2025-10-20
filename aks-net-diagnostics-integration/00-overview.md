# AKS Net-Diagnostics Integration - Overview

**Date Created:** October 19, 2025  
**Branch:** `aks-net-diagnostics-integration`  
**Target:** Integrate aks-net-diagnostics as `az aks net-diagnostics` subcommand

## Project Goal

Integrate the standalone aks-net-diagnostics tool (from https://github.com/sturrent/aks-net-diagnostics/tree/azure-sdk) into the Azure CLI as a subcommand under `az aks`.

### Desired User Experience

```bash
# Instead of:
python aks-net-diagnostics.py -n myCluster -g myResourceGroup --details --probe-test --json-report

# Users will run:
az aks net-diagnostics -n myCluster -g myResourceGroup --details --probe-test --json-report
```

## Current State

### aks-net-diagnostics (Standalone Tool)
- **Version:** 2.2.0 (Azure SDK branch)
- **Location:** https://github.com/sturrent/aks-net-diagnostics/tree/azure-sdk
- **Architecture:** Modular Python tool with 16 modules
- **Dependencies:** Azure SDK packages (NOT Azure CLI)
- **Size:** ~5,000 lines of code across modules
- **Tests:** 136 unit tests
- **Documentation:** Comprehensive (README, ARCHITECTURE, CONTRIBUTING)

### Azure CLI ACS Module
- **Location:** `src/azure-cli/azure/cli/command_modules/acs/`
- **Uses:** Azure CLI command framework
- **Dependencies:** Azure CLI libraries

## Key Challenges

### 1. Authentication
- **aks-net-diagnostics:** Uses `DefaultAzureCredential()` from Azure SDK
- **Azure CLI:** Uses `cmd.cli_ctx` for authentication context
- **Required Change:** Adapt `azure_sdk_client.py` to use CLI's authentication instead of `DefaultAzureCredential`
- **Impact:** Low complexity - primarily changing credential initialization

### 2. Argument Handling
- **aks-net-diagnostics:** Uses argparse directly
  - `-n NAME, --name NAME`
  - `-g RESOURCE_GROUP, --resource-group RESOURCE_GROUP`
  - `--subscription`
  - `--probe-test`
  - `--json-report [FILENAME]`
  - `--details`
  - `--version`
  - `--help`

- **Azure CLI:** Has its own argument system
  - Already handles `-n`, `-g`, `--subscription` globally
  - Has its own `--help` system
  - Has built-in version management
  - Must use Azure CLI's argument decorators

### 3. Code Structure
- **aks-net-diagnostics:** Standalone script with `main()` entry point and argparse
- **Azure CLI:** Command handler functions with parameters passed by framework
- **Required Change:** Convert orchestrator from standalone script to command handler function

### 4. Module Integration
- **aks-net-diagnostics:** Self-contained package with 16 modules
- **Azure CLI:** Must integrate into existing ACS command module structure
- **Required Change:** Organize code into `net_diagnostics/` subdirectory under ACS module

## Documentation References

### Azure CLI Documentation
- [Configuring Your Machine](https://github.com/Azure/azure-cli/blob/dev/doc/configuring_your_machine.md)
- [Authoring Command Modules](https://github.com/Azure/azure-cli/tree/dev/doc/authoring_command_modules)
- [Command Guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/command_guidelines.md)

### aks-net-diagnostics Documentation
- [README](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/README.md)
- [ARCHITECTURE](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/docs/ARCHITECTURE.md)
- [CONTRIBUTING](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/CONTRIBUTING.md)

## Next Steps

See the following planning documents:
1. `01-analysis.md` - Detailed analysis of required changes
2. `02-integration-strategy.md` - Chosen integration approach
3. `03-task-list.md` - Actionable task list with priorities
4. `04-testing-plan.md` - Testing strategy
5. `05-questions-and-decisions.md` - Open questions and decisions needed
