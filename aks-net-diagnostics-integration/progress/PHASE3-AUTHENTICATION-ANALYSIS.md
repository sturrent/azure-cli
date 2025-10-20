# Phase 3: Authentication Adapter - Analysis

**Date:** October 19, 2025  
**Status:** 🔍 In Progress - Analysis Phase

## Overview

This document analyzes how to adapt `azure_sdk_client.py` from aks-net-diagnostics to work with Azure CLI's authentication system.

## Current Implementation (aks-net-diagnostics)

### File: `aks_diagnostics/azure_sdk_client.py`

**Key Features:**
- Uses `DefaultAzureCredential` from `azure-identity`
- Lazy initialization pattern for SDK clients
- Property-based access (@property decorators)
- Helper methods for common operations
- Context manager support (`__enter__`/`__exit__`)

### Authentication Flow

```python
def __init__(self, subscription_id: str):
    self.subscription_id = subscription_id
    self.credential = DefaultAzureCredential()  # ← THIS NEEDS TO CHANGE
    
    # Lazy initialization
    self._aks_client = None
    self._network_client = None
    self._compute_client = None
    self._privatedns_client = None

@property
def aks_client(self) -> ContainerServiceClient:
    if not self._aks_client:
        self._aks_client = ContainerServiceClient(
            self.credential,           # ← Uses DefaultAzureCredential
            self.subscription_id
        )
    return self._aks_client
```

### SDK Clients Used

1. **ContainerServiceClient** - AKS operations
2. **NetworkManagementClient** - VNet, NSG, LB, NAT operations
3. **ComputeManagementClient** - VMSS operations
4. **PrivateDnsManagementClient** - Private DNS operations

## Azure CLI Authentication Pattern

### File: `src/azure-cli/azure/cli/command_modules/acs/_client_factory.py`

**Key Pattern:**
```python
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

def get_container_service_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(
        cli_ctx, 
        ResourceType.MGMT_CONTAINERSERVICE, 
        subscription_id=subscription_id
    )

def cf_managed_clusters(cli_ctx, *_):
    return get_container_service_client(cli_ctx).managed_clusters
```

**How it works:**
- Takes `cli_ctx` (CLI context) instead of credential
- Uses `get_mgmt_service_client()` to create clients
- `ResourceType` enum specifies which Azure service
- Automatically uses logged-in Azure CLI credentials
- No need for `DefaultAzureCredential`

### Core Function: `get_mgmt_service_client`

From `src/azure-cli-core/azure/cli/core/commands/client_factory.py`:

```python
def get_mgmt_service_client(cli_ctx, client_or_resource_type, 
                           subscription_id=None, api_version=None,
                           aux_subscriptions=None, aux_tenants=None, 
                           credential=None, **kwargs):
    """
    Create Python SDK mgmt-plane client with CLI authentication.
    
    Features:
    - Uses CLI's logged-in credentials automatically
    - Multi-API support
    - Server telemetry
    - Safe logging
    - Cross-tenant authentication
    """
```

## Adaptation Strategy

### Option 1: CLI-Style Client Factories (RECOMMENDED)

**Pros:**
- Follows Azure CLI best practices
- Consistent with existing ACS code
- Minimal code changes needed
- Automatic credential handling

**Cons:**
- Changes class design pattern
- More files to modify

**Implementation:**
```python
# In _client_factory.py (add new functions)

def get_network_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(
        cli_ctx, 
        ResourceType.MGMT_NETWORK, 
        subscription_id=subscription_id
    )

def get_privatedns_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(
        cli_ctx, 
        ResourceType.MGMT_PRIVATEDNS, 
        subscription_id=subscription_id
    )

# In custom.py or net_diagnostics/orchestrator.py
def aks_net_diagnostics(cmd, resource_group, name, **kwargs):
    # Get clients using CLI context
    aks_client = cf_managed_clusters(cmd.cli_ctx)
    network_client = get_network_client(cmd.cli_ctx)
    compute_client = get_compute_client(cmd.cli_ctx)
    privatedns_client = get_privatedns_client(cmd.cli_ctx)
    
    # Pass clients to orchestrator
    orchestrator = NetDiagnosticsOrchestrator(
        aks_client=aks_client,
        network_client=network_client,
        compute_client=compute_client,
        privatedns_client=privatedns_client,
        resource_group=resource_group,
        cluster_name=name,
        **kwargs
    )
    return orchestrator.run()
```

