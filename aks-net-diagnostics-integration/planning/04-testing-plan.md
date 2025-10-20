# Testing Plan

## Overview

This document outlines the comprehensive testing strategy for integrating aks-net-diagnostics into Azure CLI.

## Testing Levels

### 1. Unit Tests

#### Location
`src/azure-cli/azure/cli/command_modules/acs/tests/latest/test_aks_net_diagnostics.py`

#### Test Categories

##### A. SDK Client Tests
Test the new SDKClient wrapper:

```python
class TestSDKClient(unittest.TestCase):
    """Tests for SDK client wrapper"""
    
    def test_get_managed_cluster(self):
        """Test getting cluster details"""
        
    def test_get_vnet(self):
        """Test getting VNet details"""
        
    def test_error_handling_cluster_not_found(self):
        """Test error handling when cluster doesn't exist"""
        
    def test_error_handling_no_permissions(self):
        """Test error handling when user lacks permissions"""
```

##### B. Analyzer Tests
Port existing tests from aks-net-diagnostics:

```python
class TestNSGAnalyzer(unittest.TestCase):
    """Tests for NSG analyzer"""
    
    def test_detect_blocking_rule(self):
        """Test detection of NSG rules blocking AKS traffic"""
        
    def test_inter_node_communication(self):
        """Test inter-node communication validation"""
```

##### C. Command Execution Tests
Test the CLI command integration:

```python
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

class AksNetDiagnosticsScenarioTest(ScenarioTest):
    """Scenario tests for net-diagnostics command"""
    
    @ResourceGroupPreparer()
    def test_net_diagnostics_basic(self, resource_group):
        """Test basic command execution"""
        result = self.cmd('aks net-diagnostics -n {cluster} -g {rg}').get_output_in_json()
        self.assertIn('findings', result)
        self.assertIn('cluster_info', result)
    
    @ResourceGroupPreparer()
    def test_net_diagnostics_with_flags(self, resource_group):
        """Test command with all flags"""
        self.cmd('aks net-diagnostics -n {cluster} -g {rg} --details --probe-test --json-report test.json')
```

#### Running Unit Tests

```bash
# Run all ACS tests
azdev test acs

# Run only net-diagnostics tests
azdev test acs --test test_aks_net_diagnostics

# Run specific test class
azdev test acs --test TestSDKClient

# Run with coverage
azdev test acs --test test_aks_net_diagnostics --coverage
```

### 2. Integration Tests

#### Prerequisites
- Active Azure subscription
- Permissions to create AKS clusters
- Test resource group

#### Test Scenarios

##### Scenario 1: Healthy Cluster
**Setup:**
- Create basic AKS cluster (no custom networking)
- Standard CNI, no custom DNS
- No NSG restrictions

**Tests:**
```bash
az aks net-diagnostics -n healthy-cluster -g test-rg
# Expected: No critical findings, cluster should pass all checks

az aks net-diagnostics -n healthy-cluster -g test-rg --details
# Expected: Detailed output showing all components analyzed

az aks net-diagnostics -n healthy-cluster -g test-rg --probe-test
# Expected: All connectivity tests pass

az aks net-diagnostics -n healthy-cluster -g test-rg --json-report
# Expected: JSON file created with results
```

##### Scenario 2: Private Cluster
**Setup:**
- Create private AKS cluster
- Custom DNS configured
- Private endpoint enabled

**Tests:**
```bash
az aks net-diagnostics -n private-cluster -g test-rg
# Expected: Detects private cluster, analyzes private DNS

az aks net-diagnostics -n private-cluster -g test-rg --details
# Expected: Shows private endpoint details, DNS zone links
```

##### Scenario 3: Cluster with NSG Issues
**Setup:**
- Create AKS cluster
- Add NSG rule blocking required traffic (e.g., block 443 outbound)

**Tests:**
```bash
az aks net-diagnostics -n nsg-issue-cluster -g test-rg
# Expected: CRITICAL finding about blocked traffic

az aks net-diagnostics -n nsg-issue-cluster -g test-rg --probe-test
# Expected: Connectivity test failures
```

##### Scenario 4: Cluster with Custom DNS
**Setup:**
- Create AKS cluster with custom DNS
- DNS not configured to forward to Azure DNS

**Tests:**
```bash
az aks net-diagnostics -n custom-dns-cluster -g test-rg
# Expected: Detects DNS misconfiguration

az aks net-diagnostics -n custom-dns-cluster -g test-rg --probe-test
# Expected: DNS resolution failures
```

##### Scenario 5: Cluster Behind Firewall/NVA
**Setup:**
- Create AKS cluster with custom route table
- Routes pointing to NVA/firewall

**Tests:**
```bash
az aks net-diagnostics -n firewall-cluster -g test-rg
# Expected: Detects UDR configuration, warns about potential issues

az aks net-diagnostics -n firewall-cluster -g test-rg --details
# Expected: Shows route table details
```

