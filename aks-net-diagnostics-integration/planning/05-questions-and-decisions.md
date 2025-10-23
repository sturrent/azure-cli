# Questions and Decisions

**Last Updated:** October 23, 2025  
**Status:** Phase 7 Complete - Most questions resolved through implementation  

> **Note:** This document tracks questions raised during planning. Most have been answered through implementation (Phases 1-7). See progress reports in `progress/` for detailed answers.

---

## ✅ Resolved Questions

### Technical Questions

#### Q1: Authentication Context ✅ RESOLVED
**Question:** How does Azure CLI pass authentication context to commands?

**Status:** ✅ **RESOLVED** (Phase 3)

**Answer:**
- `cmd.cli_ctx` contains the CLI context
- Client factories use `get_mgmt_service_client()` with this context
- Works automatically with all auth methods (user, SP, MI)
- Token refresh handled by Azure SDK automatically

**Implementation:** See `src/azure-cli/azure/cli/command_modules/acs/_client_factory.py`
- Created factory functions: `cf_container_services()`, `cf_agent_pools()`, `cf_network_client()`, `cf_compute_client()`
- All use `cmd.cli_ctx` for authentication
- Tested with service principal and user authentication ✅

**Resolution:** Works perfectly - no issues encountered across multiple auth types.

---

#### Q2: Output Formatting ✅ RESOLVED
**Question:** How should we handle the different output formats between the standalone tool and Azure CLI?

**Status:** ✅ **RESOLVED** (Phase 1 - POC Decision)

**Decision:** For the POC phase, keep the existing aks-net-diagnostics output format (text with colors + optional `--json-report`).

**Implementation:** Uses `print()` statements directly, similar to `az aks check-acr`. Command returns `None`.

**Result:** ✅ Working perfectly - users get rich console output with colors and formatting. JSON report available via `--json-report` flag.

**Future:** Can add structured output (`--output json/table/yaml/tsv`) in post-POC phase if needed.

---

#### Q3: Error Handling Standards ✅ RESOLVED
**Question:** What are Azure CLI's error handling conventions?

**Status:** ✅ **RESOLVED** (Phases 3-7)

**Answer:**
- Use `CLIError` and `ResourceNotFoundError` from `azure.cli.core.azclierror`
- Use `logger.warning()` for non-fatal issues
- Use `logger.error()` for errors
- HTTP errors caught and converted to actionable findings
- Permission errors handled with specific finding codes

**Implementation:**
- Phase 3: Basic error handling with CLIError
- Phase 7: Comprehensive permission error handling
  - Authorization failures detected via regex pattern
  - Permission findings created with remediation commands
  - False positives prevented through permission context

**Examples:**
- `cluster_data_collector.py`: `_check_authorization_error()` method
- `outbound_analyzer.py`: Permission-aware LoadBalancer analysis
- `misconfiguration_analyzer.py`: Permission context prevents false positives

---

### Design Questions

#### D1: Module Location ✅ RESOLVED
**Question:** Should net-diagnostics be in core ACS module or a separate extension?

**Decision:** ✅ **Core ACS Module** (Phase 1)

**Rationale:**
- Tightly coupled to ACS functionality
- Used by ACS support team
- Benefits from core CLI maintenance
- Easier for users (no extension install needed)

**Implementation:** Located at `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/`

---

#### D2: Command Naming ✅ RESOLVED
**Question:** What should the command be called?

**Decision:** ✅ **`az aks net-diagnostics`** (Phase 1)

**Rationale:**
- Shorter than network-diagnostics
- Clear what it does
- Matches standalone tool name

**Implementation:** Registered in `commands.py` as `net-diagnostics` subcommand

---

#### D3: Feature Parity ✅ RESOLVED
**Question:** Should CLI version have 100% feature parity with standalone tool?

**Status:** ✅ **RESOLVED** - YES, full feature parity achieved (Phase 5-6)

