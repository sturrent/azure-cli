# AKS Net-Diagnostics Integration Planning

This directory contains the planning documents for integrating the **aks-net-diagnostics** tool into Azure CLI as an `az aks net-diagnostics` subcommand.

## 📋 Quick Links

### Essential Documents (Read in Order)
1. **[planning/POC-APPROACH.md](./planning/POC-APPROACH.md)** - ⭐ Start here for POC strategy
2. **[planning/00-overview.md](./planning/00-overview.md)** - High-level overview
3. **[planning/03-task-list.md](./planning/03-task-list.md)** - Task tracker with estimates
4. **[guides/DEVELOPMENT-SETUP.md](./guides/DEVELOPMENT-SETUP.md)** - Environment setup guide
5. **[progress/PHASE5-PROGRESS.md](./progress/PHASE5-PROGRESS.md)** - 🎉 **Phase 5: COMPLETE (100%)** - Command registered and working!

### Additional Resources
- **[planning/01-analysis.md](./planning/01-analysis.md)** - Detailed technical analysis
- **[planning/02-integration-strategy.md](./planning/02-integration-strategy.md)** - Integration strategy
- **[planning/04-testing-plan.md](./planning/04-testing-plan.md)** - Testing strategy
- **[planning/05-questions-and-decisions.md](./planning/05-questions-and-decisions.md)** - Decisions log
- **[research/OUTPUT-FORMAT-ANALYSIS.md](./research/OUTPUT-FORMAT-ANALYSIS.md)** - Output formatting research

## 🎯 Quick Start

### For Reviewers
1. Start with [00-overview.md](./00-overview.md) to understand the project goals
2. Review [01-analysis.md](./01-analysis.md) to see what changes are needed
3. Check [02-integration-strategy.md](./02-integration-strategy.md) for the implementation approach

## 📖 Documentation

### Directory Structure

```
aks-net-diagnostics-integration/
├── README.md                    # This file - start here
├── planning/                    # Planning & strategy documents
│   ├── 00-overview.md           # High-level overview
│   ├── 01-analysis.md           # Detailed analysis
│   ├── 02-integration-strategy.md
│   ├── 03-task-list.md          # Main task tracker
│   ├── 04-testing-plan.md
│   ├── 05-questions-and-decisions.md
│   └── POC-APPROACH.md          # ⭐ POC strategy
├── research/                    # Research & analysis
│   └── OUTPUT-FORMAT-ANALYSIS.md
├── progress/                    # Phase progress reports
│   └── PHASE2-PROGRESS.md
└── guides/                      # Setup & how-to guides
    └── DEVELOPMENT-SETUP.md     # Environment setup
```

### For Implementers
1. Start with **[planning/POC-APPROACH.md](./planning/POC-APPROACH.md)** to understand the simplified strategy
2. Read planning documents in order (00-05 in `planning/` directory)
3. Follow **[guides/DEVELOPMENT-SETUP.md](./guides/DEVELOPMENT-SETUP.md)** to set up your environment
4. Track progress with **[planning/03-task-list.md](./planning/03-task-list.md)**
5. Check **[planning/05-questions-and-decisions.md](./planning/05-questions-and-decisions.md)** for decisions
6. Review phase reports in `progress/` directory

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
**Current Phase:** Phase 6 - Integration Testing (IN PROGRESS - 21% complete)  
**Completed Phases:**
- ✅ Phase 1: Planning (COMPLETE)
- ✅ Phase 2: Development Environment Setup (COMPLETE)
- ✅ Phase 3: Authentication Adapter (COMPLETE - 100%)
- ✅ Phase 4: Copy Diagnostic Modules (COMPLETE - 100%)
- ✅ Phase 5: Register Command (COMPLETE - 100%)

### Latest Progress

- 🟡 **Phase 6 IN PROGRESS** (October 20-21, 2025 - 38% complete)
  - ✅ **Category 1: Basic Execution Tests** - COMPLETE (6/6 tests passed)
  - ✅ **Category 2: Cluster-Specific Tests** - COMPLETE (15/15 tests passed)
  - ✅ Test 1.1: Basic command execution - PASSED
  - ✅ Test 1.2: --details flag - PASSED (122-line detailed report)
  - ✅ Test 1.3: --json-report flag - PASSED (38KB valid JSON)
  - ✅ Test 1.4: --probe-test flag - PASSED (connectivity tests working)
  - ✅ Test 1.5: Combined flags - PASSED
  - ✅ Test 1.6: All flags combined - PASSED
  - ✅ Test 2.1: Private cluster (aks-api-connection) - ALL PASSED
  - ✅ Test 2.2: Custom DNS cluster (aks-dns-ex1) - ALL PASSED
  - ✅ Test 2.3: Overlay networking (aks-overlay) - ALL PASSED
  - ✅ 16 bugs found and fixed (100% success rate)
  - ✅ Help text added with 4 comprehensive examples
  - ✅ Linter completely clean (CLI Linter, Pylint, Flake8: PASSED)
  - ✅ Code quality: 10.00/10 rating
  - 📊 Tests passing: 11/29 (38% - Category 1 + Category 2)
  - 🐛 All bugs fixed: Client architecture, API versions, findings display, linter warnings
  - Latest commits: fdb423c890 → 05d0e677d2 (21 commits)
  
