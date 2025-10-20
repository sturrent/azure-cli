# AKS Net-Diagnostics Integration Planning

This directory contains the planning documents for integrating the **aks-net-diagnostics** tool into Azure CLI as an `az aks net-diagnostics` subcommand.

## 📋 Planning Documents

1. **[00-overview.md](./00-overview.md)** - Project overview, goals, and current state
2. **[01-analysis.md](./01-analysis.md)** - Detailed technical analysis of required changes
3. **[02-integration-strategy.md](./02-integration-strategy.md)** - Chosen integration approach and implementation plan
4. **[03-task-list.md](./03-task-list.md)** - Actionable task list with priorities and timeline
5. **[04-testing-plan.md](./04-testing-plan.md)** - Comprehensive testing strategy
6. **[05-questions-and-decisions.md](./05-questions-and-decisions.md)** - Open questions, decisions log, and risks

## 🎯 Quick Start

### For Reviewers
1. Start with [00-overview.md](./00-overview.md) to understand the project goals
2. Review [01-analysis.md](./01-analysis.md) to see what changes are needed
3. Check [02-integration-strategy.md](./02-integration-strategy.md) for the implementation approach

### For Implementers
1. Read all planning documents in order
2. Start with **POC-APPROACH.md** to understand the simplified strategy
3. Follow the task list in [03-task-list.md](./03-task-list.md)
4. Refer to [04-testing-plan.md](./04-testing-plan.md) for testing strategy
5. Check [05-questions-and-decisions.md](./05-questions-and-decisions.md) for decisions

## 🔑 Key Points

### What We're Building
```bash
# Users will be able to run:
az aks net-diagnostics -n myCluster -g myResourceGroup --details --probe-test --json-report
```

### POC Approach
- **Goal:** Prove feasibility of integration before full refinement
- **Keep:** Existing aks-net-diagnostics output format (text + colors)
- **Focus:** Authentication adapter + command integration
- **Defer:** Output formatting refactoring (json/table/yaml/tsv support)
- **See:** POC-APPROACH.md for complete strategy

### Main Challenges
1. **Authentication:** Adapt Azure SDK client to use CLI's authentication context (`cmd.cli_ctx`)
2. **Argument Handling:** Remove argparse, use CLI's parameter system
3. **Code Structure:** Adapt standalone script to CLI command function pattern
4. **Integration:** Register command and define parameters in Azure CLI framework

### Critical Changes Required
- Remove `parse_arguments()` method from orchestrator
- Adapt `azure_sdk_client.py` to use `cmd.cli_ctx` instead of `DefaultAzureCredential`
- Modify main orchestrator to accept parameters as function arguments
- Register command in `commands.py`
- Define parameters in `_params.py`
- Create command handler function

## 📊 Project Status

**Branch:** `aks-net-diagnostics-integration`  
**Phase:** Planning - Phase 1 ✅ COMPLETE  
**Next Phase:** Phase 2 - Code Preparation

### Estimated Timeline (POC Approach)
- **Total Effort:** 25-35 hours (simplified POC approach)
- **Integration Complexity:** Medium (tool already uses Azure SDK)
- **Primary Work:** Authentication adaptation and CLI framework integration
- **Deferred:** Output formatting refactoring (post-POC)

### Progress Checklist
- [x] Create planning documents
- [x] Analyze aks-net-diagnostics architecture (azure-sdk branch)
- [x] Analyze Azure CLI ACS module structure
- [x] Identify parameter conflicts
- [x] Map required changes
- [x] Define integration strategy
- [x] Create comprehensive task list
- [x] Create testing plan
- [x] Define POC approach
- [x] Research output formatting options
- [ ] Clone and review azure-sdk branch implementation
- [ ] Prototype SDK client authentication adaptation
- [ ] Begin code integration

## 🛠️ Development Setup

### Prerequisites
```bash
# Install azdev
pip install azdev

# Setup development environment
cd /home/sturrent/gitrepos/azure-cli
azdev setup -c

# Verify setup
az --version
```

### Working Branch
```bash
# Current branch
git branch
# Should show: * aks-net-diagnostics-integration

# View planning documents
ls -la aks-net-diagnostics-integration/
```

## 📁 Project Structure

### Current Repository Structure
```
azure-cli/
├── aks-net-diagnostics-integration/    # ← Planning documents (HERE)
│   ├── README.md                       # ← This file
│   ├── 00-overview.md
│   ├── 01-analysis.md
│   ├── 02-integration-strategy.md
│   ├── 03-task-list.md
│   ├── 04-testing-plan.md
│   └── 05-questions-and-decisions.md
└── src/
    └── azure-cli/
        └── azure/
            └── cli/
                └── command_modules/
                    └── acs/                # ← Where code will go
                        ├── __init__.py
                        ├── commands.py     # ← Will modify
                        ├── _params.py      # ← Will modify
                        ├── custom.py       # ← Will modify or create new file
                        └── net_diagnostics/ # ← Will create
                            └── ...
```