### Option 2: Adapter Class (HYBRID)

Keep the class design but adapt authentication:

**Pros:**
- Minimal changes to existing code
- Keeps encapsulation
- Easy to understand

**Cons:**
- Less CLI-idiomatic
- Duplicate pattern (CLI already has client factories)

**Implementation:**
```python
# In net_diagnostics/sdk_client.py

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

class AzureSDKClient:
    """
    Thin wrapper for Azure SDK clients using CLI authentication.
    """
    
    def __init__(self, cmd):
        """
        Initialize with CLI context instead of subscription_id.
        
        Args:
            cmd: CLI command context (has cli_ctx)
        """
        self.cli_ctx = cmd.cli_ctx
        self.subscription_id = cmd.cli_ctx.data.get('subscription_id')
        
        # Lazy initialization - clients created on first access
        self._aks_client = None
        self._network_client = None
        self._compute_client = None
        self._privatedns_client = None
    
    @property
    def aks_client(self) -> ContainerServiceClient:
        if not self._aks_client:
            self._aks_client = get_mgmt_service_client(
                self.cli_ctx,
                ResourceType.MGMT_CONTAINERSERVICE
            ).managed_clusters  # Return the operation group
        return self._aks_client
    
    @property
    def network_client(self) -> NetworkManagementClient:
        if not self._network_client:
            self._network_client = get_mgmt_service_client(
                self.cli_ctx,
                ResourceType.MGMT_NETWORK
            )
        return self._network_client
    
    # ... similar for compute_client and privatedns_client
    
    def get_cluster(self, resource_group: str, cluster_name: str):
        try:
            # Use the operation group directly
            cluster = self.aks_client.get(resource_group, cluster_name)
            return cluster
        except ResourceNotFoundError as exc:
            raise AzureSDKError(f"Cluster '{cluster_name}' not found") from exc
```

## ResourceType Mappings

Need to verify these exist in Azure CLI:

| SDK Client | ResourceType Constant | Status |
|------------|----------------------|--------|
| ContainerServiceClient | `ResourceType.MGMT_CONTAINERSERVICE` | ✅ Confirmed |
| NetworkManagementClient | `ResourceType.MGMT_NETWORK` | ❓ Need to verify |
| ComputeManagementClient | `ResourceType.MGMT_COMPUTE` | ✅ Confirmed (used in _client_factory.py) |
| PrivateDnsManagementClient | `ResourceType.MGMT_PRIVATEDNS` | ❓ Need to verify |

### Action: Verify ResourceType Constants

```bash
# Check what ResourceType constants are available
grep -r "MGMT_NETWORK\|MGMT_PRIVATEDNS" src/azure-cli-core/azure/cli/core/profiles/
```

## Key Changes Required

### 1. Remove azure-identity Dependency

**Before:**
```python
from azure.identity import DefaultAzureCredential
self.credential = DefaultAzureCredential()
```

**After:**
```python
# No azure-identity import needed
# CLI handles authentication automatically
```

### 2. Change Initialization

**Before:**
```python
sdk_client = AzureSDKClient(subscription_id)
```

**After (Option 1 - Factory):**
```python
aks_client = cf_managed_clusters(cmd.cli_ctx)
network_client = get_network_client(cmd.cli_ctx)
```

**After (Option 2 - Adapter):**
```python
sdk_client = AzureSDKClient(cmd)  # Pass cmd instead of subscription_id
```

### 3. Update Client Creation