##### Scenario 6: Failed/Failing Cluster
**Setup:**
- Create cluster in failed state (or break existing cluster)

**Tests:**
```bash
az aks net-diagnostics -n failed-cluster -g test-rg
# Expected: Detects cluster failure, analyzes root cause

az aks net-diagnostics -n failed-cluster -g test-rg --details
# Expected: Detailed analysis of failure reasons
```

#### Test Matrix

| Scenario | Basic | --details | --probe-test | --json-report | Expected Findings |
|----------|-------|-----------|--------------|---------------|-------------------|
| Healthy Cluster | ✓ | ✓ | ✓ | ✓ | None or INFO |
| Private Cluster | ✓ | ✓ | ✓ | ✓ | INFO about private config |
| NSG Issues | ✓ | ✓ | ✓ | ✓ | CRITICAL - blocked traffic |
| Custom DNS | ✓ | ✓ | ✓ | ✓ | CRITICAL - DNS misconfigured |
| Behind Firewall | ✓ | ✓ | ✓ | ✓ | WARNING - UDR detected |
| Failed Cluster | ✓ | ✓ | - | ✓ | CRITICAL - cluster failed |

### 3. Comparison Testing

#### Purpose
Verify that Azure CLI integration produces same results as standalone tool.

#### Test Process

1. **Select test cluster** (use production or test cluster)

2. **Run standalone tool:**
   ```bash
   cd aks-net-diagnostics
   python aks-net-diagnostics.py -n test-cluster -g test-rg --details --json-report standalone.json
   ```

3. **Run CLI command:**
   ```bash
   az aks net-diagnostics -n test-cluster -g test-rg --details --json-report cli.json
   ```

4. **Compare outputs:**
   ```bash
   # Compare finding counts
   jq '.findings | length' standalone.json
   jq '.findings | length' cli.json
   
   # Compare finding codes
   jq '[.findings[].code] | sort' standalone.json
   jq '[.findings[].code] | sort' cli.json
   
   # Compare cluster info
   diff <(jq '.cluster_info' standalone.json | sort) <(jq '.cluster_info' cli.json | sort)
   ```

5. **Document differences:**
   - Are finding counts identical?
   - Are finding codes identical?
   - Are messages similar/identical?
   - Are recommendations similar/identical?
   - If different, document why (acceptable vs. bug)

#### Acceptance Criteria
- Finding counts should be identical
- All finding codes should match
- Messages may differ slightly in formatting but content should be same
- Any differences must be documented and justified

### 4. Performance Testing

#### Metrics to Measure

1. **Execution Time:**
   ```bash
   # Standalone
   time python aks-net-diagnostics.py -n cluster -g rg
   
   # CLI
   time az aks net-diagnostics -n cluster -g rg
   ```

2. **Memory Usage:**
   ```bash
   # Use /usr/bin/time -v on Linux
   /usr/bin/time -v az aks net-diagnostics -n cluster -g rg
   ```

3. **API Call Count:**
   - Enable debug logging: `az aks net-diagnostics -n cluster -g rg --debug`
   - Count number of Azure API calls made
   - Compare with standalone tool

#### Performance Targets
- Execution time: Within 20% of standalone tool
- Memory usage: Within 30% of standalone tool
- API calls: Same or fewer than standalone tool

#### Optimization If Needed
- Cache API responses where possible
- Parallelize independent API calls
- Use batch operations where available

### 5. Edge Case Testing

#### Authentication Scenarios
- [ ] Test with user identity (az login)
- [ ] Test with service principal
- [ ] Test with managed identity (if running on Azure VM)
- [ ] Test with expired credentials (should fail gracefully)
- [ ] Test with insufficient permissions (should report clear error)

#### Cluster Configurations
- [ ] Single node pool
- [ ] Multiple node pools
- [ ] System + user node pools
- [ ] Windows node pools (if applicable)
- [ ] Virtual nodes / ACI (if applicable)
- [ ] Different VM sizes
- [ ] Different Kubernetes versions

#### Network Configurations
- [ ] Azure CNI
- [ ] Kubenet
- [ ] Bring your own CNI
- [ ] Basic networking (single subnet)
- [ ] Advanced networking (multiple subnets)
- [ ] VNet peering scenarios
- [ ] Multiple VNets

#### Output Scenarios
- [ ] `--output json`
- [ ] `--output table`
- [ ] `--output yaml`
- [ ] `--output tsv`
- [ ] Redirect output: `az aks net-diagnostics ... > output.txt`
- [ ] Pipe output: `az aks net-diagnostics ... | jq .findings`

#### Error Scenarios
- [ ] Cluster doesn't exist
- [ ] Resource group doesn't exist
- [ ] No permissions to cluster
- [ ] Network timeout
- [ ] API throttling
- [ ] Invalid parameters
- [ ] VMSS command execution failure (for --probe-test)

