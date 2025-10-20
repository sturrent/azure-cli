# Phase 6: Integration Testing & Validation

**Status:** ⏳ IN PROGRESS  
**Started:** October 20, 2025  
**Estimated Time:** 4-6 hours  

## Testing Overview

This phase validates the `az aks net-diagnostics` command works correctly with real AKS clusters and produces accurate results compared to the standalone tool.

## Test Clusters

We have 3 clusters available for testing:

| Cluster Name | Resource Group | Notes |
|--------------|----------------|-------|
| `aks-overlay` | `aks-overlay-rg` | Overlay networking test |
| `aks-api-connection` | `aks-api-connection-lab1-rg` | API server connectivity test |
| `aks-dns-ex1` | `aks-dns-ex1-rg` | DNS configuration test |

## Testing Strategy

### 6.1 Basic Functionality Tests ⏳

**Objective:** Verify command executes successfully and produces output

- [ ] **Test 1.1:** Basic execution without flags
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg
  ```
  - Expected: Command completes, displays diagnostic summary
  - Verify: No errors, proper authentication, cluster data retrieved

- [ ] **Test 1.2:** With --details flag
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --details
  ```
  - Expected: Detailed diagnostic information displayed
  - Verify: More verbose output than basic execution

- [ ] **Test 1.3:** With --json-report flag (default path)
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --json-report
  ```
  - Expected: JSON report saved to default location
  - Verify: File created with correct permissions (0o600), valid JSON

- [ ] **Test 1.4:** With --json-report and custom path
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --json-report /tmp/custom-report.json
  ```
  - Expected: JSON report saved to specified path
  - Verify: File created at custom location, valid JSON

- [ ] **Test 1.5:** With --probe-test flag
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --probe-test
  ```
  - Expected: Active connectivity tests executed
  - Verify: VMSS command execution, test results displayed

- [ ] **Test 1.6:** All flags combined
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --details --probe-test --json-report /tmp/full-report.json
  ```
  - Expected: Complete diagnostic run with all features
  - Verify: Detailed output, connectivity tests, JSON report created

### 6.2 Cluster-Specific Tests ⏳

**Objective:** Validate diagnostics work correctly with different cluster configurations

#### Cluster 1: aks-overlay (Overlay Networking)
- [ ] **Test 2.1:** Analyze overlay networking configuration
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --details
  ```
  - Verify: Overlay network mode detected correctly
  - Verify: Network plugin settings analyzed
  - Expected findings: Overlay-specific configuration details

#### Cluster 2: aks-api-connection (API Server Connectivity)
- [ ] **Test 2.2:** Analyze API server access configuration
  ```bash
  az aks net-diagnostics -n aks-api-connection -g aks-api-connection-lab1-rg --details
  ```
  - Verify: API server endpoint detected
  - Verify: Authorized IP ranges analyzed (if configured)
  - Verify: Private cluster settings detected (if applicable)
  - Expected findings: API server access configuration details

- [ ] **Test 2.3:** Test API server connectivity
  ```bash
  az aks net-diagnostics -n aks-api-connection -g aks-api-connection-lab1-rg --probe-test
  ```
  - Verify: API server reachability test executes
  - Verify: Connection results accurate
  - Expected: API connectivity validated from VMSS

#### Cluster 3: aks-dns-ex1 (DNS Configuration)
- [ ] **Test 2.4:** Analyze DNS configuration
  ```bash
  az aks net-diagnostics -n aks-dns-ex1 -g aks-dns-ex1-rg --details
  ```
  - Verify: DNS configuration detected
  - Verify: Private DNS zones analyzed (if configured)
  - Verify: VNet links validated (if private cluster)
  - Expected findings: DNS setup details

- [ ] **Test 2.5:** Test DNS resolution
  ```bash
  az aks net-diagnostics -n aks-dns-ex1 -g aks-dns-ex1-rg --probe-test
  ```
  - Verify: DNS resolution tests execute
  - Verify: Private IP validation (if private cluster)
  - Expected: DNS resolution working correctly

### 6.3 Output Format Validation ⏳

**Objective:** Ensure output is readable and properly formatted

- [ ] **Test 3.1:** Console output formatting
  - Verify: Colors display correctly
  - Verify: Severity icons present (✅, ⚠️, ❌, ℹ️)
  - Verify: Tables formatted properly
  - Verify: Sections clearly separated

- [ ] **Test 3.2:** JSON report structure
  - Verify: Valid JSON syntax
  - Verify: All expected sections present
  - Verify: Data completeness
  - Verify: No sensitive data leaked

- [ ] **Test 3.3:** Summary vs Detailed output
  - Verify: Summary mode concise
  - Verify: Detailed mode comprehensive
  - Verify: Appropriate level of detail for each

### 6.4 Comparison with Standalone Tool ⏳

**Objective:** Verify CLI version produces same results as standalone tool

- [ ] **Test 4.1:** Compare on aks-overlay cluster
  ```bash
  # Standalone tool
  cd ~/aks-net-diagnostics
  python aks-net-diagnostics.py -n aks-overlay -g aks-overlay-rg --json-report standalone.json
  
  # CLI version
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --json-report cli.json
  
  # Compare
  diff <(jq -S . standalone.json) <(jq -S . cli.json)
  ```
  - Verify: Same findings detected
  - Verify: Same severity levels
  - Verify: Same recommendations
  - Document: Any differences and reasons

- [ ] **Test 4.2:** Compare on aks-api-connection cluster
  - Repeat comparison test
  - Document: Findings consistency

- [ ] **Test 4.3:** Compare on aks-dns-ex1 cluster
  - Repeat comparison test
  - Document: Findings consistency

### 6.5 Error Handling Tests ⏳

**Objective:** Verify proper error handling for edge cases

- [ ] **Test 5.1:** Cluster not found
  ```bash
  az aks net-diagnostics -n nonexistent-cluster -g aks-overlay-rg
  ```
  - Expected: Clear error message
  - Verify: No stack traces exposed to user

- [ ] **Test 5.2:** Resource group not found
  ```bash
  az aks net-diagnostics -n aks-overlay -g nonexistent-rg
  ```
  - Expected: Clear error message
  - Verify: Proper error handling

- [ ] **Test 5.3:** No permissions
  ```bash
  # Test with user lacking RBAC permissions (if possible)
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg
  ```
  - Expected: Permission denied error with helpful message
  - Verify: Graceful failure

- [ ] **Test 5.4:** Cluster in failed state (if available)
  - Expected: Diagnostic detects and reports failed state
  - Verify: No crash, appropriate warning

- [ ] **Test 5.5:** Invalid JSON report path
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --json-report /invalid/path/report.json
  ```
  - Expected: Clear error about invalid path
  - Verify: Proper error handling

