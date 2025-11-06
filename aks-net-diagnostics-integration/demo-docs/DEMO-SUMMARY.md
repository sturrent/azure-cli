# AKS Net-Diagnostics POC - Quick Demo Summary

**Meeting Date:** November 6, 2025  
**Document:** Quick reference for demo  
**Full Details:** See [DEMO-SCENARIOS.md](./DEMO-SCENARIOS.md)

---

## What We Built

A network diagnostics tool integrated into Azure CLI as `az aks net-diagnostics` that analyzes AKS cluster network configurations and identifies misconfigurations.

**Command:**
```bash
az aks net-diagnostics -n <cluster> -g <resource-group> [--details] [--probe-test] [--json-report <file>]
```

---

## What It Checks

### ✅ Currently Working

1. **Network Plugin Detection:** Azure CNI, Kubenet, Azure CNI Overlay, Azure CNI Pod Subnet
2. **NSG Rules:** Required AKS rules (MCR, Azure Cloud, DNS, NTP, inter-node)
3. **Outbound Connectivity:** LoadBalancer, UDR, NAT Gateway analysis
4. **Private Clusters:** Private DNS, VNet links, private endpoints
5. **API Server Access:** Authorized IP ranges, UDR conflicts
6. **DNS Configuration:** Custom DNS, private DNS zones
7. **Connectivity Tests:** Active probing (--probe-test flag)
8. **Multiple Node Pools:** Data collected and analyzed
9. **Permission Handling:** Graceful degradation with clear messages

---

## Critical Gaps Identified

### 1. ❌ Azure CNI Overlay NSG Rules (HIGH PRIORITY)

**Issue:** Tool doesn't check pod CIDR traffic rules required by Azure CNI Overlay

**Impact:** May miss overlay-specific misconfigurations

**Reference:** https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay?tabs=kubectl#network-security-groups

**Note:** Azure CNI Overlay has **no encapsulation** - NSG rules must allow:
- Node CIDR to Pod CIDR traffic (service routing)
- Pod CIDR to Pod CIDR traffic (pod-to-pod, DNS)

**Effort:** 2-3 hours to implement

---

### 2. ❌ Non-VMSS Node Support (HIGH PRIORITY)

**Issue:** Tool assumes VMSS-based nodes, doesn't support:
- Node Auto-Provisioning (NAP)
- Virtual Nodes (ACI)
- Virtual Machines node pools

**Impact:** Tool fails on modern AKS deployment patterns

**Current Behavior:** Returns empty VMSS list, analysis incomplete

**Effort:** 8-12 hours to implement alternative data collection

---

### 3. 📋 Node Pool Display (MEDIUM PRIORITY - Phase 8 Planned)

**Issue:** Multiple node pools detected but details not shown in output

**Impact:** Reduced visibility for multi-pool clusters

**Status:** Design complete, ready to implement

**Effort:** 2-3 hours

---

### 4. ❌ BYO Private DNS Zone (HIGH PRIORITY)

**Issue:** NOT tested - private DNS zone created before cluster

