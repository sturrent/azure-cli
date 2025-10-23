# Phase 8: Pod CIDR Enhancement & Node Pool Display

**Created:** October 23, 2025  
**Status:** Planning  
**Priority:** Medium  
**Dependencies:** Phase 7 Complete

---

## Overview

Phase 8 enhances the diagnostic tool to properly handle all Azure CNI networking variants and display comprehensive node pool information. This phase addresses a gap discovered during testing where Azure CNI pod subnet configurations show empty pod CIDR information.

---

## Problem Statement

### Current Behavior

The tool currently displays pod CIDR by reading `networkProfile.podCidr`:

```python
print(f"- **Pod CIDR:** {network_profile.get('pod_cidr', '')}")
```

This works for:
- ✅ **Kubenet**: `podCidr` is populated (e.g., `10.244.0.0/16`)
- ✅ **Azure CNI Overlay**: `podCidr` is populated (e.g., `10.244.0.0/16`)

But fails for:
- ❌ **Azure CNI Pod Subnet**: `podCidr` is `null`, actual data is in `agentPoolProfiles[].podSubnetId`
- ⚠️ **Azure CNI Node Subnet (Legacy)**: `podCidr` is `null`, no pod CIDR exists (pods use node subnet)

### Test Results

**aks-overlay (Azure CNI Overlay):**
```json
{
  "networkPlugin": "azure",
  "networkPluginMode": "overlay",
  "podCidr": "10.244.0.0/16",
  "podCidrs": ["10.244.0.0/16"]
}
```
Agent pools: `podSubnetId: null` ✅

**aks-acni-podsubnet (Azure CNI Pod Subnet):**
```json
{
  "networkPlugin": "azure",
  "networkPluginMode": null,
  "podCidr": null,
  "podCidrs": null
}
```
Agent pools:
```json
[
  {
    "name": "nodepool1",
    "podSubnetId": ".../subnets/podsubnet",     // 10.241.0.0/16
    "vnetSubnetId": ".../subnets/nodesubnet"    // 10.240.0.0/16
  },
  {
    "name": "npool2",
    "podSubnetId": ".../subnets/pod2subnet",    // 10.243.0.0/16
    "vnetSubnetId": ".../subnets/node2subnet"   // 10.242.0.0/16
  }
]
```
❌ Currently shows: `Pod CIDR: ` (empty)

---

## Azure CNI Networking Variants

### 1. Azure CNI Node Subnet (Legacy)

**Configuration:**
- `networkPlugin`: `azure`
- `networkPluginMode`: `null`
- `podCidr`: `null`
- `podSubnetId`: `null`

**Behavior:**
- Nodes and pods share the same VNet subnet
- Pods get IPs directly from the node subnet
- No separate pod CIDR exists
- IP exhaustion risk (nodes and pods compete for IPs)

**Expected Display:**
```
- **Pod CIDR:** N/A - Pods use node subnet (legacy Azure CNI configuration)
```

---

### 2. Azure CNI Overlay

**Configuration:**
- `networkPlugin`: `azure`
- `networkPluginMode`: `overlay`
- `podCidr`: `10.244.0.0/16` (cluster-level)
- `podSubnetId`: `null`

**Behavior:**
- Nodes get IPs from VNet subnet
- Pods use overlay network (similar to kubenet but with Azure CNI)
- Cluster-wide pod CIDR defined at network profile level
- No per-pool pod subnets

**Expected Display:**
```
- **Pod CIDR:** 10.244.0.0/16
```

**Status:** ✅ Already working correctly

---

### 3. Azure CNI Pod Subnet (Dynamic IP Allocation)

**Configuration:**
- `networkPlugin`: `azure`
- `networkPluginMode`: `null`
- `podCidr`: `null`
- `podSubnetId`: Per-pool subnet resource ID

**Behavior:**
- Nodes get IPs from node subnet (`vnetSubnetId`)
- Pods get IPs from dedicated pod subnet (`podSubnetId`)
- Each node pool can have a different pod subnet
- Best practice for scaling and IP management

**Expected Display (Summary):**
```
- **Pod Subnets:** 10.241.0.0/16, 10.243.0.0/16
  (Per-pool pod subnets - see Node Pools section for details)
```

