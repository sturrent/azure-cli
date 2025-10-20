# Task List

## High-Level Phases

- [x] **Phase 1:** Planning & Analysis ✅ COMPLETE
- [ ] **Phase 2:** Code Preparation ⏳ (Current)
- [ ] **Phase 3:** Integration Implementation
- [ ] **Phase 4:** Testing & Validation
- [ ] **Phase 5:** Documentation & Polish
- [ ] **Phase 6:** Review & Merge

---

## Phase 1: Planning & Analysis ✅ COMPLETE

### Documentation
- [x] Create `00-overview.md`
- [x] Create `01-analysis.md`
- [x] Create `02-integration-strategy.md`
- [x] Create `03-task-list.md` (this file)
- [x] Create `04-testing-plan.md`
- [x] Create `05-questions-and-decisions.md`

### Code Analysis
- [x] Review aks-net-diagnostics architecture (azure-sdk branch)
- [x] Review Azure CLI ACS module structure
- [x] Identify flag conflicts
- [x] Identify critical code changes needed

**Estimated Time:** 5 hours ✅ COMPLETE

---

## Phase 2: Code Preparation

### 2.1 Set Up Development Environment
- [ ] Ensure azdev is installed and configured
- [ ] Run `azdev setup -c` to configure development environment
- [ ] Verify can run `az` commands from development environment
- [ ] Test running existing ACS commands

**Note:** POC approach - keeping existing output format to prove feasibility first. Output formatting refinement will be addressed after POC is working.

### 2.2 Clone aks-net-diagnostics
- [x] Clone aks-net-diagnostics repository locally
- [x] Checkout `azure-sdk` branch
- [ ] Review `azure_sdk_client.py` implementation
- [ ] Review all analyzer modules
- [x] Document external dependencies

**Dependencies Analysis:**
- ✅ `azure-mgmt-containerservice>=29.0.0` - Already in CLI (v40.0.0)
- ❌ `azure-mgmt-network>=25.0.0` - **NOT in CLI** - Need to add to ACS module requirements
- ✅ `azure-mgmt-compute>=30.0.0` - Already in CLI (v34.1.0)
- ✅ `azure-mgmt-privatedns>=1.1.0` - Already in CLI (v1.0.0 - may need update)
- ✅ `azure-mgmt-resource>=23.0.0` - Already in CLI (v23.3.0)
- ❓ `azure-identity>=1.15.0` - Not found, but CLI uses own auth system

**Action Required:** Add `azure-mgmt-network` to Azure CLI dependencies

**Estimated Time:** 1 hour

### 2.3 Adapt Azure SDK Client for CLI Authentication
**Priority: HIGH - Critical for integration**

The azure-sdk branch has `azure_sdk_client.py` that uses Azure SDK with `DefaultAzureCredential`.
We need to adapt it to use CLI's authentication via `cmd.cli_ctx`.

- [ ] Create `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/` directory
- [ ] Copy `azure_sdk_client.py` → `net_diagnostics/sdk_client.py`
- [ ] Replace `DefaultAzureCredential()` with CLI's `cmd.cli_ctx`
- [ ] Update `__init__(self, subscription_id)` → `__init__(self, cmd)`
- [ ] Replace `.aks_client` property to use `cf_container_services(cmd.cli_ctx)`
- [ ] Replace `.network_client` property to use `get_mgmt_service_client()`
- [ ] Replace `.compute_client` property to use `get_mgmt_service_client()`
- [ ] Replace `.privatedns_client` property to use `get_mgmt_service_client()`
- [ ] Update `get_cluster()` method to use new client initialization
- [ ] Keep `parse_resource_id()` utility method as-is
- [ ] Add type hints and docstrings
- [ ] Test basic functionality

**Estimated Time:** 3-4 hours

---

## Phase 3: Integration Implementation

### 3.1 Copy and Adapt Modules

#### Core Modules
- [ ] Copy `aks_diagnostics/__init__.py` → `net_diagnostics/__init__.py`
- [ ] Copy `aks_diagnostics/models.py` → `net_diagnostics/models.py`
- [ ] Copy `aks_diagnostics/exceptions.py` → `net_diagnostics/exceptions.py`
- [ ] Copy `aks_diagnostics/validators.py` → `net_diagnostics/validators.py`
- [ ] Update imports in validators.py

#### Analyzers Directory
- [ ] Create `net_diagnostics/analyzers/__init__.py`
- [ ] Copy `base_analyzer.py` → `analyzers/base_analyzer.py`
  - [ ] Update imports
  - [ ] Update constructor to accept SDKClient instead of AzureSDKClient
