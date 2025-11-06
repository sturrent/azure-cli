# AKS Net-Diagnostics - Scenario Coverage Matrix
  
**Visual Reference:** Current support vs gaps

---

## Legend

- ✅ **Fully Supported & Tested**
- ⚠️ **Supported but Not Fully Validated**
- 📋 **Planned Enhancement**
- ❌ **Not Supported (Gap)**

---

## Network Plugin Support Matrix

| Network Plugin | Status | Notes |
|---------------|--------|-------|
| Azure CNI | ✅ | Fully tested |
| Azure CNI (Overlay) | ✅ | Tested, but pod CIDR NSG rules not checked ❌ |
| Azure CNI (Pod Subnet) | ✅ | Tested, but Pod CIDR not displayed 📋 |
| Kubenet | ✅ | Fully tested |
| Azure CNI (Cilium) | ⚠️ | Code should work, not tested |
| BYO CNI | ❌ | Not tested |

---

## Outbound Type Support Matrix

| Outbound Type | Status | Capabilities |
|--------------|--------|-------------|
| Load Balancer | ✅ | Public IP detection, outbound rules, effective IPs |
| User Defined Routing (UDR) | ✅ | Route table analysis, next hop validation, UDR conflicts |
| Managed NAT Gateway (`managedNATGateway`) | ✅ | NAT Gateway detection, public IPs, UDR override detection |
| User-Assigned NAT Gateway (`userAssignedNATGateway`) | ⚠️ | **NOT Tested** - BYO NAT Gateway, user-managed |
| Network Isolated (`none`) | ❌ | **NOT Tested** - Zero egress, private ACR bootstrap |
| Network Isolated (`block`) | ❌ | **NOT Tested** - Actively blocks egress (preview) |

**Gaps:** User-assigned NAT Gateway not validated, Network Isolated outbound types not supported

---

## Cluster Configuration Support

| Configuration | Status | Notes |
|--------------|--------|-------|
| Public Cluster | ✅ | Fully supported |
| Private Cluster (Standard) | ✅ | Private DNS zone, VNet links validated |
| Private Cluster (BYO Private DNS Zone) | ❌ | **NOT Tested** - User-provided DNS zone |
| Private Cluster (API VNet Integration) | ❌ | **NOT Tested** - May generate false findings |
| Authorized IP Ranges | ✅ | Detection, conflict analysis, validation |
| Multiple Node Pools | ✅ | Data collected, display pending 📋 |
| Single Node Pool | ✅ | Fully supported |

---

## VNet Topology Support

| Topology | Status | Notes |
|----------|--------|-------|
| AKS-Managed VNet | ✅ | Default scenario, fully tested |
| BYO VNet (Same Subscription) | ✅ | Fully tested |
| BYO VNet (Cross-Subscription) | ⚠️ | Code supports, not tested |
| Hub-Spoke | ✅ | Virtual appliance routing tested |
| VNet Peering | ✅ | Detection and analysis |

---

## Node Infrastructure Support

| Infrastructure | Status | Critical Gap? |
|---------------|--------|--------------|
| VMSS (Standard) | ✅ | Primary support |
| Virtual Machines node pools | ❌ | **YES** - New AKS feature |
| Node Auto-Provisioning (NAP) | ❌ | **YES** - Growing adoption |
| Virtual Nodes (ACI) | ❌ | Moderate - Limited use |
| Manual VM Nodes | ❌ | Low - Rare scenario |

**Impact:** Tool completely fails on non-VMSS deployments

---

## NSG Analysis Coverage

| Check Type | Status | Details |
|-----------|--------|---------|
| Required Outbound Rules | ✅ | MCR, Azure Cloud, DNS, NTP |
| Required Inbound Rules | ✅ | Inter-node, Load Balancer probes |
| Azure CNI Overlay Pod CIDR | ❌ | **Pod CIDR traffic rules not checked** |
| Blocking Rule Detection | ✅ | Priority-based analysis |
| Service Tag Validation | ✅ | Proper service tag semantics |
| Inter-Node Communication | ✅ | Port 10250, etc. |