**Before:**
```python
self._aks_client = ContainerServiceClient(self.credential, self.subscription_id)
```

**After:**
```python
self._aks_client = get_mgmt_service_client(
    self.cli_ctx,
    ResourceType.MGMT_CONTAINERSERVICE
)
```

### 4. Update All Analyzers

All analyzer modules that use `sdk_client` need to work with the new pattern:

**Files to update:**
- `nsg_analyzer.py` - Uses network_client
- `route_table_analyzer.py` - Uses network_client
- `dns_analyzer.py` - Uses network_client, privatedns_client
- `api_server_analyzer.py` - Uses aks_client
- `connectivity_tester.py` - Uses network_client
- `outbound_analyzer.py` - Uses network_client
- `misconfiguration_analyzer.py` - Uses aks_client, network_client

## Testing Approach

### 1. Verify ResourceType Constants
```python
from azure.cli.core.profiles import ResourceType
print(dir(ResourceType))
```

### 2. Test Client Creation
```python
def test_client_creation(cmd):
    # Test each client type
    aks_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_CONTAINERSERVICE)
    network_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_NETWORK)
    compute_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_COMPUTE)
    
    print(f"AKS Client: {type(aks_client)}")
    print(f"Network Client: {type(network_client)}")
    print(f"Compute Client: {type(compute_client)}")
```

### 3. Test get_cluster Helper
```python
def test_get_cluster(cmd, resource_group, cluster_name):
    sdk_client = AzureSDKClient(cmd)
    cluster = sdk_client.get_cluster(resource_group, cluster_name)
    print(f"Cluster: {cluster.name}")
    print(f"Location: {cluster.location}")
```

## Decision: Which Option?

### Recommendation: **Option 1 (CLI-Style Client Factories)**

**Rationale:**
1. **Azure CLI Best Practice:** This is the established pattern in Azure CLI
2. **Consistency:** Matches existing ACS module code
3. **Maintainability:** Future CLI developers will understand this pattern
4. **Less Code:** No need for wrapper class
5. **Better Integration:** Uses CLI's client factory infrastructure

**Trade-off:**
- More changes to orchestrator and analyzers (pass clients as parameters)
- But: More idiomatic and maintainable long-term

### Implementation Plan

1. **Add client factories to `_client_factory.py`**
   - `get_network_client()`
   - `get_privatedns_client()`

2. **Create command handler in `custom.py` or new file**
   - Get all required clients
   - Pass to orchestrator

3. **Modify orchestrator to accept clients**
   - Change `__init__` signature
   - Remove SDK client instantiation
   - Accept clients as parameters

4. **Update all analyzers**
   - Pass clients from orchestrator
   - No changes to analyzer logic needed

## Next Steps

1. ✅ Analyze authentication patterns (this document)
2. ⏳ Verify ResourceType constants exist
3. ⏳ Create prototype adapter
4. ⏳ Test with simple cluster query
5. ⏳ Update orchestrator signature
6. ⏳ Update all analyzers
7. ⏳ Add to _client_factory.py
8. ⏳ Create command handler

## Files to Create/Modify

### New Files
- `src/azure-cli/azure/cli/command_modules/acs/net_diagnostics/` (directory)
- `orchestrator.py` - Adapted from aks-net-diagnostics.py
- Copy all analyzer modules (with client parameter updates)

### Modified Files
- `_client_factory.py` - Add network and privatedns client factories
- `custom.py` or new `_net_diagnostics.py` - Add command handler
- `commands.py` - Register new command
- `_params.py` - Define command parameters

## Questions to Resolve

1. ❓ Does `ResourceType.MGMT_NETWORK` exist?
2. ❓ Does `ResourceType.MGMT_PRIVATEDNS` exist?
3. ❓ Do we need to add azure-mgmt-network to setup.py?
4. ❓ Should command handler be in custom.py or separate file?

---

**Status:** Analysis complete, ready to verify ResourceType constants and create prototype.