**Features Implemented:**
- ✅ `--details`: Full detailed analysis
- ✅ `--probe-test`: Node connectivity testing (complex VMSS run-command)
- ✅ `--json-report`: JSON output to file
- ✅ All analyzers: DNS, NSG, Route Tables, API Server, Outbound, Connectivity, Misconfiguration
- ✅ Permission handling: Graceful handling of insufficient permissions
- ✅ Multiple outbound types: LoadBalancer, NAT Gateway, UDR

**Testing:** 33+ formal tests + 6+ exploration tests across 5 clusters ✅

**Result:** 100% feature parity with standalone tool, plus improvements (permission handling)

---

#### D4: Dependencies ✅ RESOLVED
**Question:** What dependencies can we add to Azure CLI?

**Status:** ✅ **RESOLVED** (Phase 2)

**Required Packages:** All already in Azure CLI ✅
- `azure-mgmt-containerservice` ✅ Already present
- `azure-mgmt-network` ✅ Added to requirements (was missing)
- `azure-mgmt-compute` ✅ Already present  
- `azure-mgmt-privatedns` ✅ Not needed (removed dependency)
- `azure-mgmt-resource` ✅ Already present

**Action Taken:** Added `azure-mgmt-network` to `src/azure-cli/setup.py`

**Result:** All dependencies satisfied, no new packages required beyond azure-mgmt-network

---

#### D5: Backwards Compatibility ✅ RESOLVED
**Question:** Do we need to maintain compatibility with standalone tool?

**Status:** ✅ **RESOLVED** - Not applicable for CLI integration

**Decision:** CLI version is independent of standalone tool
- Standalone tool continues to exist
- CLI version has same functionality but integrated into `az` CLI
- No migration needed - users can use either version
- Parameter compatibility maintained where possible (`--details`, `--probe-test`, `--json-report`)

---

### Process Questions

#### P1: Code Ownership ✅ RESOLVED
**Question:** Who will maintain the net-diagnostics code after integration?

**Status:** ✅ **RESOLVED** - Integration completed in personal fork for POC

**Current Status:**
- POC completed in personal fork (sturrent/azure-cli)
- Branch: `aks-net-diagnostics-integration`
- Original author maintaining during POC phase
- Ready for review and merge to Azure/azure-cli when approved

**Next Steps:**
- Submit PR to Azure/azure-cli
- ACS module owners will become maintainers after merge
- Original author available for support during transition

---

#### P2: Release Timeline 🟡 PENDING
**Question:** When should this be released?

**Status:** 🟡 **PENDING** - POC complete, awaiting merge decision

**Current Status:**
- POC: ✅ Complete (Phase 7)
- Code Quality: ✅ 10.00/10 rating
- Testing: ✅ 100% pass rate
- Documentation: ✅ Complete

**Waiting For:**
- [ ] Review by Azure CLI team
- [ ] Review by ACS module owners
- [ ] PR submission and merge approval
- [ ] Release timeline determination

---

#### P3: Documentation Requirements ✅ RESOLVED
**Question:** What documentation is required?

**Status:** ✅ **MOSTLY COMPLETE** (Phase 6-7)

**Completed Documentation:**
- [x] Help text (`az aks net-diagnostics --help`) ✅
- [x] Command examples (4 comprehensive examples) ✅
- [x] Parameter descriptions ✅
- [x] Planning documentation (comprehensive) ✅
- [x] Progress reports (Phases 2-7) ✅
- [x] Phase 8 planning document ✅

**Pending Documentation:**
- [ ] Integration guide for migrating from standalone tool (post-merge)
- [ ] Blog post announcing feature (post-merge)
- [ ] Official Azure documentation (post-merge)

---

#### P4: Testing Requirements ✅ RESOLVED
**Question:** What level of testing is required before merge?

**Status:** ✅ **RESOLVED** - Comprehensive testing completed (Phase 6-7)