**Expected Display (Detailed - in Node Pools section):**
```
### Node Pools

🔧 **aks-nodepool1-05223296-vmss** (System Pool)
  - Node Subnet: 10.240.0.0/16 (nodesubnet)
  - Pod Subnet: 10.241.0.0/16 (podsubnet)
  ...

👤 **aks-npool2-37114648-vmss** (User Pool)
  - Node Subnet: 10.242.0.0/16 (node2subnet)
  - Pod Subnet: 10.243.0.0/16 (pod2subnet)
  ...
```

**Status:** ❌ Currently shows empty, needs implementation

---

## Detection Logic

### Pseudocode for Variant Detection

```python
def detect_azure_cni_variant(cluster_info, agent_pools):
    """
    Detect which Azure CNI variant is being used.
    
    Returns:
        variant: 'node-subnet' | 'overlay' | 'pod-subnet'
        pod_cidrs: list of CIDRs or None
    """
    network_profile = cluster_info.get('network_profile', {})
    network_plugin = network_profile.get('network_plugin')
    
    if network_plugin != 'azure':
        # Not Azure CNI, handle separately (kubenet, etc.)
        return None, None
    
    # Check for overlay mode
    if network_profile.get('network_plugin_mode') == 'overlay':
        pod_cidr = network_profile.get('pod_cidr')
        return 'overlay', [pod_cidr] if pod_cidr else []
    
    # Check if any pool has podSubnetId
    has_pod_subnet = any(
        pool.get('pod_subnet_id') for pool in agent_pools
    )
    
    if has_pod_subnet:
        # Azure CNI Pod Subnet - need to fetch subnet CIDRs
        return 'pod-subnet', None  # CIDRs fetched separately
    else:
        # Legacy Azure CNI Node Subnet
        return 'node-subnet', None
```

---

## Implementation Plan

### 8.1: Pod CIDR Detection Enhancement

#### File: `cluster_data_collector.py`

**New Method: `_get_pod_subnet_cidrs()`**

```python
def _get_pod_subnet_cidrs(
    self,
    agent_pools: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Fetch pod subnet CIDRs for agent pools with podSubnetId.
    
    Args:
        agent_pools: List of agent pool configurations
        
    Returns:
        Dictionary mapping pool name to pod subnet CIDR
        Example: {'nodepool1': '10.241.0.0/16', 'npool2': '10.243.0.0/16'}
    """
    pod_subnet_cidrs = {}
    
    for pool in agent_pools:
        pod_subnet_id = pool.get('pod_subnet_id')
        if not pod_subnet_id:
            continue
            
        pool_name = pool.get('name', 'unknown')
        
        try:
            # Parse subnet ID
            # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/
            #         Microsoft.Network/virtualNetworks/{vnet}/subnets/{subnet}
            subnet_parts = pod_subnet_id.split('/')
            resource_group = subnet_parts[4]
            vnet_name = subnet_parts[8]
            subnet_name = subnet_parts[10]
            
            # Fetch subnet details
            subnet = self.network_client.subnets.get(
                resource_group_name=resource_group,
                virtual_network_name=vnet_name,
                subnet_name=subnet_name
            )
            
            cidr = subnet.address_prefix
            pod_subnet_cidrs[pool_name] = cidr
            
            self.logger.info(
                f"Retrieved pod subnet CIDR for pool '{pool_name}': {cidr}"
            )
            
        except HttpResponseError as e:
            # Check for authorization error
            is_auth_error = self._check_authorization_error(
                e,
                resource_type="Pod Subnet",
                resource_name=subnet_name,
                resource_group=resource_group
            )
            
            if is_auth_error:
                pod_subnet_cidrs[pool_name] = "Permission Denied"
            else:
                self.logger.warning(
                    f"Failed to retrieve pod subnet for pool '{pool_name}': {e}"
                )
                pod_subnet_cidrs[pool_name] = "Error"
                
        except Exception as e:
            self.logger.error(
                f"Unexpected error getting pod subnet for '{pool_name}': {e}"
            )
            pod_subnet_cidrs[pool_name] = "Error"
    
    return pod_subnet_cidrs
```

**Integration in `collect_cluster_info()` or separate method called from orchestrator**

---

#### File: `report_generator.py`

**Enhanced Pod CIDR Display Method:**

