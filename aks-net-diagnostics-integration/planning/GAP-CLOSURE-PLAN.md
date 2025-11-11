# AKS Net-Diagnostics - Gap Closure Plan

**Document Version:** 1.0  
**Date:** November 10, 2025  
**Status:** Planning Phase  
**Goal:** Address identified gaps to move from POC to production-ready feature

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Gap Classification](#gap-classification)
3. [Implementation Phases](#implementation-phases)
4. [Detailed Task Breakdown](#detailed-task-breakdown)
5. [Testing Strategy](#testing-strategy)
6. [Risk Assessment](#risk-assessment)
7. [Success Criteria](#success-criteria)

---

## Executive Summary

### Current State

The AKS Net-Diagnostics POC is **functionally complete** for core scenarios but has **9 identified gaps** that limit production readiness:

- **3 Critical Gaps** - Block adoption for modern AKS deployments
- **5 High/Medium Priority Gaps** - Limit functionality or produce false findings
- **1 Low Priority Gap** - Edge case validation

### Proposed Solution

A **4-phase implementation plan** to systematically close gaps based on impact and adoption risk:

| Phase | Focus | Duration | Gaps Closed |
|-------|-------|----------|-------------|
| **Phase 1** | Quick Wins | 8-12 hours | 4 gaps (low-hanging fruit) |
| **Phase 2** | Critical Infrastructure | 16-24 hours | 2 gaps (NAP + Network Isolated) |
| **Phase 3** | Configuration Validation | 6-8 hours | 2 gaps (BYO DNS + API VNet Integration) |
| **Phase 4** | Edge Cases | 2-4 hours | 1 gap (Cross-subscription) |

**Total Estimated Effort:** 32-48 hours (4-6 working days)

### Key Priorities

1. 🔴 **CRITICAL:** Non-VMSS support (NAP, Virtual Nodes) - Tool currently fails
2. 🔴 **HIGH:** Network Isolated clusters - Growing security requirement
3. 🟡 **HIGH:** Azure CNI Overlay NSG validation - Quick fix, important correctness
4. 🟡 **MEDIUM:** BYO Private DNS Zone + API VNet Integration - Specific but important scenarios

---

## Gap Classification

### Tier 1: Critical Blockers (Adoption Risk)

**Impact:** Tool fails completely or produces incorrect analysis

| # | Gap | Current Impact | Adoption Risk |
|---|-----|---------------|---------------|
| 1 | Non-VMSS Node Support | Tool fails - empty VMSS list | **CRITICAL** - NAP adoption growing |
| 2 | Network Isolated Clusters | Tool fails or incorrect analysis | **HIGH** - Zero-trust requirement |
| 3 | Azure CNI Overlay NSG | Missing pod CIDR validation | **MEDIUM** - Common network plugin |

**Business Justification:**
- **Node Auto-Provisioning (NAP)** is a recommended pattern for cost optimization
- **Network Isolated clusters** are required for compliance/security-sensitive workloads
- **Azure CNI Overlay** is the default for new AKS clusters in many regions

---

### Tier 2: Important Functionality Gaps

**Impact:** Specific scenarios unsupported or may produce false findings

| # | Gap | Current Impact | User Experience |
|---|-----|---------------|-----------------|
| 4 | BYO Private DNS Zone | Unknown behavior | May generate false findings |
| 5 | API Server VNet Integration | Not tested | Likely false findings about missing DNS zone |
| 6 | Node Pool Display | Data collected, not shown | Reduced visibility |
| 7 | User-Assigned NAT Gateway | Not validated | Unknown behavior |

**Business Justification:**
- **BYO Private DNS Zone**: Common in enterprise environments with existing DNS infrastructure
- **API Server VNet Integration**: New AKS feature gaining adoption
- **Node Pool Display**: Expected functionality for multi-pool clusters

---

### Tier 3: Edge Cases & Nice-to-Have

**Impact:** Limited scenarios or future considerations

| # | Gap | Current Impact | Priority |
|---|-----|---------------|----------|
| 8 | Cross-Subscription VNet | Code supports, not tested | LOW - Edge case |
| 9 | Azure CNI (Cilium) | Code should work, not tested | FUTURE - Limited adoption |
| 10 | Standard Output Formats | POC output acceptable | FUTURE - UX enhancement |
| 11 | Virtual Machines Node Pools | Not supported | FUTURE - New feature |

---

## Implementation Phases

### Phase 1: Quick Wins (8-12 hours)

**Goal:** Close easy gaps to improve coverage and build momentum

**Timeline:** 1-2 days

**Gaps Addressed:**

#### 1.1 Azure CNI Overlay NSG Rules ✅ (2-3 hours)
- **Priority:** 🟡 HIGH
- **Files:** `nsg_analyzer.py`, `models.py`
- **Changes:**
  - Add pod CIDR detection from cluster network profile
  - Add NSG rules for pod CIDR traffic:
    - Node CIDR → Pod CIDR (service routing)
    - Pod CIDR → Pod CIDR (pod-to-pod communication)
  - Add new finding codes: `NSG_POD_CIDR_BLOCKED`, `NSG_POD_CIDR_PARTIAL`
- **Testing:** Use existing overlay test cluster (`aks-demo-overlay`)
- **Success Criteria:** No false negatives on overlay clusters

#### 1.2 Node Pool Display (Phase 8) ✅ (2-3 hours)
- **Priority:** 🟡 MEDIUM
- **Files:** `report_generator.py`, `cluster_data_collector.py`
- **Changes:**
  - Display node pool details in summary report
  - Show pod CIDR allocation for pod subnet mode
  - Format multi-pool configurations clearly
- **Testing:** Use multi-pool test clusters
- **Success Criteria:** Clear visibility of all node pools

#### 1.3 User-Assigned NAT Gateway Validation ✅ (2-3 hours)
- **Priority:** 🟢 LOW (but easy to test)
- **Files:** `outbound_analyzer.py`
- **Changes:**
  - Create test cluster with user-assigned NAT Gateway
  - Validate NAT Gateway detection logic
  - Test subnet-attached NAT Gateway scenarios
- **Testing:** Create new test cluster
- **Success Criteria:** Correct detection and analysis

#### 1.4 AKS LocalDNS Feature Validation ✅ (2-3 hours)
- **Priority:** 🟡 MEDIUM
- **Files:** `dns_analyzer.py`, `connectivity_tester.py`
- **Changes:**
  - Research LocalDNS configuration (169.254.10.10/11)
  - Update DNS tests to handle LocalDNS nameservers
  - Document LocalDNS impact on diagnostics
- **Testing:** Enable LocalDNS on test cluster (if available)
- **Success Criteria:** No false findings for LocalDNS clusters

**Phase 1 Deliverables:**
- ✅ 4 gaps closed
- ✅ Test coverage improved
- ✅ Documentation updated

---

### Phase 2: Critical Infrastructure Support (16-24 hours)

**Goal:** Support modern AKS deployment patterns (highest adoption risk)

**Timeline:** 2-3 days

**Gaps Addressed:**

#### 2.1 Non-VMSS Node Support 🔴 (10-14 hours)

**Priority:** 🔴 CRITICAL

**Scope:** Support Node Auto-Provisioning (NAP), Virtual Nodes (ACI), Virtual Machines node pools

**Implementation Strategy:**

1. **Detection & Data Collection** (4-5 hours)
   - **Files:** `cluster_data_collector.py`, `models.py`
   - Detect node infrastructure type from agent pool properties
   - Add NAP-specific data collection:
     ```python
     # Detect NAP from agent pool properties
     if 'nodeProvisioningProfile' in agent_pool:
         # Node Auto-Provisioning
         node_type = 'NAP'
     elif 'mode' == 'User' and 'count' == 0:
         # Virtual Nodes (ACI)
         node_type = 'VirtualNodes'
     elif 'type' == 'VirtualMachines':
         # VM node pools
         node_type = 'VirtualMachines'
     else:
         # Traditional VMSS
         node_type = 'VMSS'
     ```
   - Collect VM-specific network configuration for VM node pools
   - Add Virtual Node (ACI) detection and subnet info

2. **Connectivity Testing Adaptation** (4-5 hours)
   - **Files:** `connectivity_tester.py`, `orchestrator.py`
   - Add alternative connectivity test methods:
     - **NAP:** Use managed identity + API calls instead of run-command
     - **Virtual Nodes:** Skip node-level tests (ACI limitations)
     - **VM Node Pools:** Use VM run-command API
   - Graceful degradation when run-command unavailable
   - Add informational findings for limited connectivity testing

3. **Analysis Updates** (2-4 hours)
   - **Files:** `nsg_analyzer.py`, `dns_analyzer.py`
   - Update NSG analysis for non-VMSS network interfaces
   - Handle different node identity patterns
   - Validate NAP-specific networking requirements

**Testing:**
- Create NAP test cluster
- Create Virtual Nodes test cluster (if supported)
- Create VM node pool test cluster
- Validate all analysis modules

**Success Criteria:**
- ✅ Tool completes analysis for NAP clusters
- ✅ Tool completes analysis for Virtual Nodes
- ✅ Tool completes analysis for VM node pools
- ✅ Clear messaging about connectivity test limitations
- ✅ No false positives/negatives

**Risk Mitigation:**
- NAP may not support all connectivity test methods → Document limitations
- Virtual Nodes have ACI restrictions → Skip incompatible tests
- API changes required → Test thoroughly

---

#### 2.2 Network Isolated Clusters 🔴 (6-10 hours)

**Priority:** 🔴 HIGH

**Scope:** Support outbound types `none` and `block` with private ACR bootstrap

**Implementation Strategy:**

1. **Outbound Type Detection** (2-3 hours)
   - **Files:** `outbound_analyzer.py`, `models.py`
   - Add `none` and `block` to supported outbound types
   - Detect bootstrap artifact source (`Cache` for private ACR)
   - Add new finding codes: `OUTBOUND_NETWORK_ISOLATED`, `OUTBOUND_BOOTSTRAP_CACHE`

2. **Analysis Adaptation** (2-3 hours)
   - **Files:** `nsg_analyzer.py`, `outbound_analyzer.py`
   - Skip public MCR connectivity checks for network isolated
   - Validate private ACR connectivity requirements
   - Check NSG rules for private ACR access
   - Validate bootstrap artifact source configuration

3. **Connectivity Testing Updates** (2-4 hours)
   - **Files:** `connectivity_tester.py`
   - Skip public MCR tests for `none`/`block` outbound
   - Add private ACR connectivity tests (if configured)
   - Update test recommendations for network isolated

**Testing:**
- Create network isolated cluster (`--outbound-type none`)
- Test with private ACR bootstrap
- Validate NSG/UDR analysis for zero-egress

**Success Criteria:**
- ✅ Tool completes analysis for network isolated clusters
- ✅ No false findings about missing public internet access
- ✅ Correct validation of private ACR requirements
- ✅ Clear guidance for network isolated setup

**Documentation Requirements:**
- Document network isolated cluster support
- Add troubleshooting guide for private ACR bootstrap
- Example configurations

---

**Phase 2 Deliverables:**
- ✅ 2 critical gaps closed
- ✅ Support for modern AKS patterns
- ✅ Production readiness significantly improved

---

### Phase 3: Configuration Validation (6-8 hours)

**Goal:** Support advanced private cluster configurations

**Timeline:** 1 day

**Gaps Addressed:**

#### 3.1 BYO Private DNS Zone 🟡 (2 hours)

**Priority:** 🟡 MEDIUM

**Scope:** Validate clusters with user-provided private DNS zones

**Implementation Strategy:**

1. **Test Cluster Creation** (1 hour)
   - Create private cluster with BYO private DNS zone
   - Test scenarios:
     - Private DNS zone in user resource group
     - Private DNS zone in node resource group
     - Cross-subscription private DNS zone
     - Custom DNS zone name

2. **Validation & Fixes** (1 hour)
   - **Files:** `dns_analyzer.py`
   - Validate BYO DNS zone detection logic
   - Fix any false findings
   - Document expected behavior

**Testing:**
- Run diagnostics on BYO DNS zone cluster
- Verify VNet link detection
- Validate DNS configuration warnings

**Success Criteria:**
- ✅ Correct detection of BYO private DNS zone
- ✅ No false findings about missing DNS zone
- ✅ Accurate VNet link validation

---

#### 3.2 API Server VNet Integration 🟡 (4-6 hours)

**Priority:** 🟡 MEDIUM

**Scope:** Support API Server VNet Integration (no private endpoint/DNS zone)

**Implementation Strategy:**

1. **Feature Research** (1 hour)
   - Review [API Server VNet Integration](https://learn.microsoft.com/en-us/azure/aks/api-server-vnet-integration) documentation
   - Understand delegated subnet requirements
   - Identify API differences vs private endpoint mode

2. **Detection Logic** (2-3 hours)
   - **Files:** `api_server_analyzer.py`, `dns_analyzer.py`
   - Add API Server VNet Integration detection:
     ```python
     # Detect VNet integration mode
     if cluster.api_server_access_profile:
         if cluster.api_server_access_profile.enable_vnet_integration:
             return 'vnet_integration'
         elif cluster.api_server_access_profile.enable_private_cluster:
             return 'private_endpoint'
     return 'public'
     ```
   - Skip private DNS zone checks for VNet integration mode
   - Validate delegated subnet configuration
   - Check NSG rules for delegated subnet

3. **Testing** (1-2 hours)
   - Create test cluster with API Server VNet Integration
   - Run diagnostics and validate output
   - Fix any false findings

**Success Criteria:**
- ✅ Correct detection of VNet integration mode
- ✅ No false findings about missing private DNS zone
- ✅ Accurate delegated subnet validation
- ✅ Clear distinction between private endpoint vs VNet integration

---

**Phase 3 Deliverables:**
- ✅ 2 important gaps closed
- ✅ Support for advanced private cluster configurations
- ✅ Improved accuracy for enterprise scenarios

---

### Phase 4: Edge Cases & Refinements (2-4 hours)

**Goal:** Complete coverage for remaining scenarios

**Timeline:** 0.5-1 day

**Gaps Addressed:**

#### 4.1 Cross-Subscription BYO VNet 🟢 (2 hours)

**Priority:** 🟢 LOW

**Scope:** Validate cross-subscription VNet scenarios

**Implementation Strategy:**

1. **Test Cluster Creation** (1 hour)
   - Create cluster in Subscription A
   - Use VNet from Subscription B
   - Configure appropriate permissions

2. **Validation** (1 hour)
   - **Files:** `cluster_data_collector.py`, `dns_analyzer.py`
   - Run diagnostics
   - Verify cross-subscription resource retrieval
   - Validate permission handling

**Success Criteria:**
- ✅ Tool works for cross-subscription VNet
- ✅ Graceful handling of permission issues
- ✅ Accurate VNet link validation

---

#### 4.2 Azure CNI (Cilium) Validation 🔵 (1-2 hours)

**Priority:** 🔵 FUTURE (Optional)

**Scope:** Validate Cilium network plugin support

**Implementation Strategy:**

1. **Test Cluster** (0.5-1 hour)
   - Create Azure CNI (Cilium) cluster if available
   - Document any Cilium-specific networking requirements

2. **Validation** (0.5-1 hour)
   - Run diagnostics
   - Verify network plugin detection
   - Document any Cilium-specific considerations

**Success Criteria:**
- ✅ Accurate Cilium detection
- ✅ No false findings
- ✅ Documentation updated

---

**Phase 4 Deliverables:**
- ✅ All identified gaps closed
- ✅ Comprehensive scenario coverage
- ✅ Production-ready feature

---

## Detailed Task Breakdown

### Phase 1 Tasks

<details>
<summary><b>Task 1.1: Azure CNI Overlay NSG Rules</b></summary>

**Estimated Time:** 2-3 hours

**Prerequisites:**
- Existing overlay test cluster (`aks-demo-overlay`)
- Understanding of Azure CNI Overlay networking

**Implementation Steps:**

1. **Research** (30 min)
   - Review [Azure CNI Overlay NSG requirements](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay?tabs=kubectl#network-security-groups)
   - Document required NSG rules:
     - Node CIDR → Pod CIDR
     - Pod CIDR → Pod CIDR

2. **Code Changes** (60-90 min)
   - Update `cluster_data_collector.py`:
     ```python
     def collect_cluster_info(self):
         # ... existing code ...
         
         # Get pod CIDR for overlay mode
         if cluster.network_profile.network_plugin == 'azure':
             if cluster.network_profile.network_plugin_mode == 'overlay':
                 pod_cidr = cluster.network_profile.pod_cidr
                 # Store for NSG analysis
     ```
   
   - Update `nsg_analyzer.py`:
     ```python
     def _check_overlay_pod_cidr_rules(self):
         """Check NSG rules for Azure CNI Overlay pod CIDR traffic."""
         if not self.is_overlay_mode:
             return
         
         node_cidr = self.cluster_data['vnet']['subnets'][0]['address_prefix']
         pod_cidr = self.cluster_data['network_profile'].get('pod_cidr')
         
         # Check Node CIDR → Pod CIDR
         # Check Pod CIDR → Pod CIDR
         # Add findings if blocked
     ```
   
   - Add finding codes to `models.py`:
     ```python
     NSG_POD_CIDR_BLOCKED = "nsg_pod_cidr_blocked"
     NSG_POD_CIDR_PARTIAL = "nsg_pod_cidr_partial"
     ```

3. **Testing** (30-60 min)
   - Run against `aks-demo-overlay` cluster
   - Verify pod CIDR detection
   - Validate NSG rule checks
   - Test with missing NSG rules

4. **Documentation** (15 min)
   - Update COVERAGE-MATRIX.md
   - Add overlay NSG validation to feature list

**Success Criteria:**
- [ ] Pod CIDR correctly detected for overlay clusters
- [ ] NSG rules validated for pod traffic
- [ ] Appropriate findings generated for missing rules
- [ ] No false positives on properly configured overlay clusters

</details>

<details>
<summary><b>Task 1.2: Node Pool Display</b></summary>

**Estimated Time:** 2-3 hours

**Prerequisites:**
- Multi-pool test cluster
- Data already collected in `cluster_data_collector.py`

**Implementation Steps:**

1. **Design Output Format** (30 min)
   - Design clear node pool display format
   - Example:
     ```
     **Node Pools:**
     - systempool (System)
       - VM Size: Standard_DS2_v2
       - Count: 3
       - Mode: System
       - CIDR: 10.224.0.0/16 (Pod Subnet)
     
     - userpool (User)
       - VM Size: Standard_DS3_v2
       - Count: 2
       - Mode: User
       - CIDR: 10.225.0.0/16 (Pod Subnet)
     ```

2. **Code Changes** (60-90 min)
   - Update `report_generator.py`:
     ```python
     def _format_node_pools(self, cluster_data):
         """Format node pool information."""
         pools = cluster_data.get('agent_pools', [])
         
         output = ["**Node Pools:**"]
         for pool in pools:
             output.append(f"- {pool['name']} ({pool['mode']})")
             output.append(f"  - VM Size: {pool['vm_size']}")
             output.append(f"  - Count: {pool['count']}")
             
             # Show pod CIDR if pod subnet mode
             if pool.get('pod_subnet_id'):
                 pod_cidr = self._get_pod_cidr_for_pool(pool)
                 output.append(f"  - Pod CIDR: {pod_cidr}")
         
         return "\n".join(output)
     ```

3. **Testing** (30-60 min)
   - Test with single pool cluster
   - Test with multi-pool cluster
   - Test with pod subnet mode
   - Test with system + user pools

4. **Documentation** (15 min)
   - Update feature documentation
   - Add examples to user guide

**Success Criteria:**
- [ ] All node pools displayed clearly
- [ ] Pod CIDR shown for pod subnet mode
- [ ] Clean formatting for 1-N pools
- [ ] Consistent with Azure CLI conventions

</details>

<details>
<summary><b>Task 1.3: User-Assigned NAT Gateway Validation</b></summary>

**Estimated Time:** 2-3 hours

**Prerequisites:**
- Azure subscription with NAT Gateway support
- Test resource group

**Implementation Steps:**

1. **Create Test Cluster** (60-90 min)
   ```bash
   # Create NAT Gateway
   az network nat gateway create \
     --resource-group aks-test-rg \
     --name test-nat-gateway \
     --public-ip-addresses nat-gateway-pip \
     --location eastus
   
   # Create VNet with NAT Gateway attached
   az network vnet create \
     --resource-group aks-test-rg \
     --name test-vnet \
     --address-prefix 10.0.0.0/16 \
     --subnet-name aks-subnet \
     --subnet-prefix 10.0.1.0/24
   
   az network vnet subnet update \
     --resource-group aks-test-rg \
     --vnet-name test-vnet \
     --name aks-subnet \
     --nat-gateway test-nat-gateway
   
   # Create AKS cluster with user-assigned NAT Gateway
   az aks create \
     --resource-group aks-test-rg \
     --name aks-user-nat \
     --vnet-subnet-id /subscriptions/.../aks-subnet \
     --outbound-type userAssignedNATGateway \
     --network-plugin azure
   ```

2. **Run Diagnostics** (30 min)
   ```bash
   az aks net-diagnostics -n aks-user-nat -g aks-test-rg --details
   ```

3. **Validate & Fix** (30-60 min)
   - Verify NAT Gateway detection in `outbound_analyzer.py`
   - Check public IP detection
   - Validate subnet association
   - Fix any issues found

4. **Documentation** (15 min)
   - Update COVERAGE-MATRIX.md (⚠️ → ✅)
   - Document user-assigned NAT Gateway support

**Success Criteria:**
- [ ] NAT Gateway correctly detected
- [ ] Public IPs correctly identified
- [ ] Subnet association validated
- [ ] No false findings

</details>

<details>
<summary><b>Task 1.4: AKS LocalDNS Validation</b></summary>

**Estimated Time:** 2-3 hours

**Prerequisites:**
- AKS cluster with Kubernetes 1.31+
- LocalDNS feature availability

**Implementation Steps:**

1. **Research** (30-60 min)
   - Review [LocalDNS documentation](https://learn.microsoft.com/en-us/azure/aks/localdns-custom)
   - Understand 169.254.10.10/11 nameserver configuration
   - Document DNS resolution path: Pods → LocalDNS → CoreDNS

2. **Enable LocalDNS on Test Cluster** (30 min)
   ```bash
   # Enable LocalDNS on node pool (if supported)
   az aks nodepool update \
     --resource-group aks-test-rg \
     --cluster-name test-cluster \
     --name nodepool1 \
     --enable-local-dns
   ```

3. **Run Diagnostics & Analyze** (30-60 min)
   - Run connectivity tests
   - Check DNS test output
   - Identify any unexpected nameserver addresses

4. **Code Updates** (30-60 min)
   - Update `dns_analyzer.py`:
     ```python
     def _detect_local_dns(self):
         """Detect if LocalDNS is enabled."""
         # Check for 169.254.10.10 or 169.254.10.11 nameservers
         # Add informational finding if detected
     ```
   
   - Update `connectivity_tester.py`:
     ```python
     # Handle LocalDNS nameservers in DNS tests
     if '169.254.10.10' in nameservers or '169.254.10.11' in nameservers:
         # LocalDNS detected - adjust test expectations
     ```

5. **Documentation** (15 min)
   - Document LocalDNS support
   - Add to known configurations

**Success Criteria:**
- [ ] LocalDNS detected if enabled
- [ ] DNS tests handle LocalDNS nameservers
- [ ] No false findings for LocalDNS clusters
- [ ] Clear messaging about LocalDNS presence

</details>

---

### Phase 2 Tasks

<details>
<summary><b>Task 2.1: Non-VMSS Node Support</b></summary>

**Estimated Time:** 10-14 hours

**Prerequisites:**
- Understanding of NAP, Virtual Nodes, VM node pools
- Test subscription with required quotas

**Sub-Tasks:**

**2.1.1 Detection & Data Collection** ✅ (COMPLETED for VM Node Pools)

1. **Research** (1 hour) ✅
   - ✅ Reviewed VM node pools documentation
   - ✅ Identified API differences (type='VirtualMachines', no vmSize, virtualMachinesProfile)
   - ⏳ Review NAP documentation (pending)
   - ⏳ Review Virtual Nodes documentation (pending)

2. **Update Data Collection** (2-3 hours) ✅ (VM Node Pools)
   - File: `cluster_data_collector.py`
   - ✅ VM node pool detection: `type='VirtualMachines'`
   - ✅ VM network configuration collection via `collect_vm_info()`
   - ✅ Full NIC details collection (ip_configurations, subnet IDs)
   - ✅ VM subnet enrichment to agent pools
   - ⏳ NAP detection (pending)
   - ⏳ Virtual Nodes detection (pending)

3. **Testing** (1 hour) ✅
   - ✅ Created VM node pool test cluster (aks-vm-nodepool)
   - ✅ Verified data collection accuracy
   - ✅ Mixed cluster testing in progress (aks-mixed)

**2.1.2 Connectivity Testing Adaptation** ✅ (COMPLETED for VM Node Pools)

1. **Design Alternative Test Methods** (1 hour) ✅
   - ✅ VM Node Pools: Use `virtual_machines.begin_run_command()` API (no instance_id parameter)
   - ✅ Verified existing implementation already compatible
   - ⏳ NAP: Use Azure Monitor API or managed identity approach (pending)
   - ⏳ Virtual Nodes: Skip node-level tests (pending, document limitation)

2. **Implement Alternative Methods** (2-3 hours) ✅ (VM Node Pools)
   - File: `connectivity_tester.py`
   - ✅ VM run-command already implemented correctly
   - ✅ Verified all 4 connectivity tests work with VM nodes
   - ⏳ NAP implementation (pending)
   - ⏳ Virtual Nodes skip logic (pending)

3. **Testing** (1-2 hours) ✅
   - ✅ Tested VM node pool connectivity (all 4 tests passed)
   - ✅ Verified MCR DNS, Internet, API Server DNS, API Server HTTPS
   - ⏳ NAP testing (pending)
   - ⏳ Virtual Nodes testing (pending)

**2.1.3 Analysis Updates** ✅ (COMPLETED for VM Node Pools)

1. **Update NSG Analysis** (1-2 hours) ✅
   - File: `nsg_analyzer.py`
   - ✅ Added VM NIC collection from vm_info parameter
   - ✅ Enhanced _analyze_subnet_nsgs() to process VM NICs (Section 1b)
   - ✅ Enhanced _analyze_nic_nsgs() to analyze VM NICs with vm_name tracking
   - ✅ VM subnet NSGs correctly validated
   - ⏳ ACI subnet NSG rules (pending for Virtual Nodes)

2. **Update Orchestrator** (1 hour) ✅
   - File: `orchestrator.py`
   - ✅ Added _enrich_agent_pools_with_vm_subnets() function
   - ✅ Extracts subnet IDs from VM nic_details and enriches agent pools
   - ✅ Changed processing order: VM collection → enrichment → VNet analysis
   - ✅ Passes vm_analysis to NSG analyzer and report generator

3. **Update Report Display** (1 hour) ✅
   - File: `report_generator.py`
   - ✅ Added [VM] marker in node pool summary
   - ✅ Shows "Virtual Machines" in detailed view
   - ✅ Displays subnet CIDR for VM node pools
   - ✅ Helper methods for VM pool display (compact and detailed formats)

4. **Testing** (1 hour) ✅
   - ✅ Ran full diagnostics on VM node pool cluster
   - ✅ Verified [VM] marker display
   - ✅ Verified subnet CIDR display (aks-subnet 10.224.0.0/16)
   - ✅ Verified NSG analysis (1 subnet NSG found)
   - ✅ Verified VNet analysis (1 VNet with VM subnet)
   - ✅ Mixed cluster testing in progress

**Success Criteria:**

- [ ] NAP clusters fully supported (pending)
- [ ] Virtual Nodes supported with clear limitations (pending)
- [x] **VM node pools fully supported** ✅
- [x] **Clear messaging about test method differences** ✅
- [x] **No false positives or tool failures for VM pools** ✅
- [x] **VM NICs analyzed in NSG validation** ✅
- [x] **Subnet CIDR displayed for VM node pools** ✅
- [x] **Connectivity tests work with VM nodes** ✅
- [x] **Mixed VMSS+VM clusters supported** (testing in progress)

</details>

<details>
<summary><b>Task 2.2: Network Isolated Clusters</b></summary>

**Estimated Time:** 6-10 hours

**Prerequisites:**
- Understanding of network isolated clusters
- Private ACR for bootstrap
- Test subscription

**Sub-Tasks:**

**2.2.1 Outbound Type Detection** (2-3 hours)

1. **Research** (1 hour)
   - Review [Network Isolated Clusters](https://learn.microsoft.com/en-us/azure/aks/concepts-network-isolated)
   - Understand bootstrap artifact source options
   - Document private ACR requirements

2. **Update Detection Logic** (1-2 hours)
   - File: `outbound_analyzer.py`
   ```python
   SUPPORTED_OUTBOUND_TYPES = [
       'loadBalancer',
       'userDefinedRouting',
       'managedNATGateway',
       'userAssignedNATGateway',
       'none',      # Network isolated
       'block'      # Network isolated (preview)
   ]
   
   def _analyze_network_isolated(self):
       """Analyze network isolated configuration."""
       bootstrap_source = self.cluster_data.get('bootstrap_artifact_source')
       
       if bootstrap_source == 'Cache':
           # Private ACR bootstrap - validate private ACR access
           self._validate_private_acr_access()
       else:
           # May need public access
           self.add_finding(
               severity=Severity.WARNING,
               code=FindingCode.OUTBOUND_NETWORK_ISOLATED_BOOTSTRAP,
               message="Network isolated cluster without private ACR bootstrap"
           )
   ```
   
   - Add new finding codes to `models.py`

**2.2.2 Analysis Adaptation** (2-3 hours)

1. **Update NSG Analysis** (1 hour)
   - File: `nsg_analyzer.py`
   - Skip public MCR checks for network isolated
   - Validate private ACR NSG rules
   ```python
   def _check_outbound_requirements(self):
       if self.outbound_type in ['none', 'block']:
           # Network isolated - different requirements
           self._check_private_acr_access()
           return
       
       # Standard public internet checks
       self._check_mcr_access()
       # ...
   ```

2. **Update Outbound Analysis** (1-2 hours)
   - File: `outbound_analyzer.py`
   - Validate bootstrap artifact configuration
   - Check private ACR connectivity requirements
   - Document expected configuration

**2.2.3 Connectivity Testing Updates** (2-4 hours)

1. **Update Test Selection** (1-2 hours)
   - File: `connectivity_tester.py`
   ```python
   def _select_tests_for_outbound_type(self):
       if self.outbound_type in ['none', 'block']:
           # Skip public MCR tests
           return [
               'api_server_dns',
               'api_server_https',
               'private_acr_access'  # If configured
           ]
       
       # Standard tests for other outbound types
       return [
           'mcr_dns',
           'mcr_https',
           'api_server_dns',
           'api_server_https'
       ]
   ```

2. **Add Private ACR Tests** (1-2 hours)
   - Implement private ACR connectivity test
   - Validate private endpoint/service endpoint

3. **Testing** (1 hour)
   - Create network isolated test cluster
   - Run diagnostics
   - Verify correct analysis

**Success Criteria:**
- [ ] Network isolated clusters detected
- [ ] No false findings about missing public internet
- [ ] Private ACR validation working
- [ ] Clear guidance for network isolated setup
- [ ] Tests skip appropriately

</details>

---

### Phase 3 Tasks

<details>
<summary><b>Task 3.1: BYO Private DNS Zone</b></summary>

**Estimated Time:** 2 hours

**Implementation Steps:**

1. **Create Test Cluster** (1 hour)
   ```bash
   # Create private DNS zone first
   az network private-dns zone create \
     --resource-group aks-test-rg \
     --name privatelink.eastus.azmk8s.io
   
   # Create private cluster with BYO DNS zone
   az aks create \
     --resource-group aks-test-rg \
     --name aks-byo-dns \
     --enable-private-cluster \
     --private-dns-zone /subscriptions/.../privatelink.eastus.azmk8s.io \
     --network-plugin azure
   ```

2. **Run Diagnostics** (15 min)
   ```bash
   az aks net-diagnostics -n aks-byo-dns -g aks-test-rg --details
   ```

3. **Validate & Fix** (30 min)
   - Check DNS zone detection in `dns_analyzer.py`
   - Verify VNet link validation
   - Fix any false findings

4. **Test Cross-Subscription Scenario** (15 min)
   - Create DNS zone in different subscription
   - Run diagnostics
   - Verify cross-subscription handling

**Success Criteria:**
- [ ] BYO DNS zone correctly detected
- [ ] VNet links validated
- [ ] Cross-subscription support working
- [ ] No false findings

</details>

<details>
<summary><b>Task 3.2: API Server VNet Integration</b></summary>

**Estimated Time:** 4-6 hours

**Implementation Steps:**

1. **Feature Research** (1 hour)
   - Read [API Server VNet Integration](https://learn.microsoft.com/en-us/azure/aks/api-server-vnet-integration) documentation
   - Understand delegated subnet requirements
   - Document API property differences

2. **Create Test Cluster** (1 hour)
   ```bash
   # Create VNet with delegated subnet
   az network vnet create \
     --resource-group aks-test-rg \
     --name test-vnet \
     --address-prefix 10.0.0.0/16 \
     --subnet-name aks-subnet \
     --subnet-prefix 10.0.1.0/24
   
   az network vnet subnet create \
     --resource-group aks-test-rg \
     --vnet-name test-vnet \
     --name api-server-subnet \
     --address-prefix 10.0.2.0/28 \
     --delegations Microsoft.ContainerService/managedClusters
   
   # Create cluster with API Server VNet Integration
   az aks create \
     --resource-group aks-test-rg \
     --name aks-api-vnet-int \
     --enable-apiserver-vnet-integration \
     --apiserver-subnet-id /subscriptions/.../api-server-subnet \
     --vnet-subnet-id /subscriptions/.../aks-subnet \
     --network-plugin azure
   ```

3. **Add Detection Logic** (2-3 hours)
   - File: `api_server_analyzer.py`
   ```python
   def _detect_api_server_mode(self):
       """Detect API server access mode."""
       profile = self.cluster_data.get('api_server_access_profile', {})
       
       if profile.get('enable_vnet_integration'):
           return 'vnet_integration'
       elif profile.get('enable_private_cluster'):
           return 'private_endpoint'
       else:
           return 'public'
   
   def analyze(self):
       mode = self._detect_api_server_mode()
       
       if mode == 'vnet_integration':
           # Skip private DNS zone checks
           self._validate_delegated_subnet()
           self._check_vnet_integration_nsg()
       elif mode == 'private_endpoint':
           # Existing private endpoint logic
           self._validate_private_dns_zone()
       # ...
   ```
   
   - File: `dns_analyzer.py`
   ```python
   def analyze(self):
       # Skip private DNS checks for VNet integration
       if self.api_server_mode == 'vnet_integration':
           self.add_finding(
               severity=Severity.INFO,
               code=FindingCode.API_VNET_INTEGRATION_DETECTED,
               message="API Server VNet Integration enabled - private DNS zone not required"
           )
           return
       
       # Existing private DNS logic
   ```

4. **Testing** (1 hour)
   - Run diagnostics on VNet integration cluster
   - Verify no false DNS findings
   - Test delegated subnet validation

**Success Criteria:**
- [ ] VNet integration mode detected
- [ ] No false findings about missing private DNS
- [ ] Delegated subnet validated
- [ ] NSG rules for delegated subnet checked
- [ ] Clear distinction from private endpoint mode

</details>

---

### Phase 4 Tasks

<details>
<summary><b>Task 4.1: Cross-Subscription BYO VNet</b></summary>

**Estimated Time:** 2 hours

**Implementation Steps:**

1. **Setup** (30 min)
   - Ensure access to 2 subscriptions
   - Create VNet in Subscription B
   - Configure appropriate permissions

2. **Create Test Cluster** (30 min)
   ```bash
   # Create cluster in Subscription A using VNet from Subscription B
   az aks create \
     --subscription <sub-a-id> \
     --resource-group aks-test-rg \
     --name aks-cross-sub \
     --vnet-subnet-id /subscriptions/<sub-b-id>/resourceGroups/.../subnets/aks-subnet \
     --network-plugin azure
   ```

3. **Run Diagnostics** (30 min)
   ```bash
   az aks net-diagnostics -n aks-cross-sub -g aks-test-rg --details
   ```

4. **Validate & Fix** (30 min)
   - Verify cross-subscription resource retrieval
   - Check permission error handling
   - Fix any issues

**Success Criteria:**
- [ ] Cross-subscription VNet detected
- [ ] Resources retrieved correctly
- [ ] Graceful permission error handling
- [ ] VNet link validation works

</details>

---

## Testing Strategy

### Test Matrix

| Gap | Test Clusters Required | Validation Points |
|-----|----------------------|-------------------|
| Azure CNI Overlay NSG | 1 (existing: aks-demo-overlay) | Pod CIDR detection, NSG rules |
| Node Pool Display | 1 (multi-pool cluster) | Display formatting, pod CIDR |
| User-Assigned NAT Gateway | 1 (new: aks-user-nat) | NAT detection, public IPs |
| AKS LocalDNS | 1 (existing + enable LocalDNS) | DNS test handling |
| Non-VMSS Nodes | 3 (NAP, Virtual Nodes, VM pools) | Data collection, connectivity |
| Network Isolated | 1 (new: outbound=none) | Analysis skips, private ACR |
| BYO Private DNS | 1 (new: BYO DNS zone) | DNS zone detection |
| API VNet Integration | 1 (new: VNet integration) | Mode detection, no false DNS findings |
| Cross-Subscription | 1 (new: cross-sub VNet) | Resource retrieval |

**Total New Test Clusters:** 7 clusters

---

### Test Automation

**Regression Test Suite:**

```bash
#!/bin/bash
# test_all_scenarios.sh

CLUSTERS=(
  "aks-demo-overlay:aks-demo-rg"         # Overlay
  "aks-demo-kubenet:aks-demo-rg"         # Kubenet
  "aks-user-nat:aks-test-rg"             # User NAT Gateway
  "aks-nap:aks-test-rg"                  # NAP
  "aks-virtual-nodes:aks-test-rg"        # Virtual Nodes
  "aks-network-isolated:aks-test-rg"     # Network Isolated
  "aks-byo-dns:aks-test-rg"              # BYO Private DNS
  "aks-api-vnet-int:aks-test-rg"         # API VNet Integration
  "aks-cross-sub:aks-test-rg"            # Cross-Subscription
)

for cluster in "${CLUSTERS[@]}"; do
  IFS=':' read -r name rg <<< "$cluster"
  echo "Testing $name..."
  
  az aks net-diagnostics -n "$name" -g "$rg" --details --probe-test \
    --json-report "test-results/$name-report.json"
  
  if [ $? -eq 0 ]; then
    echo "✅ $name PASSED"
  else
    echo "❌ $name FAILED"
  fi
done
```

---

### Validation Checklist

For each gap closed:

- [ ] **Implementation Complete**
  - [ ] Code changes reviewed
  - [ ] Finding codes added to models
  - [ ] Error handling implemented
  
- [ ] **Testing Complete**
  - [ ] Test cluster created
  - [ ] Diagnostics run successfully
  - [ ] Output verified
  - [ ] Edge cases tested
  
- [ ] **Documentation Updated**
  - [ ] COVERAGE-MATRIX.md updated
  - [ ] ARCHITECTURE.md updated (if needed)
  - [ ] User-facing docs updated
  - [ ] Code comments added
  
- [ ] **Quality Checks**
  - [ ] Pylint score 10.00/10
  - [ ] Flake8 passed
  - [ ] Linter checks passed
  - [ ] No regressions in existing tests

---

## Risk Assessment

### High Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **NAP API Changes** | Non-VMSS support may not work | Research NAP APIs thoroughly, test early |
| **Network Isolated Availability** | Feature may be in preview/limited | Verify feature availability, document limitations |
| **Connectivity Test Methods** | Alternative methods may not exist | Design graceful degradation, document test limitations |
| **Breaking Changes** | Code changes may break existing scenarios | Comprehensive regression testing |

---

### Medium Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Permission Issues** | Cross-subscription tests fail | Document permission requirements clearly |
| **Feature Availability** | Some features region-specific | Test in supported regions, document regional limitations |
| **Timeline Slippage** | Phases take longer than estimated | Build buffer into schedule, prioritize ruthlessly |

---

### Low Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Documentation Gaps** | User confusion | Thorough documentation review |
| **Edge Case Bugs** | Minor issues in production | Comprehensive test coverage |
| **Output Format Changes** | User experience inconsistency | Maintain output format consistency |

---

## Success Criteria

### Phase Completion Criteria

**Phase 1 Success:**
- ✅ 4 gaps closed (Overlay NSG, Node Pool Display, User NAT Gateway, LocalDNS)
- ✅ All tests passing on existing clusters
- ✅ No regressions
- ✅ Documentation updated

**Phase 2 Success:**
- ✅ 2 critical gaps closed (Non-VMSS, Network Isolated)
- ✅ NAP clusters fully supported
- ✅ Network isolated clusters supported
- ✅ Connectivity tests work with alternative methods
- ✅ No tool failures on modern AKS patterns

**Phase 3 Success:**
- ✅ 2 important gaps closed (BYO DNS, API VNet Integration)
- ✅ No false findings for BYO private DNS zones
- ✅ No false findings for API VNet Integration
- ✅ Private cluster scenarios fully validated

**Phase 4 Success:**
- ✅ All identified gaps closed
- ✅ Edge cases validated
- ✅ Comprehensive test coverage
- ✅ Production-ready feature

---

### Overall Success Metrics

| Metric | Target | Current | Post-Implementation |
|--------|--------|---------|-------------------|
| **Scenario Coverage** | 95%+ | ~75% | 95%+ |
| **Critical Gaps** | 0 | 3 | 0 |
| **Test Cluster Support** | All major types | VMSS only | VMSS, NAP, VM, Virtual Nodes |
| **False Findings** | <5% | Unknown | <5% |
| **User Satisfaction** | High | N/A | High |

---

### Production Readiness Criteria

- [ ] **Functionality**
  - [ ] All 9 identified gaps closed
  - [ ] Comprehensive scenario coverage
  - [ ] Graceful degradation for unsupported scenarios
  
- [ ] **Quality**
  - [ ] Pylint score 10.00/10
  - [ ] Zero linter violations
  - [ ] 100% test pass rate
  - [ ] No known critical bugs
  
- [ ] **Documentation**
  - [ ] User guide complete
  - [ ] Scenario examples provided
  - [ ] Troubleshooting guide
  - [ ] API documentation
  
- [ ] **Performance**
  - [ ] <60s for basic analysis
  - [ ] <5min with --probe-test
  - [ ] Acceptable for large clusters (>100 nodes)
  
- [ ] **UX**
  - [ ] Clear, actionable findings
  - [ ] Consistent output format
  - [ ] Helpful error messages
  - [ ] Permission limitations clearly communicated

---

## Next Steps

### Immediate Actions

1. **Review & Approve Plan**
   - Stakeholder review of gap closure plan
   - Confirm priorities and timeline
   - Allocate resources

2. **Phase 1 Kickoff**
   - Begin with quick wins (8-12 hours)
   - Build momentum with easy gaps
   - Validate approach

3. **Test Infrastructure Setup**
   - Create required test clusters
   - Document cluster configurations
   - Setup automation scripts

### Decision Points

**After Phase 1 (Week 1):**
- ✅ Quick wins validated
- ✅ Approach confirmed
- 🔍 **DECIDE:** Proceed to Phase 2 (critical gaps)?

**After Phase 2 (Week 2-3):**
- ✅ Critical gaps closed
- ✅ Modern AKS patterns supported
- 🔍 **DECIDE:** Production release or continue to Phase 3?

**After Phase 3 (Week 3-4):**
- ✅ Important scenarios validated
- ✅ False findings eliminated
- 🔍 **DECIDE:** Production release or complete Phase 4?

**After Phase 4 (Week 4-5):**
- ✅ All gaps closed
- ✅ Comprehensive coverage
- 🔍 **DECIDE:** Production release

---

## Timeline

### Proposed Schedule

**Week 1: Phase 1 - Quick Wins**
- Day 1-2: Azure CNI Overlay NSG + Node Pool Display
- Day 2-3: User-Assigned NAT Gateway + LocalDNS

**Week 2-3: Phase 2 - Critical Infrastructure**
- Day 1-3: Non-VMSS Node Support (10-14 hours)
- Day 4-5: Network Isolated Clusters (6-10 hours)

**Week 3-4: Phase 3 - Configuration Validation**
- Day 1: BYO Private DNS Zone (2 hours)
- Day 2-3: API Server VNet Integration (4-6 hours)

**Week 4-5: Phase 4 - Edge Cases** (Optional)
- Day 1: Cross-Subscription VNet (2 hours)
- Day 1: Cilium Validation (1-2 hours)

**Week 5: Final Validation & Documentation**
- Regression testing
- Documentation finalization
- Production readiness review

---

## Appendix

### Reference Documents

- [COVERAGE-MATRIX.md](./COVERAGE-MATRIX.md) - Detailed gap analysis
- [DEMO-SUMMARY.md](./DEMO-SUMMARY.md) - POC summary and gaps
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture documentation

### Azure Documentation Links

- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Network Isolated Clusters](https://learn.microsoft.com/en-us/azure/aks/concepts-network-isolated)
- [API Server VNet Integration](https://learn.microsoft.com/en-us/azure/aks/api-server-vnet-integration)
- [BYO Private DNS Zone](https://learn.microsoft.com/en-us/azure/aks/private-clusters)
- [LocalDNS Configuration](https://learn.microsoft.com/en-us/azure/aks/localdns-custom)
- [Node Auto-Provisioning](https://learn.microsoft.com/en-us/azure/aks/node-autoprovision)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 10, 2025  
**Next Review:** After Phase 1 completion