**Feature:** [Create a private AKS cluster with a custom private DNS zone or private DNS subzone](https://learn.microsoft.com/en-us/azure/aks/private-clusters?tabs=default-basic-networking%2Cportal%2Cazure-portal#create-a-private-aks-cluster-with-a-custom-private-dns-zone-or-private-dns-subzone)

**Test Gaps:**
- BYO private DNS zone scenarios not tested
- Resource group location (user RG vs node RG)
- Cross-subscription private DNS zone scenarios
- Custom DNS zone name validation

**Impact:** Unknown behavior, may generate false findings

**Effort:** 2 hours (create test cluster + validate)

---

### 5. ❌ API Server VNet Integration (HIGH PRIORITY)

**Issue:** NOT tested - no test cluster created

**Feature:** [AKS API Server VNet Integration](https://learn.microsoft.com/en-us/azure/aks/api-server-vnet-integration)

**What It Is:**
- API server injected directly into customer VNet (delegated subnet)
- No private endpoint needed
- API server accessible from VNet without private DNS zone

**Test Gaps:**
- No test cluster with API Server VNet Integration created
- May not distinguish between private endpoint vs VNet integration mode
- Tool likely generates false findings about missing private DNS zone
- Delegated subnet and NSG requirements not validated

**Impact:** Tool may produce incorrect warnings for VNet integration clusters

**Effort:** 4-6 hours (create test cluster + add detection logic)

---

### 6. ⚠️ Cross-Subscription BYO VNet (MEDIUM PRIORITY)

**Issue:** Code supports it but not formally tested

**Scenario:** Cluster in Subscription A, VNet in Subscription B

**Test Needed:** Create and validate cross-subscription setup

**Effort:** 2 hours

---

### 7. ❌ Network Isolated Clusters (HIGH PRIORITY)

**Issue:** NOT tested - clusters with outbound type `none` or `block` (preview)

**Feature:** [Network Isolated AKS Clusters](https://learn.microsoft.com/en-us/azure/aks/concepts-network-isolated)

**What It Is:**
- **Bootstrap Artifact Source**: `Cache` - Uses private ACR instead of public Microsoft Artifact Registry (MAR)
- **Outbound Type**: `none` or `block` - Blocks/restricts all egress traffic
- **Purpose**: Zero-trust networking, data exfiltration prevention

**Test Gaps:**
- Tool expects outbound types: `loadBalancer`, `userDefinedRouting`, `managedNATGateway`
- No test cluster with `--outbound-type none` or `block` created
- Private ACR bootstrap detection not implemented
- Connectivity tests assume public MCR access (will fail)

**Impact:** Tool likely fails or produces incorrect analysis for network isolated clusters

**Effort:** 12-16 hours (requires significant outbound and connectivity analysis changes)

---

### 8. ⚠️ User-Assigned NAT Gateway (LOW PRIORITY)

**Issue:** NOT tested - BYO NAT Gateway (`userAssignedNATGateway`)

**What It Is:**
- User creates NAT Gateway before cluster creation
- NAT Gateway attached to subnet before AKS deployment
- User manages NAT Gateway (vs AKS-managed `managedNATGateway`)

**Test Gaps:**
- Only tested AKS-managed NAT Gateway (`managedNATGateway`)
- User-assigned NAT Gateway detection not validated
- Subnet-attached NAT Gateway scenarios not tested

**Impact:** Unknown behavior - tool likely works but not validated

**Effort:** 1-2 hours (create test cluster + validate)

---

### 9. ⚠️ AKS LocalDNS (MEDIUM PRIORITY)

**Issue:** NOT tested - LocalDNS preview feature (Kubernetes 1.31+)

**Feature:** [Configure LocalDNS in AKS](https://learn.microsoft.com/en-us/azure/aks/localdns-custom)

**What It Is:**
- **Node-level DNS caching** - systemd service on each node (169.254.10.10/11)
- Configured per node pool with JSON config file
- Sits between pods and CoreDNS, reducing latency

**Test Gaps:**
- No test cluster with LocalDNS enabled
- DNS connectivity tests may report unexpected nameserver addresses
- Tool may misinterpret DNS resolution path (LocalDNS → CoreDNS)

**Impact:** DNS connectivity tests may produce unexpected results or incorrect analysis

**Effort:** 2-3 hours (enable LocalDNS on test cluster + validate DNS tests)

---

## Sample Output Highlights

### Successful Analysis
```
=== AKS Network Diagnostics Summary ===
Cluster: aks-demo-overlay (aks-demo-rg)
Network Plugin: azure (overlay mode)
Outbound Type: loadBalancer

**Findings Summary:**
- [OK] No critical issues detected

**Network Topology:**
- VNet: aks-vnet (10.0.0.0/16)
  - Subnet: aks-subnet (10.0.1.0/24)

**Outbound Configuration:**
- Type: loadBalancer
- Outbound IPs: 20.151.23.45
```

### With Permission Limitations
```
**Findings Summary:**
- [OK] No critical issues detected in analyzed components
- [WARNING] Analysis incomplete - see Permission Limitations below

**Permission Limitations:**
- Incomplete VMSS Analysis - Missing permission to read MC_*
  Recommendation: Grant 'Reader' role or assign 
    Microsoft.Compute/virtualMachineScaleSets/read permission
```

### With Findings
```
**Findings Summary:**
- [ERROR] UDR + API Authorized IPs Conflict - Route table may redirect traffic
- [WARNING] Custom DNS Server Unreachable - DNS server 10.0.1.4 may not resolve private DNS zones

**Recommendations:**
1. Review route table configuration for API server access
2. Ensure custom DNS can forward to Azure DNS (168.63.129.16)
```

---

## Enhancement Priority Recommendations

### Tier 1: High Impact, Low Effort (7-11 hours)
1. ✅ Azure CNI Overlay NSG rules (2-3 hours)
2. ✅ Phase 8: Pod CIDR & Node Pool display (2-3 hours)
3. ✅ AKS LocalDNS validation (2-3 hours)
4. ✅ User-Assigned NAT Gateway validation (1-2 hours)

### Tier 2: High Impact, Medium Effort (6-8 hours)
5. ❌ BYO Private DNS Zone validation (2 hours)
6. ❌ API Server VNet Integration validation (4-6 hours)

### Tier 3: High Impact, High Effort (20-28 hours)
7. ⚠️ Network Isolated Clusters support (12-16 hours)
8. ⚠️ Non-VMSS node support (8-12 hours)

### Tier 4: Lower Priority (3-4 hours)
9. 📋 Cross-subscription testing (2 hours)
10. 📋 Cilium validation (1-2 hours)

---

## Next Steps

Based on feedback, determine:

1. **Release timeline** - Build a new submodule vs continue working on this one
2. **Gap prioritization** - Which gaps are blockers vs nice-to-have
3. **Resource allocation** - Who can help review and validate
4. **Validation needs** - Additional testing scenarios
5. **Documentation** - User-facing docs and examples

---

**Quick Reference Documents:**
- Full Analysis: [DEMO-SCENARIOS.md](./DEMO-SCENARIOS.md)
- Architecture: [ARCHITECTURE.md](../ARCHITECTURE.md)
- Test Results: [progress/PHASE6-COMPLETION.md](../progress/PHASE6-COMPLETION.md)
- Permission Handling: [progress/PHASE7-PROGRESS.md](../progress/PHASE7-PROGRESS.md)
