# AKS Net-Diagnostics Integration Planning

This directory contains the planning documents for integrating the **aks-net-diagnostics** tool into Azure CLI as an `az aks net-diagnostics` subcommand.

## 📋 Quick Links

### Essential Documents (Read in Order)
1. **[planning/POC-APPROACH.md](./planning/POC-APPROACH.md)** - ⭐ Start here for POC strategy
2. **[planning/00-overview.md](./planning/00-overview.md)** - High-level overview
3. **[planning/03-task-list.md](./planning/03-task-list.md)** - Task tracker with estimates
4. **[guides/DEVELOPMENT-SETUP.md](./guides/DEVELOPMENT-SETUP.md)** - Environment setup guide
5. **[progress/PHASE6-COMPLETION.md](./progress/PHASE6-COMPLETION.md)** - 🎉 **Phase 6: COMPLETE (100%)** - All testing complete!
6. **[progress/PHASE7-PROGRESS.md](./progress/PHASE7-PROGRESS.md)** - 🎉 **Phase 7: COMPLETE (100%)** - Permission handling & UX improvements complete!
7. **[planning/06-phase8-pod-cidr-nodepool.md](./planning/06-phase8-pod-cidr-nodepool.md)** - 📋 **Phase 8: PLANNED** - Pod CIDR & node pool display

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
**Current Phase:** Phase 8 - Node Pool Display & Pod CIDR Enhancement ⏳ (Next)  
**Completed Phases:**
- ✅ Phase 1: Planning (COMPLETE)
- ✅ Phase 2: Development Environment Setup (COMPLETE)
- ✅ Phase 3: Authentication Adapter (COMPLETE - 100%)
- ✅ Phase 4: Copy Diagnostic Modules (COMPLETE - 100%)
- ✅ Phase 5: Register Command (COMPLETE - 100%)
- ✅ Phase 6: Integration Testing (COMPLETE - 100%)
  - 33+ formal tests executed
  - 6+ exploration tests conducted
  - **24 bugs found and fixed (100% resolution rate)**
  - 5 test clusters validated
  - All outbound types tested (loadBalancer, userDefinedRouting, managedNATGateway)
- ✅ Phase 7: UX Improvements & Permission Handling (COMPLETE - 100%)
  - Comprehensive permission error handling
  - 3 permission-specific finding codes
  - Authorization error detection across 4 analyzers
  - 100% false positive elimination
  - Tested across 3 network types (Overlay, Kubenet, Azure CNI Pod Subnet)

### Latest Progress

- ✅ **Phase 7 Complete! (October 22-23, 2025)**
  - ✅ Comprehensive permission error handling implemented
  - ✅ 3 permission-specific finding codes added (VNet, VMSS, LoadBalancer)
  - ✅ Authorization error detection across 4 analyzers
  - ✅ False positive prevention (NO_OUTBOUND_IPS, "No X found" messages)
  - ✅ Contextual findings summary with permission limitations
  - ✅ 7 UX improvements implemented
  - ✅ Tested with service principal (limited permissions)
  - ✅ Clean, consistent output formatting (removed emoji, [NOTE] prefix)
  - ✅ **Outbound IP display bug fixed** - now shows actual IPs instead of resource IDs
  - ✅ README documentation cleanup (emoji fixes, streamlined setup)
  - ✅ **Comprehensive testing across network types:**
    - ✅ Azure CNI Overlay (aks-overlay) - pod CIDR: 10.244.0.0/16
    - ✅ Kubenet (aks-kubenet-byo-vnet-bicep) - route tables detected
    - ✅ Azure CNI Pod Subnet (aks-acni-podsubnet) - multiple node pools
  - 📊 7 files modified for permission handling
  - 🎯 100% false positive elimination
  - 🐛 Outbound IP bug discovered during cross-tenant testing and fixed
  - � Phase 7 completion report created
  - Latest commits: 6bb51ad442, 60a81cda26, 1a1a854a4e, ace0d843a7

- 📋 **Phase 8 Planning Complete! (October 23, 2025)**
  - 📝 Comprehensive planning document created (planning/06-phase8-pod-cidr-nodepool.md)
  - 🔍 **Discovery:** Azure CNI Pod Subnet stores pod CIDRs per-pool, not in networkProfile
  - 📊 4 Azure CNI variants documented (Node Subnet, Overlay, Pod Subnet, Kubenet)
  - 🎯 Implementation plan: Pod CIDR detection + Node pool display
  - ✅ Testing matrix defined for all cluster types
  - **Scope:** Fix empty pod CIDR for Azure CNI Pod Subnet + display node pool details
  
- **Next:** Phase 8 Implementation - Pod CIDR Enhancement & Node Pool Display

### Quick Stats