- **Previous:** Phase 5 COMPLETE (Command registered and working)

### Quick Stats

- **Total Effort:** 24-34 hours POC (24 hours completed = 71%)
- **Current Phase:** Phase 6 - Integration Testing ⏳ (38% complete)
- **Code Quality:** 10.00/10 rating, all linters passing ✅
- **Next Phase:** Phase 7 - Documentation & Polish
- **See:** [📅 Timeline section below](#-timeline) for detailed phase breakdown

### Progress Checklist
- [x] **Phase 1: Planning** ✅ COMPLETE (June 2025)
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
- [x] **Phase 2: Development Environment Setup** ✅ COMPLETE (September 2025)
  - [x] Set up Python virtual environment (.venv)
  - [x] Install and configure azdev (0.2.7)
  - [x] Set up Azure CLI development environment
  - [x] Verify az commands working (v2.78.0)
  - [x] Clone aks-net-diagnostics repository
  - [x] Checkout azure-sdk branch
  - [x] Analyze dependencies
  - [x] Identify missing packages (azure-mgmt-network)
  - [x] Add azure-mgmt-network dependency
  - [x] Create comprehensive documentation
  - [x] Organize documentation structure
- [x] **Phase 3: Authentication Adapter** ✅ COMPLETE (October 2025)
  - [x] Phase 3.1: Review and analyze authentication patterns ✅
  - [x] Phase 3.2a: Add client factory functions ✅
  - [x] Phase 3.3: Create command handler in custom.py ✅
  - [x] Phase 3.4: Create orchestrator stub ✅
  - [x] Phase 3.5: Code quality perfection (10.00/10 pylint) ✅
- [x] **Phase 4: Copy Diagnostic Modules** ✅ COMPLETE (100% - October 2025)
  - [x] Phase 4.1: Foundation modules (_version, exceptions, models, validators) ✅
  - [x] Phase 4.2: Base analyzer class ✅
  - [x] Phase 4.3: Cluster data collector ✅
  - [x] Phase 4.4: All 7 analyzers ✅ COMPLETE
    - [x] dns_analyzer.py ✅
    - [x] route_table_analyzer.py ✅
    - [x] api_server_analyzer.py ✅
    - [x] outbound_analyzer.py ✅
    - [x] nsg_analyzer.py ✅
    - [x] connectivity_tester.py ✅
    - [x] misconfiguration_analyzer.py ✅
  - [x] Phase 4.5: Report generator ✅ COMPLETE
  - [x] Phase 4.6: Update orchestrator with real diagnostic logic ✅ COMPLETE
- [x] **Phase 5: Register Command** ✅ COMPLETE (October 2025)
  - [x] Register 'net-diagnostics' command in commands.py ✅
  - [x] Define all parameters in _params.py ✅
  - [x] Update command handler in custom.py ✅
  - [x] Test command registration and execution ✅
  - [x] Code quality validation (10.00/10 pylint) ✅
- [ ] **Phase 6: Integration Testing** ⏳ IN PROGRESS (21% complete - October 2025)
  - [x] Category 1: Basic Execution Tests ✅ COMPLETE (6/6)
    - [x] Test 1.1: Basic command execution ✅
    - [x] Test 1.2: --details flag ✅
    - [x] Test 1.3: --json-report flag ✅
    - [x] Test 1.4: --probe-test flag ✅
    - [x] Test 1.5: Combined flags ✅
    - [x] Test 1.6: All flags combined ✅
  - [ ] Category 2-7: Advanced testing ⏳ PENDING (23/29 tests remaining)
  - [x] Bug fixes: 16/16 fixed (100% success rate) ✅

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
├── aks-net-diagnostics-integration/    # ← Documentation (HERE)
│   ├── README.md                       # ← This file
│   ├── planning/                       # Planning documents
│   ├── research/                       # Research & analysis
│   ├── progress/                       # Phase reports
│   └── guides/                         # Setup guides
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
| Phase 1: Planning | 5 hours | ✅ COMPLETE |
| Phase 2: Development Environment Setup | 15 minutes | ✅ COMPLETE |
| Phase 3: Authentication Adapter | 3-4 hours | ✅ COMPLETE |
| Phase 4: Copy Diagnostic Modules | 8-10 hours | ✅ COMPLETE |
| Phase 5: Register Command & Parameters | 1 hour | ✅ COMPLETE |
| Phase 6: Integration Testing | 4-6 hours | ⏳ NEXT (Current) |
| Phase 7: Documentation & Polish | 2-4 hours | 🔴 Not Started |
| **TOTAL (POC)** | **24-34 hours** | **~18 hours completed** |

**Note:** Using POC approach - deferring output formatting refactoring. Timeline assumes working on this as a focused effort. Calendar time will vary based on availability and review cycles.

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

**Last Updated:** October 20, 2025  
**Current Phase:** Phase 6 - Integration Testing & Validation  
**Status:** 5 of 7 phases complete (18 hours / ~53% of POC)  
**Next Action:** Test command with real AKS cluster  
**Environment:** Python 3.10.12, Azure CLI 2.78.0 (dev mode), azdev 0.2.7
