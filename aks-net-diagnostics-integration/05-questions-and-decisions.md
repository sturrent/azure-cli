# Questions and Decisions

## Open Questions

### Technical Questions

#### Q1: Authentication Context
**Question:** How does Azure CLI pass authentication context to commands?

**Status:** 🟡 **PARTIALLY UNDERSTOOD**

**What We Know:**
- `cmd.cli_ctx` contains the CLI context
- Client factories use this context for authentication
- Should work automatically

**What We Need to Verify:**
- Does it work with all auth methods (user, SP, MI)?
- How to handle subscription switching?
- What happens with expired tokens?

**Action Items:**
- [ ] Test with different authentication methods
- [ ] Review client factory implementation
- [ ] Test token refresh scenarios

---

#### Q2: Output Formatting
**Question:** Should output be formatted differently for CLI vs standalone tool?

**Context:** Azure CLI has specific output formats (json, table, yaml, tsv). Our tool currently has its own output format.

**Status:** 🟡 **NEEDS DECISION**

**Options:**
1. Keep existing output format, ignore CLI output modes
2. Adapt output to work with CLI's `--output` parameter
3. Hybrid: custom format by default, support CLI modes

**Considerations:**
- User experience consistency
- Azure CLI conventions
- Backwards compatibility with standalone tool

**Action Items:**
- [ ] Review Azure CLI output expectations
- [ ] Check how other diagnostic commands handle output
- [ ] Decide on approach

---

#### Q3: Error Handling Standards
**Question:** What are Azure CLI's error handling conventions?

**Status:** 🟡 **NEEDS RESEARCH**

**Questions:**
- What exceptions should we raise?
- How to format error messages?
- What exit codes to use?
- How to handle partial failures?

**Action Items:**
- [ ] Review Azure CLI error handling documentation
- [ ] Look at other ACS commands for examples
- [ ] Document error handling patterns to follow

---

### Design Questions

#### D1: Module Location
**Question:** Should net-diagnostics be in core ACS module or a separate extension?

**Decision:** ✅ **DECIDED - Core ACS Module**

**Rationale:**
- Tightly coupled to ACS functionality
- Used by ACS support team
- Benefits from core CLI maintenance
- Easier for users (no extension install needed)

---

#### D2: Command Naming
**Question:** What should the command be called?

**Options:**
1. `az aks net-diagnostics` (current choice)
2. `az aks network-diagnostics`
3. `az aks diagnose-network`
4. `az aks troubleshoot-network`

**Decision:** ✅ **DECIDED - `az aks net-diagnostics`**

**Rationale:**
- Shorter than network-diagnostics
- Clear what it does
- Matches standalone tool name

---

#### D3: Feature Parity
**Question:** Should CLI version have 100% feature parity with standalone tool?

**Status:** 🟡 **NEEDS DISCUSSION**

**Considerations:**
- Some features may be harder to implement in CLI
- Some features may not fit CLI patterns
- Do we need all features in v1?

**Features to Discuss:**
- `--probe-test`: Complex, long-running, executes code on nodes
- `--json-report`: Works fine, but CLI has `--output json`
- `--details`: Works fine
- Auto-generated report filenames: Works but may conflict with CLI patterns

**Proposal:**
- **v1:** Basic analysis + --details (no --probe-test)
- **v2:** Add --probe-test after testing
- **Always:** Support --json-report for compatibility

---

#### D4: Dependencies
**Question:** What dependencies can we add to Azure CLI?

**Context:** aks-net-diagnostics requires specific Azure SDK packages. Azure CLI already includes many, but not all.

**Status:** 🟡 **NEEDS VERIFICATION**

**Required Packages:**
- `azure-mgmt-containerservice` - ✅ Likely already in CLI
- `azure-mgmt-network` - ✅ Likely already in CLI
- `azure-mgmt-compute` - ✅ Likely already in CLI
- `azure-mgmt-privatedns` - ❓ May need to add
- `azure-mgmt-resource` - ✅ Likely already in CLI

**Action Items:**
- [ ] Check Azure CLI's requirements.txt
- [ ] Identify any missing packages
- [ ] Verify package versions are compatible
- [ ] Confirm no new dependencies are prohibited

---

#### D5: Backwards Compatibility
**Question:** Do we need to maintain compatibility with standalone tool?

**Status:** 🟡 **NEEDS DISCUSSION**

**Scenarios:**
1. User scripts calling standalone tool
2. CI/CD pipelines
3. Documentation and examples

**Proposal:**
- Keep standalone tool available
- Document migration path
- Add note in standalone tool about CLI version
- Eventually deprecate standalone tool (6-12 months)

---

### Process Questions

#### P1: Code Ownership
**Question:** Who will maintain the net-diagnostics code after integration?

**Status:** 🔴 **NEEDS DECISION**

**Options:**
1. ACS module owners take over
2. Original author remains maintainer
3. Shared ownership

**Action Items:**
- [ ] Discuss with ACS module owners
- [ ] Document ownership in CODEOWNERS file
- [ ] Establish maintenance plan

---

#### P2: Release Timeline
**Question:** When should this be released?