```python
def _print_pod_cidr_info(self):
    """
    Display pod CIDR information based on networking variant.
    Handles: Kubenet, Azure CNI Overlay, Azure CNI Pod Subnet, Legacy Azure CNI.
    """
    network_profile = self.cluster_info.get("network_profile", {})
    network_plugin = network_profile.get("network_plugin")
    network_plugin_mode = network_profile.get("network_plugin_mode")
    pod_cidr = network_profile.get("pod_cidr")
    
    # Kubenet or Azure CNI Overlay - use cluster-level podCidr
    if pod_cidr:
        print(f"- **Pod CIDR:** {pod_cidr}")
        return
    
    # Azure CNI specific variants
    if network_plugin == "azure":
        # Check if we have per-pool pod subnets
        pod_subnet_cidrs = self.pod_subnet_cidrs  # From orchestrator/collector
        
        if pod_subnet_cidrs:
            # Azure CNI Pod Subnet
            cidrs = ", ".join(pod_subnet_cidrs.values())
            print(f"- **Pod Subnets:** {cidrs}")
            print("  (Per-pool pod subnets - see Node Pools section for details)")
        else:
            # Legacy Azure CNI Node Subnet
            print("- **Pod CIDR:** N/A - Pods use node subnet (legacy Azure CNI configuration)")
    else:
        # Other network plugins or no pod CIDR configured
        print(f"- **Pod CIDR:** {pod_cidr or 'Not configured'}")
```

---

### 8.2: Node Pool Display

#### File: `report_generator.py`

**New Method: `_print_node_pools()`**

```python
def _print_node_pools(self):
    """
    Display detailed node pool information in detailed report.
    Shows: mode, count, VM size, OS, state, node/pod subnets, zones, etc.
    """
    agent_pools = self.cluster_info.get("agent_pool_profiles", [])
    
    if not agent_pools:
        print("\n### Node Pools")
        print("No agent pool information available.")
        return
    
    print("\n### Node Pools")
    print()
    
    for pool in agent_pools:
        pool_name = pool.get("name", "unknown")
        mode = pool.get("mode", "Unknown")
        count = pool.get("count", "Unknown")
        vm_size = pool.get("vm_size", "Unknown")
        os_type = pool.get("os_type", "Linux")
        provisioning_state = pool.get("provisioning_state", "Unknown")
        
        # Icon based on mode
        icon = "🔧" if mode == "System" else "👤"
        
        # VMSS name if available (from self.vmss_info)
        vmss_name = self._get_vmss_name_for_pool(pool_name)
        display_name = vmss_name if vmss_name else pool_name
        
        print(f"{icon} **{display_name}** ({mode} Pool)")
        print(f"  - Mode: {mode}")
        print(f"  - Node Count: {count}")
        print(f"  - VM Size: {vm_size}")
        print(f"  - OS Type: {os_type}")
        print(f"  - State: {provisioning_state}")
        
        # Node subnet
        node_subnet_id = pool.get("vnet_subnet_id")
        if node_subnet_id:
            node_subnet_info = self._get_subnet_info(node_subnet_id)
            print(f"  - Node Subnet: {node_subnet_info}")
        
        # Pod subnet (if exists)
        pod_subnet_id = pool.get("pod_subnet_id")
        if pod_subnet_id:
            pod_subnet_info = self._get_subnet_info(pod_subnet_id)
            print(f"  - Pod Subnet: {pod_subnet_info}")
        
        # Max pods per node
        max_pods = pool.get("max_pods")
        if max_pods:
            print(f"  - Max Pods/Node: {max_pods}")
        
        # Availability zones
        zones = pool.get("availability_zones", [])
        if zones:
            zones_str = ", ".join(str(z) for z in zones)
            print(f"  - Availability Zones: {zones_str}")
        
        print()

def _get_subnet_info(self, subnet_id: str) -> str:
    """
    Get formatted subnet information (CIDR and name).
    
    Args:
        subnet_id: Full Azure resource ID of subnet
        
    Returns:
        Formatted string like "10.240.0.0/16 (nodesubnet)"
    """
    if not subnet_id:
        return "Not configured"
    
    # Extract subnet name from resource ID
    subnet_name = subnet_id.split('/')[-1]
    
    # Check if we have CIDR from collector
    # Option 1: From self.pod_subnet_cidrs (for pod subnets)
    # Option 2: Fetch on-demand (cache to avoid duplicates)
    
    # For now, use cached data if available
    # If this is a pod subnet, check pod_subnet_cidrs
    # If this is a node subnet, we could have node_subnet_cidrs too
    
    # Simple version: just show name
    # Enhanced version: show CIDR + name
    
    # If we have the CIDR cached:
    if hasattr(self, 'subnet_cidrs') and subnet_id in self.subnet_cidrs:
        cidr = self.subnet_cidrs[subnet_id]
        return f"{cidr} ({subnet_name})"
    
    # Fallback: just show name
    return f"({subnet_name})"

def _get_vmss_name_for_pool(self, pool_name: str) -> Optional[str]:
    """
    Get VMSS name for agent pool from collected VMSS info.
    
    Args:
        pool_name: Agent pool name
        
    Returns:
        VMSS name if found, None otherwise
    """
    # Look through self.vmss_info for matching pool
    # VMSS typically named: aks-{poolname}-{id}-vmss
    
    if not hasattr(self, 'vmss_info') or not self.vmss_info:
        return None
    
    for vmss in self.vmss_info:
        vmss_name = vmss.get('name', '')
        # Match pattern: aks-{poolname}-
        if f"aks-{pool_name}-" in vmss_name.lower():
            return vmss_name
    
    return None
```

