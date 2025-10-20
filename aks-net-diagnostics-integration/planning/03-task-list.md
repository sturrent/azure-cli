# Task List

## High-Level Phases

- [x] **Phase 1:** Planning & Analysis ✅ COMPLETE
- [x] **Phase 2:** Development Environment Setup ✅ COMPLETE
- [x] **Phase 3:** Authentication Adapter ✅ COMPLETE
- [ ] **Phase 4:** Copy Diagnostic Modules ⏳ (Current)
- [ ] **Phase 5:** Register Command
- [ ] **Phase 6:** Define Parameters
- [ ] **Phase 7:** Integration Testing
- [ ] **Phase 8:** Documentation & Polish

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

## Phase 2: Development Environment Setup ✅ COMPLETE

### 2.1 Set Up Development Environment ✅
- [x] Create Python virtual environment (.venv)
- [x] Install azdev (v0.2.7)
- [x] Run `azdev setup -c .` to configure development environment (57 seconds)
- [x] Verify can run `az` commands from development environment (v2.78.0)
- [x] Create workspace directory structure
- [x] Add .venv/ to .gitignore

**Status:** ✅ Complete - Environment fully functional

### 2.2 Clone aks-net-diagnostics ✅
- [x] Clone aks-net-diagnostics repository locally
- [x] Checkout `azure-sdk` branch
- [x] Verify repository structure (16 modules in aks_diagnostics/)
- [x] Document external dependencies
- [x] Analyze dependency compatibility with Azure CLI

**Dependencies Analysis:**
- ✅ `azure-mgmt-containerservice>=29.0.0` - Already in CLI (v40.0.0)
- ❌ `azure-mgmt-network>=25.0.0` - **NOT in CLI** - Need to add to ACS module requirements
- ✅ `azure-mgmt-compute>=30.0.0` - Already in CLI (v34.1.0)
- ⚠️ `azure-mgmt-privatedns>=1.1.0` - Already in CLI (v1.0.0 - may need update)
- ✅ `azure-mgmt-resource>=23.0.0` - Already in CLI (v23.3.0)
- ℹ️ `azure-identity>=1.15.0` - Not needed, CLI uses own auth system

**Key Finding:** azure-mgmt-network package is missing from Azure CLI but required by 4 analyzer modules (nsg_analyzer, route_table_analyzer, outbound_analyzer, dns_analyzer).

**Action Required:** Add `azure-mgmt-network>=25.0.0` to ACS module setup.py

### 2.3 Documentation ✅
- [x] Create DEVELOPMENT-SETUP.md (comprehensive 300+ line setup guide)
- [x] Create PHASE2-PROGRESS.md (detailed progress report)
- [x] Update task list with dependency findings
- [x] Organize documentation into logical structure:
  - planning/ - Strategy documents
  - research/ - Technical research
  - progress/ - Phase reports
  - guides/ - How-to guides

### 2.4 Add Missing Dependency ✅
- [x] Identified azure-mgmt-network as missing
- [x] Added `azure-mgmt-network~=25.0.0` to `src/azure-cli/setup.py`
- [x] Reinstalled Azure CLI: `pip install -e src/azure-cli/`
- [x] Verified installation: `python -c "import azure.mgmt.network"`
- [x] Confirmed version: azure-mgmt-network 25.0.0
- [x] Updated .gitignore with .venv entry

**Status:** ✅ Complete

**Time Spent:** ~20 minutes

**Note:** POC approach - keeping existing output format to prove feasibility first. Output formatting refinement will be addressed after POC is working.

---

## Phase 3: Authentication Adapter ✅ COMPLETE (100%)

### 3.1 Review Source Code ✅ COMPLETE
- [x] Review `azure_sdk_client.py` implementation in detail
- [x] Review CLI's `_client_factory.py` pattern
- [x] Review CLI's `get_mgmt_service_client()` function
- [x] Document how DefaultAzureCredential is used
- [x] Map SDK client methods to CLI patterns
- [x] **Verify ResourceType constants exist** ✅
  - ✅ `ResourceType.MGMT_CONTAINERSERVICE` - EXISTS
  - ✅ `ResourceType.MGMT_NETWORK` - EXISTS
  - ✅ `ResourceType.MGMT_COMPUTE` - EXISTS
  - ✅ `ResourceType.MGMT_NETWORK_PRIVATEDNS` - EXISTS
- [x] Create comprehensive analysis document
- [x] Decide on implementation approach: **CLI-Style Client Factories**

**Status:** ✅ Complete  
**Time Spent:** 45 minutes  
**Commit:** `13308bb8e4`  
**Documentation:**
- Created `PHASE3-AUTHENTICATION-ANALYSIS.md` (400+ lines technical deep-dive)
- Created `PHASE3-SUMMARY.md` (executive summary with implementation plan)