**Status:** 🔴 **NEEDS DECISION**

**Considerations:**
- Azure CLI release cycle
- Testing requirements
- Feature completeness

**Questions:**
- Target Azure CLI version?
- Beta/preview first?
- Phased rollout?

---

#### P3: Documentation Requirements
**Question:** What documentation is required?

**Status:** 🟡 **NEEDS PLANNING**

**Required Documentation:**
- [ ] Help text (`az aks net-diagnostics --help`)
- [ ] Command examples
- [ ] Integration guide for migrating from standalone tool
- [ ] Troubleshooting guide
- [ ] Internal documentation for maintainers

**Optional Documentation:**
- [ ] Blog post announcing feature
- [ ] Video walkthrough
- [ ] Architecture documentation

---

#### P4: Testing Requirements
**Question:** What level of testing is required before merge?

**Status:** 🟡 **NEEDS CLARIFICATION**

**Questions:**
- Unit test coverage requirement? (80%? 90%?)
- Integration tests mandatory?
- Performance benchmarks required?
- Must test on production clusters?

**Action Items:**
- [ ] Review Azure CLI testing standards
- [ ] Define acceptance criteria
- [ ] Document testing checklist

---

## Decision Log

### Decision 1: Integration Approach
**Date:** October 19, 2025  
**Decision:** Hybrid integration - port code to Azure CLI but keep analyzer logic intact  
**Rationale:** Balances code reuse with CLI best practices  
**Status:** ✅ Approved  

### Decision 2: Directory Structure
**Date:** October 19, 2025  
**Decision:** Create `net_diagnostics/` subdirectory under `acs/` module  
**Rationale:** Keeps code organized, follows CLI patterns  
**Status:** ✅ Approved  

### Decision 3: Command Name
**Date:** October 19, 2025  
**Decision:** Use `az aks net-diagnostics`  
**Rationale:** Clear, concise, matches standalone tool  
**Status:** ✅ Approved  

### Decision 4: Parameter Names
**Date:** October 19, 2025  
**Decision:** Use CLI standard parameters (`-n`, `-g`) and keep tool-specific ones (`--details`, `--probe-test`, `--json-report`)  
**Rationale:** Consistency with Azure CLI, compatibility with standalone tool  
**Status:** ✅ Approved  

---

## Risks and Mitigations

### Risk 1: Authentication Edge Cases
**Risk:** CLI authentication may not work in all scenarios (service principal, managed identity, etc.)  
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:** 
- Test with different authentication methods early
- Review CLI's client factory implementation
- Add comprehensive authentication tests

### Risk 2: Breaking Changes
**Risk:** Azure CLI changes may break our integration  
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Follow CLI best practices
- Use stable APIs
- Add tests to detect breakage

### Risk 3: Maintenance Burden
**Risk:** Code becomes hard to maintain  
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Clear documentation
- Good test coverage
- Establish ownership early

### Risk 4: User Confusion
**Risk:** Having both standalone tool and CLI command confuses users  
**Likelihood:** Medium  
**Impact:** Low  
**Mitigation:**
- Clear migration guide
- Update standalone tool documentation
- Eventually deprecate standalone tool

---

## Next Steps

### Immediate (This Week)
1. ✅ Complete planning documents
2. [ ] Clone aks-net-diagnostics azure-sdk branch
3. [ ] Test CLI client factory authentication
4. [ ] Prototype authentication adaptation

### Short Term (Next 2 Weeks)
1. [ ] Complete code adaptation
2. [ ] Register command in Azure CLI
3. [ ] Basic testing

### Medium Term (1 Month)
1. [ ] Comprehensive testing
2. [ ] Documentation
3. [ ] Code review
4. [ ] Submit PR

### Long Term (2-3 Months)
1. [ ] Address PR feedback
2. [ ] Release with Azure CLI
3. [ ] Monitor for issues
4. [ ] Plan standalone tool deprecation

---

## Stakeholders

### Primary Stakeholders
- **Azure CLI Team:** Must approve integration
- **ACS Module Owners:** Will maintain code
- **Original Author:** Knows code best

### Secondary Stakeholders
- **AKS Support Team:** Primary users
- **AKS Customers:** End users
- **Documentation Team:** Update docs

### Communication Plan
- [ ] Email Azure CLI team about proposal
- [ ] Schedule meeting with ACS module owners
- [ ] Present plan and get feedback
- [ ] Update plan based on feedback
- [ ] Get formal approval before starting implementation

---

## Resources

### People to Contact
- **Azure CLI Team:** [contact info needed]
- **ACS Module Owners:** [contact info needed]
- **Code Reviewers:** [contact info needed]

### Useful Links
- Azure CLI Dev Guide: https://github.com/Azure/azure-cli/blob/dev/doc/configuring_your_machine.md
- Azure SDK for Python: https://github.com/Azure/azure-sdk-for-python
- ACS Module Code: https://github.com/Azure/azure-cli/tree/dev/src/azure-cli/azure/cli/command_modules/acs

---

**Last Updated:** October 19, 2025  
**Status:** Planning Phase  
**Next Review:** After completing Phase 2 (Code Preparation)