---

## DNS Analysis Coverage

| DNS Configuration | Status | Capabilities |
|------------------|--------|-------------|
| Azure Default DNS | ✅ | Detection and validation |
| Custom DNS Servers | ✅ | Reachability warnings |
| Private DNS Zones | ✅ | Zone detection, VNet links |
| Custom DNS + Private Zone | ✅ | Compatibility warnings |
| AKS LocalDNS (Preview) | ⚠️ | **NOT Tested** - Node-level DNS caching (169.254.10.10/11) |

**Gap:** LocalDNS feature not tested - may affect node OS DNS resolution in connectivity tests

---

## API Server Access Analysis

| Check Type | Status | Details |
|-----------|--------|---------|
| Authorized IP Ranges | ✅ | Detection and validation |
| UDR + Authorized IP Conflicts | ✅ | Critical misconfiguration detection |
| Client IP Authorization | ✅ | Current client validation |
| Outbound IP Authorization | ✅ | Cluster IP validation |
| Private Endpoint | ✅ | Detection and analysis |
| API Server VNet Integration | ❌ | **NOT Tested** - May incorrectly report missing private DNS zone |

**Gap:** API Server VNet Integration not tested - tool may generate false findings (expects private DNS zone that doesn't exist with VNet integration)

---

## Connectivity Testing (--probe-test)

| Test Type | Status | Requirements |
|----------|--------|-------------|
| MCR DNS Resolution | ✅ | VMSS instances required ❌ |
| MCR HTTPS Connectivity | ✅ | VMSS instances required ❌ |
| API Server DNS | ✅ | VMSS instances required ❌ |
| API Server HTTPS | ✅ | VMSS instances required ❌ |
| Custom Endpoints | ❌ | Not supported |

**Limitation:** All tests require VMSS run-command (fails on NAP/Virtual Nodes)

---

## Permission Handling

| Scenario | Status | User Experience |
|----------|--------|----------------|
| Full Permissions | ✅ | Complete analysis |
| Missing VNet Read | ✅ | Graceful degradation + warning |
| Missing VMSS Read | ✅ | Graceful degradation + warning |
| Missing LoadBalancer Read | ✅ | Graceful degradation + warning |
| Missing All Permissions | ✅ | Clear error messages |
| Cross-Subscription Permissions | ⚠️ | Code supports, not tested |

---

## Output Formats

| Format | Status | Notes |
|--------|--------|-------|
| Console (Summary) | ✅ | Default output |
| Console (Detailed) | ✅ | --details flag |
| JSON Report | ✅ | --json-report flag |
| Table Format | ❌ | POC deferred (--output table) |
| YAML Format | ❌ | POC deferred (--output yaml) |
| TSV Format | ❌ | POC deferred (--output tsv) |

**POC Decision:** Keep existing rich text output, defer Azure CLI standard formats

---

## Scenario Test Coverage

### High Priority Scenarios (All Tested ✅)

1. ✅ **Basic Public Cluster** - Azure CNI + LoadBalancer
2. ✅ **Private Cluster** - Private DNS + VNet links
3. ✅ **UDR with Firewall** - Virtual appliance routing
4. ✅ **NAT Gateway** - Managed NAT Gateway outbound
5. ✅ **Authorized IP Ranges** - API access restrictions
6. ✅ **Multiple Node Pools** - Multi-pool clusters
7. ✅ **Hub-Spoke Topology** - Customer VNet with UDR
8. ✅ **Limited Permissions** - Service principal auth

### Medium Priority Scenarios

9. 📋 **Pod Subnet Display** - Data collected, not shown (Phase 8)
10. ⚠️ **Cross-Subscription BYO VNet** - Code supports, not tested

### Gap Scenarios (Not Supported ❌)

11. ❌ **BYO Private DNS Zone** - **High Priority Gap** - NOT tested
12. ❌ **API Server VNet Integration** - **High Priority Gap** - NOT tested, may have false findings
13. ❌ **Network Isolated Clusters** - **High Priority Gap** - Outbound type `none`/`block` not supported
14. ⚠️ **User-Assigned NAT Gateway** - **Low Priority Gap** - BYO NAT Gateway not tested
15. ⚠️ **AKS LocalDNS** - **Medium Priority Gap** - DNS caching (169.254.10.10/11) not tested
16. ❌ **Node Auto-Provisioning (NAP)** - **Critical Gap** - Tool fails
17. ❌ **Virtual Nodes (ACI)** - Growing adoption
18. ❌ **Virtual Machines node pools** - New AKS feature
19. ❌ **Azure CNI Overlay Pod CIDR NSG Check** - **Important Gap**

---

## Feature Completeness by Category

### Network Analysis: 90% Complete

- ✅ VNet topology
- ✅ Subnet analysis
- ✅ VNet peering
- ✅ Route tables
- ✅ NSGs (except Overlay-specific)
- 📋 Pod CIDR display

### Cluster Analysis: 85% Complete

- ✅ Cluster info
- ✅ Agent pools
- ✅ Network plugin detection
- ✅ Outbound type
- 📋 Node pool display details
- ❌ Non-VMSS support

### Security Analysis: 95% Complete

- ✅ NSG rules (generic)
- ✅ API access
- ✅ Authorized IPs
- ✅ Private clusters
- ❌ Overlay-specific NSG rules
- ❌ API Server VNet Integration (not tested)

### DNS Analysis: 95% Complete

- ✅ DNS configuration
- ✅ Private DNS zones
- ✅ VNet links
- ✅ Custom DNS servers
- ⚠️ LocalDNS feature (not tested)

### Connectivity Analysis: 75% Complete

- ✅ Active testing (--probe-test)
- ✅ MCR connectivity
- ✅ API server connectivity
- ❌ NAP/Virtual Nodes support
- ❌ Custom endpoint testing

### UX & Reporting: 90% Complete

- ✅ Summary report
- ✅ Detailed report
- ✅ JSON export
- ✅ Permission handling
- 📋 Node pool display
- ❌ Azure CLI standard output formats

---

## Priority Gap Analysis

### Critical Gaps (Block Adoption)

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| Non-VMSS Support (NAP) | HIGH - Tool fails completely | 8-12h | 🔴 CRITICAL |
| Azure CNI Overlay NSG | MEDIUM - Missing validation | 2-3h | 🟡 HIGH |

### Important Gaps (Limit Functionality)

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| Network Isolated Clusters | HIGH - Tool fails for `none`/`block` outbound | 12-16h | 🔴 HIGH |
| Node Pool Display | MEDIUM - Reduced visibility | 2-3h | 🟡 MEDIUM |
| BYO Private DNS Zone | MEDIUM - Specific scenario | 2h | 🟡 MEDIUM |
| API VNet Integration | MEDIUM - Specific scenario | 4-6h | 🟡 MEDIUM |
| Cross-Sub Validation | LOW - Edge case | 2h | 🟢 LOW |

### Nice-to-Have

| Enhancement | Impact | Effort | Priority |
|------------|--------|--------|----------|
| Cilium Validation | LOW - Rare use case | 1-2h | 🔵 FUTURE |
| Standard Output Formats | LOW - POC acceptable | 6-8h | 🔵 FUTURE |
| Virtual Machines Node Pools | LOW - New feature, limited adoption | 4-6h | 🔵 FUTURE |

---

## Conclusion

**POC Status:** Strong foundation with identified gaps

**Strengths:**
- Core network analysis complete and validated
- Permission handling robust
- Performance excellent
- Output informative

**Work pending:**
- Need to address the gaps and do extensive testing
- Non-VMSS support (NAP adoption growing?)
- Azure CNI Overlay NSG gap (easy fix)

---

**Reference Documents:**
- Detailed Scenarios: [DEMO-SCENARIOS.md](./DEMO-SCENARIOS.md)
- Quick Summary: [DEMO-SUMMARY.md](./DEMO-SUMMARY.md)
- Architecture: [ARCHITECTURE.md](../ARCHITECTURE.md)