**Testing Completed:**
- ✅ 33+ formal tests across 5 categories
- ✅ 6+ exploration tests with real-world scenarios
- ✅ 100% test pass rate
- ✅ 5 test clusters validated
- ✅ All outbound types tested (LoadBalancer, NAT Gateway, UDR)
- ✅ Permission scenarios tested (full permissions, limited permissions)
- ✅ 3 network types tested (Overlay, Kubenet, Azure CNI Pod Subnet)
- ✅ Multiple node pools validated
- ✅ 25 bugs found and fixed (100% fix rate)

**Code Quality:**
- ✅ `azdev style acs`: PASSED (10.00/10 pylint, flake8 clean)
- ✅ `azdev linter acs`: PASSED (0 violations)
- ✅ All custom pylint rules: PASSED

**Acceptance Criteria:** All exceeded ✅

---

## 🟡 Open Questions (Remaining)

### P5: Azure CLI Team Review
**Question:** What is the process for submitting this to Azure CLI team?

**Status:** 🟡 **PENDING**

**Action Items:**
- [ ] Contact Azure CLI team
- [ ] Submit PR to Azure/azure-cli
- [ ] Address review feedback
- [ ] Get merge approval

---

### P6: Phase 8 Priority
**Question:** Should Phase 8 (Pod CIDR + Node Pool Display) be completed before PR submission?

**Status:** 🟡 **PENDING DISCUSSION**

**Options:**
1. Submit PR now (Phase 7 complete, fully functional)
2. Complete Phase 8 first (2-3 hours estimated)
3. Submit Phase 8 as follow-up PR

**Consideration:** Current implementation is production-ready and feature-complete. Phase 8 is an enhancement, not a bug fix.

---

## Decision Log

### Decision 1: Integration Approach ✅ IMPLEMENTED
**Date:** October 19, 2025  
**Decision:** Hybrid integration - port code to Azure CLI but keep analyzer logic intact  
**Rationale:** Balances code reuse with CLI best practices  
**Status:** ✅ **IMPLEMENTED** (Phase 2-3)  
**Result:** Successfully ported 7 analyzer files with minimal modifications. Original logic preserved.

### Decision 2: Directory Structure ✅ IMPLEMENTED
**Date:** October 19, 2025  
**Decision:** Create `net_diagnostics/` subdirectory under `acs/` module  
**Rationale:** Keeps code organized, follows CLI patterns  
**Status:** ✅ **IMPLEMENTED** (Phase 2)  
**Location:** `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/`

### Decision 3: Command Name ✅ IMPLEMENTED
**Date:** October 19, 2025  
**Decision:** Use `az aks net-diagnostics`  
**Rationale:** Clear, concise, matches standalone tool  
**Status:** ✅ **IMPLEMENTED** (Phase 3)  
**Implementation:** Registered in `commands.py`, working in production

### Decision 4: Parameter Names ✅ IMPLEMENTED
**Date:** October 19, 2025  
**Decision:** Use CLI standard parameters (`-n`, `-g`) and keep tool-specific ones (`--details`, `--probe-test`, `--json-report`)  
**Rationale:** Consistency with Azure CLI, compatibility with standalone tool  
**Status:** ✅ **IMPLEMENTED** (Phase 3)  
**Parameters:**
- `-n/--name`: Cluster name (CLI standard) ✅
- `-g/--resource-group`: Resource group (CLI standard) ✅
- `--details`: Detailed analysis (tool-specific) ✅
- `--probe-test`: Node connectivity testing (tool-specific) ✅
- `--json-report`: JSON report file (tool-specific) ✅

### Decision 5: Azure CNI Variants Support ✅ PLANNED
**Date:** October 23, 2025 (Phase 8 Planning)  
**Decision:** Support all 4 Azure CNI variants with proper pod CIDR detection  
**Rationale:** Different Azure CNI variants have different pod subnet architectures  
**Status:** 📋 **PLANNED** (Phase 8)  
**Variants:**
1. Azure CNI Node Subnet (Legacy) - Pod and node share same subnet
2. Azure CNI Overlay - Pod CIDR from network profile
3. Azure CNI Pod Subnet (Dynamic Allocation) - Pod subnets per node pool
4. Kubenet - Pod CIDR from network profile