- [ ] Copy `nsg_analyzer.py` → `analyzers/nsg_analyzer.py`
  - [ ] Update imports
  - [ ] Verify works with adapted SDK client
- [ ] Copy `dns_analyzer.py` → `analyzers/dns_analyzer.py`
  - [ ] Update imports only
- [ ] Copy `route_table_analyzer.py` → `analyzers/route_table_analyzer.py`
  - [ ] Update imports only
- [ ] Copy `api_server_analyzer.py` → `analyzers/api_server_analyzer.py`
  - [ ] Update imports only
- [ ] Copy `connectivity_tester.py` → `analyzers/connectivity_tester.py`
  - [ ] Update imports
  - [ ] Verify VMSS run-command works with CLI SDK client
- [ ] Copy `outbound_analyzer.py` → `analyzers/outbound_analyzer.py`
  - [ ] Update imports only
- [ ] Copy `misconfiguration_analyzer.py` → `analyzers/misconfiguration_analyzer.py`
  - [ ] Update imports only

**Estimated Time:** 3-4 hours

#### Collectors Directory
- [ ] Create `net_diagnostics/collectors/__init__.py`
- [ ] Copy `cluster_data_collector.py` → `collectors/cluster_data_collector.py`
  - [ ] Update imports
  - [ ] Update to use adapted SDK client

**Estimated Time:** 1 hour

#### Reporting
- [ ] Copy `report_generator.py` → `net_diagnostics/report_generator.py`
  - [ ] Update imports
  - [ ] Adapt output formatting for CLI if needed

#### Main Orchestrator
- [ ] Create `net_diagnostics/orchestrator.py` (adapted from `aks-net-diagnostics.py`)
  - [ ] Remove `parse_arguments()` method
  - [ ] Update `__init__()` to accept cmd and parameters (not parse them)
  - [ ] Replace `AzureSDKClient` initialization with adapted `SDKClient`
  - [ ] Keep all analysis methods unchanged
  - [ ] Update imports throughout

**Estimated Time:** 2-3 hours

### 3.2 Register Command in Azure CLI

#### Update commands.py
- [ ] Open `src/azure-cli/azure/cli/command_modules/acs/commands.py`
- [ ] Add import for net-diagnostics function
- [ ] Register 'net-diagnostics' command in command group
- [ ] Verify command loads without errors

#### Update _params.py
- [ ] Open `src/azure-cli/azure/cli/command_modules/acs/_params.py`
- [ ] Add argument context for 'aks net-diagnostics'
- [ ] Define `name` parameter (cluster name)
- [ ] Define `resource_group_name` parameter
- [ ] Define `details` flag
- [ ] Define `probe_test` flag
- [ ] Define `json_report` parameter
- [ ] Add help text for all parameters

#### Create Command Function
- [ ] Decide where to put command function (custom.py or new file)
- [ ] Create `aks_net_diagnostics()` function
- [ ] Accept cmd, name, resource_group_name, and optional parameters
- [ ] Create NetDiagnosticsOrchestrator instance
- [ ] Call orchestrator.run()
- [ ] Return results
- [ ] Add proper docstring

### 3.3 Handle Output Formatting
- [ ] Review Azure CLI output expectations
- [ ] Ensure console output works with CLI's output system
- [ ] Ensure JSON output works correctly
- [ ] Handle `--output json/table/tsv/yaml` formats if needed
- [ ] Test with different output modes

---

## Phase 4: Testing & Validation

### 4.1 Unit Tests
- [ ] Create `src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_aks_net_diagnostics.py`
- [ ] Write test: basic command execution
- [ ] Write test: with --details flag
- [ ] Write test: with --probe-test flag
- [ ] Write test: with --json-report flag
- [ ] Write test: error handling (cluster not found)
- [ ] Write test: error handling (no permissions)
- [ ] Mock Azure SDK calls appropriately
- [ ] Run tests: `azdev test acs --test test_aks_net_diagnostics`

### 4.2 Integration Tests
- [ ] Create test AKS cluster in test subscription
- [ ] Test: `az aks net-diagnostics -n testcluster -g testrg`
- [ ] Test: `az aks net-diagnostics -n testcluster -g testrg --details`
- [ ] Test: `az aks net-diagnostics -n testcluster -g testrg --probe-test`
- [ ] Test: `az aks net-diagnostics -n testcluster -g testrg --json-report`
- [ ] Test: `az aks net-diagnostics -n testcluster -g testrg --json-report custom.json`
- [ ] Test: with different output formats (`--output json`, `--output table`)
- [ ] Verify output matches standalone tool output
- [ ] Delete test cluster