### 3.2a Add Client Factory Functions ✅ COMPLETE
- [x] Add `get_network_client()` to `_client_factory.py`
- [x] Add `get_privatedns_client()` to `_client_factory.py`
- [x] Follow existing Azure CLI client factory pattern
- [x] Use `get_mgmt_service_client()` for authentication
- [x] Support optional `subscription_id` parameter
- [x] Create comprehensive test suite
- [x] Verify all tests pass

**Status:** ✅ Complete  
**Time Spent:** 45 minutes (including testing)  
**Commit:** `8947250ce8`  
**Lines Changed:** 10 lines added to `_client_factory.py`  
**Testing:** All 5 test categories passed ✅

### 3.3 Create Command Handler Function ✅ COMPLETE
- [x] Create `aks_net_diagnostics()` function in `custom.py`
- [x] Accept required parameters: `cmd`, `client`, `resource_group_name`, `name`, `details`, `probe_test`, `json_report`
- [x] Use `get_network_client()` and `get_privatedns_client()` from Phase 3.2a
- [x] Retrieve cluster information using container service client
- [x] Get subscription ID from CLI context
- [x] Create Azure SDK clients with CLI authentication
- [x] Return POC output (basic cluster info)
- [x] Verify syntax and imports
- [x] Pass pre-commit hook validation

**Status:** ✅ Complete  
**Time Spent:** 30 minutes  
**Commit:** `161fe57f9f`  
**Lines Changed:** 73 lines added to `custom.py`  
**Pattern:** Follows existing AKS command patterns (e.g., `aks_check_acr`)

### 3.4 Adapt Orchestrator from aks-net-diagnostics ✅ COMPLETE
**Priority: HIGH - Critical for integration**

Copy and adapt the orchestrator to work with CLI authentication and command handler.

- [x] Create `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/` directory
- [x] Create `net_diagnostics/__init__.py`
- [x] Created `net_diagnostics/orchestrator.py` with `run_diagnostics()` function
- [x] Adapted to accept pre-created clients as parameters (from command handler)
- [x] Removed `DefaultAzureCredential` initialization (uses CLI clients)
- [x] Removed argument parsing (CLI handles this)
- [x] Implemented POC stub showing integration works
- [x] Updated `custom.py` to import and call orchestrator
- [x] Added compute_client creation in command handler
- [x] Tested basic integration - all files compile
- [x] Fixed style violations (trailing whitespace, unused imports)
- [x] Verified POC functionality works

**Status:** ✅ Complete  
**Time Spent:** 45 minutes  
**Commits:** `b601e002a0`, `78881b256f`  
**Lines Changed:** +156 lines (orchestrator.py + __init__.py)  
**Pattern:** Function-based orchestrator accepting pre-authenticated clients

### 3.5 Code Quality Improvements ✅ COMPLETE
- [x] Identified pylint warnings (reimport, variable shadowing)
- [x] Removed unnecessary `get_subscription_id` reimport
- [x] Renamed local logger to `diagnostics_logger`
- [x] Achieved perfect pylint score (10.00/10)
- [x] All style checks passed cleanly

**Status:** ✅ Complete  
**Time Spent:** 15 minutes  
**Commit:** `8d387f6495`  
**Result:** Perfect code quality, zero warnings

**Phase 3 Total Time:** ~2.5 hours  
**Phase 3 Status:** ✅ COMPLETE (100%)

---

## Phase 4: Copy Diagnostic Modules ⏳ IN PROGRESS (72% complete)

### 4.1 Copy Foundation Modules ✅ COMPLETE
- [x] Copy `__version__.py` → `_version.py`
- [x] Copy `models.py` → `models.py` (with pylint disable for too-many-instance-attributes)
- [x] Copy `exceptions.py` → `exceptions.py`
- [x] Copy `validators.py` → `validators.py`
- [x] Update `__init__.py` with proper imports
- [x] Fixed duplicate headers and import order

**Status:** ✅ Complete  
**Time Spent:** 30 minutes  
**Commit:** `7f8c791636`  
**Lines Added:** 405 lines (329 new + 76 modified)  
**Code Quality:** 10.00/10 pylint score

### 4.2 Copy Base Analyzer ✅ COMPLETE
- [x] Copy `base_analyzer.py` → `base_analyzer.py`
- [x] Adapt constructor to accept dict of clients instead of azure_sdk_client wrapper
- [x] Update docstrings for CLI context
- [x] Verify style compliance