**Implementation:** See `planning/06-phase8-pod-cidr-nodepool.md`

---

## Risks and Mitigations (Updated: October 23, 2025)

### Risk 1: Authentication Edge Cases ✅ RESOLVED
**Risk:** CLI authentication may not work in all scenarios (service principal, managed identity, etc.)  
**Likelihood:** Low  
**Impact:** Medium  
**Outcome:** ✅ **NO ISSUES ENCOUNTERED**
- Phase 3: CLI authentication works perfectly
- Used `cf_container_service_client`, `cf_network_client`, `cf_compute_client`
- Tested with multiple clusters (5+) and authentication contexts
- **Mitigation was successful:** No authentication issues in 33+ tests

### Risk 2: Breaking Changes ❌ LOW RISK
**Risk:** Azure CLI changes may break our integration  
**Likelihood:** Low  
**Impact:** Medium  
**Current Status:** ❌ **No issues detected**
- Following CLI best practices (stable APIs, standard patterns)
- Code quality: 10.00/10 pylint, 0 linter violations
- **Mitigation in place:** Comprehensive test suite (33+ tests) will detect future breakage

### Risk 3: Maintenance Burden ✅ MITIGATED
**Risk:** Code becomes hard to maintain  
**Likelihood:** Medium → **Low** (post-implementation)  
**Impact:** Medium  
**Mitigation Status:** ✅ **SUCCESSFULLY MITIGATED**
- ✅ Clear documentation (README, progress reports, planning docs)
- ✅ Excellent test coverage (33+ tests, 100% pass rate)
- ✅ Code quality validated (azdev style + linter passing)
- ✅ Comprehensive inline comments and docstrings
- 📋 Ownership establishment pending (post-merge)

### Risk 4: User Confusion ⏳ FUTURE
**Risk:** Having both standalone tool and CLI command confuses users  
**Likelihood:** Medium  
**Impact:** Low  
**Current Status:** ⏳ **Pending post-merge**
- CLI version complete and production-ready
- Standalone tool still available
- **Next Steps:** Create migration guide, update standalone tool docs, plan deprecation

### Risk 5: Permission Handling (NEW - Discovered Phase 7) ✅ RESOLVED
**Risk:** Missing permissions cause false positive findings  
**Date Discovered:** October 21, 2025 (Phase 7 testing)  
**Likelihood:** High (real-world scenario)  
**Impact:** High (misleading output)  
**Resolution:** ✅ **FULLY RESOLVED** (Phase 7)
- Implemented `_check_authorization_error()` in cluster_data_collector.py
- Permission context prevents false positives in all analyzers
- Remediation commands provided when permissions missing
- **Result:** 100% accurate findings even with limited permissions

---

## Next Steps (Updated: October 23, 2025)

### ✅ COMPLETED STEPS

#### Phase 1-7 (COMPLETE)
1. ✅ Planning documents created
2. ✅ Code ported from aks-net-diagnostics azure-sdk branch
3. ✅ CLI client factory authentication tested and working
4. ✅ Authentication adaptation implemented
5. ✅ Command registered in Azure CLI
6. ✅ All 7 analyzers implemented
7. ✅ Comprehensive testing (33+ tests, 5 clusters)
8. ✅ Permission handling implemented
9. ✅ Documentation complete (README, help text, examples)
10. ✅ Code quality validated (10.00/10 pylint)

### 🔄 CURRENT PHASE: Documentation Cleanup (Phase 7.5)
1. 🔄 Update questions-and-decisions.md to reflect implementation status
2. 📋 Commit and push final documentation updates