**Integration:** Call `_print_node_pools()` in `_print_detailed()` after network configuration section.

---

### 8.3: Subnet CIDR Caching

To avoid duplicate API calls when fetching subnet CIDRs (both in pod CIDR summary and node pool display), implement caching:

```python
# In cluster_data_collector.py

def _get_all_subnet_cidrs(
    self,
    agent_pools: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Fetch all subnet CIDRs (both node and pod subnets) in a single pass.
    Cache results to avoid duplicate API calls.
    
    Returns:
        Dictionary mapping subnet resource ID to CIDR
    """
    subnet_cidrs = {}
    processed_subnets = set()
    
    for pool in agent_pools:
        # Collect all unique subnet IDs
        subnet_ids = []
        
        node_subnet_id = pool.get('vnet_subnet_id')
        if node_subnet_id and node_subnet_id not in processed_subnets:
            subnet_ids.append(node_subnet_id)
            processed_subnets.add(node_subnet_id)
        
        pod_subnet_id = pool.get('pod_subnet_id')
        if pod_subnet_id and pod_subnet_id not in processed_subnets:
            subnet_ids.append(pod_subnet_id)
            processed_subnets.add(pod_subnet_id)
        
        # Fetch each subnet
        for subnet_id in subnet_ids:
            try:
                subnet_parts = subnet_id.split('/')
                resource_group = subnet_parts[4]
                vnet_name = subnet_parts[8]
                subnet_name = subnet_parts[10]
                
                subnet = self.network_client.subnets.get(
                    resource_group_name=resource_group,
                    virtual_network_name=vnet_name,
                    subnet_name=subnet_name
                )
                
                subnet_cidrs[subnet_id] = subnet.address_prefix
                
            except HttpResponseError as e:
                self._check_authorization_error(
                    e,
                    resource_type="Subnet",
                    resource_name=subnet_name,
                    resource_group=resource_group
                )
                subnet_cidrs[subnet_id] = "Permission Denied"
                
            except Exception as e:
                self.logger.error(f"Error fetching subnet {subnet_id}: {e}")
                subnet_cidrs[subnet_id] = "Error"
    
    return subnet_cidrs
```

---

## Testing Strategy

### Test Matrix

| Cluster Type | Network Plugin | Plugin Mode | Pod CIDR | Pod Subnet ID | Expected Display |
|--------------|----------------|-------------|----------|---------------|------------------|
| **aks-kubenet-byo-vnet-bicep** | kubenet | null | ✅ Populated | null | `Pod CIDR: 10.244.0.0/16` |
| **aks-overlay** | azure | overlay | ✅ Populated | null | `Pod CIDR: 10.244.0.0/16` |
| **aks-acni-podsubnet** | azure | null | null | ✅ Per-pool | `Pod Subnets: 10.241.0.0/16, 10.243.0.0/16` |
| **aks-legacy-acni** (TBD) | azure | null | null | null | `Pod CIDR: N/A - Pods use node subnet` |