**Status:** ✅ Complete  
**Time Spent:** 15 minutes  
**Commit:** `193775b759`  
**Lines Added:** 89 lines  
**Code Quality:** 10.00/10 pylint score

### 4.3 Copy Cluster Data Collector ✅ COMPLETE
- [x] Copy `cluster_data_collector.py` → `cluster_data_collector.py`
- [x] Remove dependency on `azure_sdk_client` wrapper
- [x] Add `_to_dict()` helper function for SDK object conversion
- [x] Update constructor to accept individual clients (aks, network, compute)
- [x] Change dict keys from camelCase to snake_case (SDK native format)
- [x] Fix flake8 whitespace warnings

**Status:** ✅ Complete  
**Time Spent:** 45 minutes  
**Commits:** `b31592577c`, `fe4458ac06`  
**Lines Added:** 306 lines  
**Code Quality:** 10.00/10 pylint, flake8 passed

### 4.4 Copy Analyzers ⏳ IN PROGRESS (4 of 7 complete - 57%)

#### 4.4a DNS Analyzer ✅ COMPLETE
- [x] Copy `dns_analyzer.py` (341 lines adapted) - Private DNS analysis
- [x] Inherits from BaseAnalyzer
- [x] Removed azure_sdk_client dependency
- [x] Uses clients dict with network_client access
- [x] Manual resource ID parsing (no parse_resource_id helper)
- [x] Changed dict keys to snake_case
- [x] Uses self.add_finding() from BaseAnalyzer

**Status:** ✅ Complete  
**Time Spent:** 30 minutes  
**Commit:** `b1fcee9c53`  
**Code Quality:** 10.00/10 pylint score

#### 4.4b Route Table Analyzer ✅ COMPLETE
- [x] Copy `route_table_analyzer.py` (407 lines adapted) - Route table analysis
- [x] Standalone analyzer (doesn't inherit from BaseAnalyzer)
- [x] Accepts agent_pools, network_client, logger directly
- [x] Manual resource ID parsing for subnets and route tables
- [x] Added _to_dict() helper function
- [x] Changed all dict keys to snake_case
- [x] Added pylint disable for too-few-public-methods (justified - single entry point)

**Status:** ✅ Complete  
**Time Spent:** 35 minutes  
**Commit:** `e40a3ddf70`  
**Code Quality:** 10.00/10 pylint score

#### 4.4c API Server Analyzer ✅ COMPLETE
- [x] Copy `api_server_analyzer.py` (464 lines adapted) - API server access
- [x] Analyzes authorized IP ranges and private cluster settings
- [x] Validates security configurations
- [x] Detects UDR overrides affecting Load Balancer outbound
- [x] Checks if cluster outbound IPs are in authorized ranges
- [x] Provides security recommendations
- [x] Optional logger parameter
- [x] Fixed line-too-long issues (split long strings)
- [x] Added pylint disable for too-few-public-methods

**Status:** ✅ Complete  
**Time Spent:** 40 minutes  
**Commit:** `d3eebda04e`  
**Code Quality:** 10.00/10 pylint score

#### 4.4d Outbound Analyzer ✅ COMPLETE
- [x] Copy `outbound_analyzer.py` (591 lines adapted) - Outbound connectivity
- [x] Analyzes Load Balancer, NAT Gateway, and UDR outbound configuration
- [x] Detects effective outbound path considering UDR overrides
- [x] Warns about conflicts between configured and effective outbound types
- [x] Integrates with RouteTableAnalyzer for comprehensive UDR analysis
- [x] Supports cross-subscription resource lookups
- [x] Added `_parse_resource_id()` and `_to_dict()` helper methods
- [x] Pylint disables for structural patterns (too-many-instance-attributes, too-many-nested-blocks)
- [x] Fixed flake8 W503 (binary operator placement)

**Status:** ✅ Complete  
**Time Spent:** 45 minutes  
**Commits:** `8cc97895fd`, `a61bb1f348`  
**Code Quality:** 10.00/10 pylint score, flake8 passed

#### 4.4e NSG Analyzer ⏳ NEXT
- [ ] Copy `nsg_analyzer.py` (510 lines) - NSG analysis

#### 4.4f Connectivity Tester
- [ ] Copy `nsg_analyzer.py` (510 lines) - NSG analysis

#### 4.4f Connectivity Tester
- [ ] Copy `connectivity_tester.py` (615 lines) - Connectivity probing

#### 4.4g Misconfiguration Analyzer
- [ ] Copy `misconfiguration_analyzer.py` (721 lines) - Misconfiguration detection

**Estimated Time:** 4-5 hours total (2-3 hours remaining)  
**Strategy:** One analyzer at a time, smallest to largest
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