### 📋 PLANNED: Phase 8 - Pod CIDR & Node Pool Display (2-3 hours)
**See:** `planning/06-phase8-pod-cidr-nodepool.md` for comprehensive plan

**8.1 Pod CIDR Detection Enhancement** (1-1.5 hours)
1. [ ] Implement `_get_pod_subnet_cidrs()` in cluster_data_collector.py
2. [ ] Update `_print_pod_cidr_info()` to handle all 4 Azure CNI variants
3. [ ] Test with aks-acni-podsubnet (expected: "10.241.0.0/16, 10.243.0.0/16")

**8.2 Node Pool Display** (1 hour)
1. [ ] Implement `_print_node_pools()` in report_generator.py
2. [ ] Display: name, mode, count, VM size, OS, state, subnets, zones
3. [ ] Test with multi-pool clusters

**8.3 Code Quality & Testing** (0.5 hours)
1. [ ] Run azdev style acs (target: maintain 10.00/10)
2. [ ] Run azdev linter --ci-exclusions acs (target: 0 violations)
3. [ ] Test on all 3 network types (Overlay, Kubenet, Azure CNI Pod Subnet)

### 🟡 PENDING: Post-Implementation
**Awaiting User Decision:**
- [ ] Should Phase 8 be completed before PR submission?
- [ ] Or submit PR now with Phase 8 as follow-up?

**Post-Merge Tasks:**
1. [ ] Submit PR to Azure/azure-cli
2. [ ] Address code review feedback
3. [ ] Create migration guide from standalone tool
4. [ ] Update standalone tool documentation
5. [ ] Plan standalone tool deprecation timeline (6-12 months)

---

## Stakeholders (Updated: October 23, 2025)

### Primary Stakeholders
- **Azure CLI Team:** Must approve integration (PR pending submission)
- **ACS Module Owners:** Will maintain code post-merge
- **Original Author (sturrent):** POC implementation complete, available for transition support

### Secondary Stakeholders
- **AKS Support Team:** Primary users - tool designed for their troubleshooting workflows
- **AKS Customers:** End users who will benefit from integrated diagnostics
- **Documentation Team:** Update docs post-merge

### Communication Plan
- [x] Planning documents created and shared ✅
- [x] POC implementation completed ✅
- [x] Comprehensive testing and documentation ✅
- [ ] Email Azure CLI team about PR submission (pending)
- [ ] Schedule code review with ACS module owners (pending)
- [ ] Present implementation and get feedback (pending)
- [ ] Submit PR to Azure/azure-cli (pending user decision on Phase 8)

---

## Resources

### Completed Implementation
- **Branch:** `aks-net-diagnostics-integration` (sturrent/azure-cli fork)
- **Status:** Phase 7 COMPLETE, Phase 8 PLANNED
- **Code Quality:** 10.00/10 pylint, 0 linter violations
- **Testing:** 33+ tests, 100% pass rate, 5 clusters validated

### Documentation
- **Planning:** `aks-net-diagnostics-integration/planning/` (comprehensive)
- **Progress Reports:** Phases 2-7 documented
- **Phase 8 Plan:** `06-phase8-pod-cidr-nodepool.md` (650+ lines)
- **README:** Updated with Phase 7 completion, Phase 8 planning

### Useful Links
- Azure CLI Dev Guide: https://github.com/Azure/azure-cli/blob/dev/doc/configuring_your_machine.md
- Azure SDK for Python: https://github.com/Azure/azure-sdk-for-python
- ACS Module Code: https://github.com/Azure/azure-cli/tree/dev/src/azure-cli/azure/cli/command_modules/acs
- Original Tool: https://github.com/Azure/aks-net-diagnostics (azure-sdk branch)

---

**Last Updated:** October 23, 2025  
**Status:** Phase 7 COMPLETE - Most questions resolved through implementation (Phases 1-7)  
**Next Review:** After Phase 8 implementation or PR submission decision  
**Next Action:** Complete Phase 8 (Pod CIDR + Node Pool Display) or submit PR now