### 6.6 Performance Tests ⏳

**Objective:** Verify acceptable performance compared to standalone tool

- [ ] **Test 6.1:** Execution time comparison
  ```bash
  # Standalone tool
  time python aks-net-diagnostics.py -n aks-overlay -g aks-overlay-rg
  
  # CLI version
  time az aks net-diagnostics -n aks-overlay -g aks-overlay-rg
  ```
  - Document: Execution times
  - Verify: CLI version not significantly slower
  - Acceptable: Within 20% of standalone tool

- [ ] **Test 6.2:** With --probe-test performance
  - Measure execution time with connectivity tests
  - Verify: No performance regressions

### 6.7 Azure CLI Output Format Tests ⏳

**Objective:** Verify command works with Azure CLI output formats

- [ ] **Test 7.1:** Default output format
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg
  ```
  - Expected: Custom formatted output (POC approach)
  - Verify: Readable console output

- [ ] **Test 7.2:** JSON output format
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --output json
  ```
  - Expected: Custom output (POC defers --output support)
  - Verify: Command doesn't crash
  - Note: Full --output support deferred to post-POC

- [ ] **Test 7.3:** Table output format
  ```bash
  az aks net-diagnostics -n aks-overlay -g aks-overlay-rg --output table
  ```
  - Expected: Custom output (POC defers --output support)
  - Verify: Command doesn't crash
  - Note: Full --output support deferred to post-POC

## Testing Progress

### Summary
- **Total Tests:** 29 tests across 7 categories
- **Completed:** 0
- **In Progress:** 0
- **Blocked:** 0
- **Failed:** 0

### Status by Category
- [ ] 6.1 Basic Functionality (0/6)
- [ ] 6.2 Cluster-Specific Tests (0/5)
- [ ] 6.3 Output Format Validation (0/3)
- [ ] 6.4 Comparison with Standalone (0/3)
- [ ] 6.5 Error Handling (0/5)
- [ ] 6.6 Performance Tests (0/2)
- [ ] 6.7 Azure CLI Output Formats (0/3)

## Issues Found

### Critical Issues
*None yet*

### Medium Priority Issues
*None yet*

### Low Priority Issues
*None yet*

## Test Results Log

### Test Run 1: [Date/Time]
*Pending first test run*

---

## Next Steps

1. ✅ Identify test clusters (DONE)
2. ⏳ Run basic functionality tests (Test 1.1-1.6)
3. ⏳ Run cluster-specific tests (Test 2.1-2.5)
4. ⏳ Validate output formats (Test 3.1-3.3)
5. ⏳ Compare with standalone tool (Test 4.1-4.3)
6. ⏳ Test error handling (Test 5.1-5.5)
7. ⏳ Measure performance (Test 6.1-6.2)
8. ⏳ Test output format compatibility (Test 7.1-7.3)
9. ⏳ Document all findings and issues
10. ⏳ Create Phase 6 completion report

## Notes

- **POC Approach:** Keeping standalone tool output format, deferring Azure CLI output format integration
- **Test Environment:** Python 3.10.12, Azure CLI 2.78.0 (dev mode)
- **Branch:** aks-net-diagnostics-integration
- **Standalone Tool:** Located at ~/aks-net-diagnostics (azure-sdk branch)

---

**Last Updated:** October 20, 2025  
**Status:** Ready to begin testing