### Test Cases

1. **Azure CNI Overlay (aks-overlay)**
   - ✅ Verify pod CIDR still displays correctly
   - ✅ Verify no regression in existing functionality
   - Test command: `az aks net-diagnostics -n aks-overlay -g aks-overlay-rg`

2. **Azure CNI Pod Subnet (aks-acni-podsubnet)**
   - ❌ Currently shows empty, should show pod subnets
   - Verify aggregated pod subnet CIDRs in summary
   - Verify per-pool pod subnets in detailed view
   - Test command: `az aks net-diagnostics -n aks-acni-podsubnet -g aks-acni-podsubnet-rg --details`

3. **Kubenet (aks-kubenet-byo-vnet-bicep)**
   - ✅ Verify pod CIDR still displays correctly
   - Test command: `az aks net-diagnostics -n aks-kubenet-byo-vnet-bicep -g aks-kubenet-byo-vnet-bicep-rg`

4. **Azure CNI Node Subnet (Legacy)** - Need to create test cluster
   - Verify shows appropriate "N/A - Pods use node subnet" message
   - Create cluster without overlay mode or pod subnet

5. **Node Pool Display**
   - Verify multi-pool clusters show all pools (aks-acni-podsubnet has 2 pools)
   - Verify single pool clusters work
   - Verify node/pod subnet information displays correctly
   - Verify VMSS names displayed when available

6. **Authorization Errors**
   - Test with pod subnet in different resource group (if possible)
   - Verify graceful handling with "Permission Denied" message

---

## Success Criteria

### Functional
- ✅ All four Azure CNI variants display correct pod CIDR information
- ✅ Multi-pool clusters show all agent pools with details
- ✅ Node and pod subnets displayed with CIDRs and names
- ✅ No regression in existing clusters (kubenet, overlay)
- ✅ Authorization errors handled gracefully

### Code Quality
- ✅ `azdev style acs` passes (10.00/10 rating)
- ✅ `azdev linter --ci-exclusions acs` passes
- ✅ No flake8 violations
- ✅ All new code has docstrings and type hints

### Documentation
- ✅ Code comments explain Azure CNI variant detection logic
- ✅ Docstrings describe parameters and return values
- ✅ Phase 8 marked complete in task list

---

## Technical Notes

### Subnet Resource ID Format

```
/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}
```

Parse with:
```python
parts = subnet_id.split('/')
subscription_id = parts[2]
resource_group = parts[4]
vnet_name = parts[8]
subnet_name = parts[10]
```

### Azure CNI Variant Decision Tree

```
Is networkPlugin == 'azure'?
├─ No → Handle as kubenet or other (use podCidr)
└─ Yes → Is networkPluginMode == 'overlay'?
    ├─ Yes → Azure CNI Overlay (use podCidr)
    └─ No → Does any pool have podSubnetId?
        ├─ Yes → Azure CNI Pod Subnet (fetch subnet CIDRs)
        └─ No → Azure CNI Node Subnet Legacy (no pod CIDR)
```

### API Calls Summary

**New API Calls:**
- `network_client.subnets.get()` - for each unique subnet (node + pod)
  - Cached to avoid duplicates
  - Called during cluster data collection phase

**No Additional Calls for Display:**
- All subnet CIDRs fetched once during collection
- Stored in orchestrator/collector for use in report generation

---

## Future Enhancements

### Phase 9 Considerations
- Add pod IP allocation statistics (used/available IPs in pod subnet)
- Show subnet delegation status
- Display subnet service endpoints
- Show subnet network policies (if any)
- Add warnings for pod subnet capacity issues

---

## References

- [Azure CNI Networking](https://learn.microsoft.com/en-us/azure/aks/configure-azure-cni)
- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Azure CNI Dynamic IP Allocation](https://learn.microsoft.com/en-us/azure/aks/configure-azure-cni-dynamic-ip-allocation)
- [AKS Network Concepts](https://learn.microsoft.com/en-us/azure/aks/concepts-network)

---

**Last Updated:** October 23, 2025  
**Next Review:** Before Phase 8 implementation