### 6. Regression Testing

After any code changes:
1. Re-run all unit tests
2. Re-run key integration scenarios
3. Re-run comparison test
4. Verify no new findings on known-good cluster
5. Verify same findings on known-problematic cluster

### 7. User Acceptance Testing (UAT)

#### Test Users
- Azure CLI team members
- AKS support engineers
- Beta users (if available)

#### UAT Scenarios
1. Install Azure CLI with new feature
2. Run on their own clusters
3. Collect feedback:
   - Is output clear?
   - Are findings actionable?
   - Are recommendations helpful?
   - Any bugs or issues?
   - Performance acceptable?

#### Feedback Collection
- GitHub issues for bugs
- Survey for feature feedback
- Direct interviews with heavy users

## Test Data Management

### Test Clusters
Maintain a set of test clusters with known configurations:

1. **reference-cluster-healthy** - Clean, working cluster
2. **reference-cluster-private** - Private cluster with correct config
3. **reference-cluster-nsg-issue** - Known NSG blocking issue
4. **reference-cluster-dns-issue** - Known DNS misconfiguration
5. **reference-cluster-firewall** - Cluster behind NVA

### Test Credentials
- Use service principal for automated tests
- Document required permissions
- Rotate credentials regularly
- Store securely (Azure Key Vault, etc.)

## Continuous Testing

### Pre-Commit
```bash
# Run unit tests before committing
azdev test acs --test test_aks_net_diagnostics
```

### Pre-Push
```bash
# Run style checks
azdev style acs

# Run linter
azdev linter acs

# Run all tests
azdev test acs
```

### CI/CD Pipeline
Should run automatically on PR:
1. Unit tests
2. Style checks
3. Linter
4. Integration tests (if test cluster available)

## Test Documentation

### Test Results Template

```markdown
## Test Results - [Date]

**Tester:** [Name]
**Environment:** [Dev/Test/Production]
**Azure CLI Version:** [Version]

### Test Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Skipped: W

### Failed Tests
1. **Test Name:** 
   - **Error:** 
   - **Expected:** 
   - **Actual:** 
   - **Action:** 

### Performance Metrics
- Execution time: Xs
- Memory usage: XMB
- API calls: X

### Notes
[Any additional observations]
```

## Definition of Done

A test phase is complete when:
- [ ] All unit tests pass (100% pass rate)
- [ ] All integration scenarios tested
- [ ] Comparison test shows <5% variance
- [ ] Performance within targets
- [ ] All edge cases tested
- [ ] No P0 or P1 bugs outstanding
- [ ] Test documentation complete
- [ ] Test coverage >80% (if measured)

## Appendix: Test Cluster Setup Scripts

### Create Test Cluster

```bash
#!/bin/bash
# create-test-cluster.sh

RG="aks-net-diag-test-rg"
LOCATION="eastus"
CLUSTER_NAME="test-cluster"

# Create resource group
az group create -n $RG -l $LOCATION

# Create AKS cluster
az aks create \
  -n $CLUSTER_NAME \
  -g $RG \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --network-plugin azure \
  --generate-ssh-keys

echo "Cluster created: $CLUSTER_NAME in $RG"
```

### Create Problematic Test Cluster

```bash
#!/bin/bash
# create-problematic-cluster.sh

RG="aks-net-diag-test-rg"
LOCATION="eastus"
CLUSTER_NAME="nsg-issue-cluster"
VNET_NAME="test-vnet"
SUBNET_NAME="aks-subnet"
NSG_NAME="blocking-nsg"

# Create VNet
az network vnet create \
  -n $VNET_NAME \
  -g $RG \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.0.0/24

# Create NSG with blocking rule
az network nsg create -n $NSG_NAME -g $RG
az network nsg rule create \
  -n block-https \
  --nsg-name $NSG_NAME \
  -g $RG \
  --priority 100 \
  --destination-port-ranges 443 \
  --direction Outbound \
  --access Deny

# Associate NSG with subnet
az network vnet subnet update \
  -n $SUBNET_NAME \
  --vnet-name $VNET_NAME \
  -g $RG \
  --network-security-group $NSG_NAME

# Create cluster
az aks create \
  -n $CLUSTER_NAME \
  -g $RG \
  --vnet-subnet-id $(az network vnet subnet show -n $SUBNET_NAME --vnet-name $VNET_NAME -g $RG --query id -o tsv) \
  --network-plugin azure

echo "Problematic cluster created: $CLUSTER_NAME"
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup-test-resources.sh

RG="aks-net-diag-test-rg"

echo "Deleting resource group: $RG"
az group delete -n $RG --yes --no-wait

echo "Cleanup initiated. Resources will be deleted in background."
```

## Next Steps

After completing testing:
1. Document all test results
2. Fix any bugs found
3. Update documentation with known issues/limitations
4. Proceed to Phase 5 (Documentation & Polish)