### 4.3 Comparison Testing
- [ ] Run standalone tool on production cluster: `python aks-net-diagnostics.py -n prod -g rg`
- [ ] Run CLI command on same cluster: `az aks net-diagnostics -n prod -g rg`
- [ ] Compare findings (should be identical or very similar)
- [ ] Document any differences and reasons
- [ ] Verify both tools detect same issues

### 4.4 Edge Case Testing
- [ ] Test with private cluster
- [ ] Test with cluster in failed state
- [ ] Test with cluster behind firewall/NVA
- [ ] Test with custom DNS
- [ ] Test with multiple node pools
- [ ] Test with different auth scenarios (service principal, managed identity)
- [ ] Test with different subscription contexts

### 4.5 Performance Testing
- [ ] Measure execution time for typical cluster
- [ ] Compare with standalone tool performance
- [ ] Profile if significantly slower
- [ ] Optimize bottlenecks if found

---

## Phase 5: Documentation & Polish

### 5.1 Help Text
- [ ] Add help text to command in `_help.py`
- [ ] Add examples section
- [ ] Add description of what the command does
- [ ] Document all parameters
- [ ] Add warnings for --probe-test flag

### 5.2 Code Quality
- [ ] Run pylint: `azdev style acs`
- [ ] Fix all pylint issues
- [ ] Run linter: `azdev linter acs`
- [ ] Fix all linter issues
- [ ] Ensure code follows Azure CLI style guidelines
- [ ] Add type hints where missing
- [ ] Add docstrings where missing

### 5.3 Documentation Files
- [ ] Update ACS module README if it exists
- [ ] Create or update documentation for net-diagnostics subcommand
- [ ] Add to Azure CLI command reference (if applicable)
- [ ] Document differences from standalone tool (if any)

### 5.4 Examples
- [ ] Add example to help text: basic usage
- [ ] Add example to help text: with details
- [ ] Add example to help text: with probe-test
- [ ] Add example to help text: with json-report
- [ ] Create example outputs in documentation

---

## Phase 6: Review & Merge

### 6.1 Pre-PR Checklist
- [ ] All tests pass: `azdev test acs`
- [ ] Style checks pass: `azdev style acs`
- [ ] Linter passes: `azdev linter acs`
- [ ] Manual testing completed
- [ ] Documentation complete
- [ ] No TODO or FIXME comments in code
- [ ] Version updated if needed
- [ ] HISTORY.rst updated with change

### 6.2 Create Pull Request
- [ ] Create PR branch based on latest `dev`
- [ ] Format PR title following guidelines: `[ACS] Add net-diagnostics subcommand`
- [ ] Fill out PR description template
- [ ] Link to any related issues
- [ ] Add testing instructions for reviewers
- [ ] Request reviews from ACS module owners

### 6.3 Address Review Feedback
- [ ] Respond to all review comments
- [ ] Make requested changes
- [ ] Re-run tests after changes
- [ ] Update documentation if needed
- [ ] Request re-review

### 6.4 Post-Merge
- [ ] Verify command in next Azure CLI release
- [ ] Monitor for issues/bugs reported
- [ ] Create follow-up issues for any enhancements
- [ ] Update standalone tool documentation to mention CLI integration

---

## Quick Reference: Key Files to Modify

### New Files to Create
1. `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/` (entire directory)
2. `src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_aks_net_diagnostics.py`

### Existing Files to Modify
1. `src/azure-cli/azure/cli/command_modules/acs/commands.py` - Register command
2. `src/azure-cli/azure/cli/command_modules/acs/_params.py` - Define parameters
3. `src/azure-cli/azure/cli/command_modules/acs/custom.py` - Add command function (or create new file)
4. `src/azure-cli/azure/cli/command_modules/acs/_help.py` - Add help text

---

## Estimated Timeline

| Phase | Estimated Time | Priority | Notes |
|-------|----------------|----------|-------|
| Phase 1: Planning | 5 hours | ✅ Complete | Documentation and analysis |
| Phase 2: Code Preparation | 4-5 hours | 🔴 Critical | Adapt authentication |
| Phase 3: Integration | 8-12 hours | 🔴 Critical | Copy modules & update imports |
| Phase 4: Testing | 8-12 hours | 🟡 High | Comprehensive testing |
| Phase 5: Documentation | 4-6 hours | 🟢 Medium | Help text and examples |
| Phase 6: Review & Merge | 4-8 hours | 🟢 Medium | PR and review process |
| **TOTAL** | **33-48 hours** | | |

---

## Current Status

**Last Updated:** October 19, 2025  
**Current Phase:** Phase 2 (Code Preparation) - Ready to begin  
**Next Action:** Clone aks-net-diagnostics azure-sdk branch and set up development environment

**Blockers:** None

**Questions:** See `05-questions-and-decisions.md`