### Target Structure After Integration
```
src/azure-cli/azure/cli/command_modules/acs/
└── net_diagnostics/                    # NEW
    ├── __init__.py
    ├── orchestrator.py                 # Adapted from aks-net-diagnostics.py
    ├── sdk_client.py                   # Adapted from azure_sdk_client.py
    ├── analyzers/
    │   ├── __init__.py
    │   ├── base_analyzer.py
    │   ├── nsg_analyzer.py
    │   ├── dns_analyzer.py
    │   ├── route_table_analyzer.py
    │   ├── api_server_analyzer.py
    │   ├── connectivity_tester.py
    │   ├── outbound_analyzer.py
    │   └── misconfiguration_analyzer.py
    ├── collectors/
    │   ├── __init__.py
    │   └── cluster_data_collector.py
    ├── report_generator.py
    ├── models.py
    ├── exceptions.py
    └── validators.py
```

## 🔗 References

### aks-net-diagnostics (Source)
- **Repository:** https://github.com/sturrent/aks-net-diagnostics
- **Branch:** `azure-sdk`
- **Documentation:** 
  - [README](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/README.md)
  - [ARCHITECTURE](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/docs/ARCHITECTURE.md)
  - [CONTRIBUTING](https://github.com/sturrent/aks-net-diagnostics/blob/azure-sdk/CONTRIBUTING.md)

### Azure CLI Documentation
- [Configuring Your Machine](https://github.com/Azure/azure-cli/blob/dev/doc/configuring_your_machine.md)
- [Authoring Command Modules](https://github.com/Azure/azure-cli/tree/dev/doc/authoring_command_modules)
- [Command Guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/command_guidelines.md)
- [Authoring Tests](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md)

### Azure SDK
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Management Libraries](https://docs.microsoft.com/en-us/python/api/overview/azure/mgmt?view=azure-python)

## 💡 Key Decisions

1. **Integration Type:** Core ACS module (not extension)
2. **Command Name:** `az aks net-diagnostics`
3. **Source Branch:** Use `azure-sdk` branch (already uses Azure SDK directly)
4. **Directory Structure:** Create `net_diagnostics/` subdirectory under ACS module
5. **Authentication:** Adapt SDK client to use CLI's `cmd.cli_ctx` instead of `DefaultAzureCredential`
6. **Feature Parity:** Include all features from standalone tool (including --probe-test)

## ⚠️ Open Questions

See [05-questions-and-decisions.md](./05-questions-and-decisions.md) for:
- Authentication context handling
- VMSS run-command implementation
- Output formatting conventions
- Error handling standards
- Testing requirements

## 📅 Timeline

| Phase | Estimated Hours | Status |
|-------|----------------|--------|
| Phase 1: Planning | 5 hours | 🟢 95% Complete |
| Phase 2: Code Preparation | 4-5 hours | 🔴 Not Started |
| Phase 3: Integration | 8-12 hours | 🔴 Not Started |
| Phase 4: Testing | 8-12 hours | 🔴 Not Started |
| Phase 5: Documentation | 4-6 hours | 🔴 Not Started |
| Phase 6: Review & Merge | 4-8 hours | 🔴 Not Started |
| **TOTAL** | **33-48 hours** | |

**Note:** Timeline assumes working on this as a focused effort. Calendar time will vary based on availability and review cycles.

## 🤝 Contributing

This is an integration project. If you want to help:

1. Review the planning documents
2. Ask questions in [05-questions-and-decisions.md](./05-questions-and-decisions.md)
3. Pick tasks from [03-task-list.md](./03-task-list.md)
4. Follow the integration strategy in [02-integration-strategy.md](./02-integration-strategy.md)
5. Write tests per [04-testing-plan.md](./04-testing-plan.md)

## 📞 Contact

- **Project Lead:** [Your name/contact]
- **Azure CLI Team:** [Contact info]
- **ACS Module Owners:** [Contact info]

## 📝 Notes

- This is a **planning directory only** - no production code here yet
- All code changes will go in `src/azure-cli/azure/cli/command_modules/acs/`
- Keep this directory updated as the project progresses
- Document decisions and changes in the appropriate planning files

---

**Last Updated:** October 19, 2025  
**Current Focus:** Complete Phase 1 planning, prepare for Phase 2 implementation  
**Next Milestone:** Clone azure-sdk branch and prototype authentication adaptation