- **Total Effort:** 24-34 hours POC estimate
- **Time Spent:** ~28 hours (Phase 7 complete + Phase 8 planning)
- **Current Phase:** Phase 8 - Pod CIDR & Node Pool Display ⏳ (Planned - Ready to Execute)
- **Code Quality:** 10.00/10 rating, all linters passing ✅
- **Test Success Rate:** 100% (33+ formal + 6+ exploration + permission scenarios + 3 network types)
- **Bug Fix Rate:** 100% (25 bugs found, 25 fixed - including outbound IP display)
- **Permission Handling:** ✅ Complete - Comprehensive error handling
- **Network Type Coverage:** 3/3 validated (Overlay, Kubenet, Azure CNI Pod Subnet)
- **POC Status:** ✅ Complete - Ready for Phase 8 enhancements
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
- [x] **Phase 6: Integration Testing** ✅ COMPLETE (October 2025)
  - [x] Category 1: Basic Execution Tests ✅ COMPLETE (6/6)
    - [x] Test 1.1-1.6: All parameter flags and combinations ✅
  - [x] Category 2: Cluster-Specific Tests ✅ COMPLETE (23/23)
    - [x] Test 2.1: Private cluster detection (6 tests) ✅
    - [x] Test 2.2: Authorized IP ranges (5 tests) ✅
    - [x] Test 2.3: Outbound type detection (9 tests) ✅
    - [x] Test 2.4: NAT Gateway scenarios (3 tests) ✅
  - [x] Category 3: Output Format Validation ✅ COMPLETE (4/4)
  - [x] Category 4: Error Handling ✅ COMPLETE (2/2)
  - [x] Category 5: Performance ✅ COMPLETE (1/1)
  - [x] 33+ formal tests executed, 100% pass rate ✅
  - [x] 6+ exploration tests with real-world scenarios ✅
  - [x] 24 bugs found and fixed (100% fix rate) ✅
    - [x] Bugs #1-20: Found during formal testing ✅
    - [x] Bug #21: Probe test results not visible in summary ✅
    - [x] Bug #22: Duplicate route table messages ✅
    - [x] Bug #23: Misleading API server failure diagnostics ✅
    - [x] Bug #24: Silent connectivity test execution ✅
  - [x] Phase 6 completion report created ✅
- [x] **Phase 7: UX Improvements & Permission Handling** ✅ COMPLETE (October 2025)
  - [x] Implement permission error detection ✅
  - [x] Add permission-specific finding codes (VNet, VMSS, LoadBalancer) ✅
  - [x] Create authorization error detection pattern ✅
  - [x] Apply to cluster_data_collector (VNet, VMSS) ✅
  - [x] Apply to outbound_analyzer (LoadBalancer) ✅
  - [x] Apply to dns_analyzer (VNet for DNS) ✅
  - [x] Prevent false NO_OUTBOUND_IPS warnings ✅
  - [x] Fix outbound IPs display when permission limited ✅
  - [x] Remove emoji from execution logs ✅
  - [x] Remove [NOTE] prefix for consistency ✅
  - [x] Add contextual findings summary ✅
  - [x] Separate permission findings in report ✅
  - [x] Test with service principal (limited permissions) ✅
  - [x] Fix outbound IP display bug (resource ID → actual IP) ✅
  - [x] README documentation cleanup ✅
  - [x] Test across 3 network types (Overlay, Kubenet, Azure CNI Pod Subnet) ✅
  - [x] Validate multiple node pool detection ✅
  - [x] Phase 7 progress report created ✅
  - [x] All code quality checks passing (linter, pylint, flake8) ✅
- [ ] **Phase 8: Node Pool Display & Pod CIDR Enhancement** ⏳ PLANNED (Next)
  - [x] Planning complete - comprehensive design document created ✅
  - [x] Azure CNI variants analysis complete ✅
  - [x] Testing matrix defined ✅
  - [ ] Implement pod CIDR detection for Azure CNI Pod Subnet
  - [ ] Add node pool display to detailed report
  - [ ] Test with all 4 Azure CNI variants
  - [ ] Code quality validation
  - See: [planning/06-phase8-pod-cidr-nodepool.md](./planning/06-phase8-pod-cidr-nodepool.md)

## 🛠️ Development Setup

For complete development environment setup instructions, see **[guides/DEVELOPMENT-SETUP.md](./guides/DEVELOPMENT-SETUP.md)**.

Quick reference:
- Python 3.10.12
- Azure CLI 2.78.0 (dev mode)
- azdev 0.2.7
- Working branch: `aks-net-diagnostics-integration`

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
| Phase 6: Integration Testing | 4-6 hours | ✅ COMPLETE |
| Phase 7: Permission Handling & UX | 2-4 hours | ✅ COMPLETE |
| Phase 8: Pod CIDR & Node Pool Display | 2-3 hours | 📋 PLANNED |
| **TOTAL (POC)** | **24-34 hours** | **~28 hours completed** |

**Note:** Using POC approach - deferring output formatting refactoring. Timeline assumes working on this as a focused effort. Calendar time will vary based on availability and review cycles.

**Phase 7 Summary:**
- 7 files modified for comprehensive permission handling
- 3 permission-specific finding codes added
- Authorization error detection across 4 analyzers
- 100% false positive elimination
- Tested across 3 network types (Overlay, Kubenet, Azure CNI Pod Subnet)
- Critical outbound IP display bug fixed
- Documentation cleaned up
- Phase 8 fully planned and ready for implementation

## 🤝 Contributing

This is an integration project. If you want to help:

1. Review the planning documents
2. Ask questions in [05-questions-and-decisions.md](./planning/05-questions-and-decisions.md)
3. Pick tasks from [03-task-list.md](./planning/03-task-list.md)
4. Follow the integration strategy in [02-integration-strategy.md](./planning/02-integration-strategy.md)
5. Write tests per [04-testing-plan.md](./planning/04-testing-plan.md)

## 📝 Notes

- This is a **planning directory only** - no production code here yet
- All code changes will go in `src/azure-cli/azure/cli/command_modules/acs/`
- Keep this directory updated as the project progresses
- Document decisions and changes in the appropriate planning files

---

**Last Updated:** October 23, 2025  
**Current Phase:** Phase 8 - Pod CIDR Enhancement & Node Pool Display (Planned)  
**Status:** Phase 7 complete - All permission handling, testing, and bug fixes complete  
**Next Action:** Implement pod CIDR detection for Azure CNI Pod Subnet + node pool display  
**Environment:** Python 3.10.12, Azure CLI 2.78.0 (dev mode), azdev 0.2.7
