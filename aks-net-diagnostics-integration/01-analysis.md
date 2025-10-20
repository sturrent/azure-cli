# Analysis of Integration Requirements

## 1. aks-net-diagnostics Architecture Analysis

### Current Structure (azure-sdk branch)
```
aks-net-diagnostics/
├── aks-net-diagnostics.py          # Main orchestrator (467 lines)
└── aks_diagnostics/                # Core modules
    ├── __init__.py
    ├── api_server_analyzer.py
    ├── azure_sdk_client.py
    ├── base_analyzer.py
    ├── cluster_data_collector.py
    ├── connectivity_tester.py
    ├── dns_analyzer.py
    ├── exceptions.py
    ├── misconfiguration_analyzer.py
    ├── models.py
    ├── nsg_analyzer.py
    ├── outbound_analyzer.py
    ├── report_generator.py
    ├── route_table_analyzer.py
    └── validators.py
```

### Key Components

#### 1. Main Orchestrator (`aks-net-diagnostics.py`)
- **Purpose:** Coordinates the analysis workflow
- **Key Methods:**
  - `parse_arguments()` - ⚠️ Uses argparse (MUST REMOVE)
  - `run()` - Main execution flow (CAN REUSE)
  - `fetch_cluster_information()`
  - `analyze_vnet_configuration()`
  - `analyze_outbound_connectivity()`
  - `analyze_vmss_configuration()`
  - `analyze_nsg_configuration()`
  - `analyze_private_dns()`
  - `analyze_api_server_access()`
  - `check_api_connectivity()`
  - `analyze_misconfigurations()`
  - `generate_report()`

#### 2. Azure SDK Client (`aks_diagnostics/azure_sdk_client.py`)
- Uses Azure SDK management clients directly
- **Key Features:**
  - Lazy initialization of SDK clients (matches Azure CLI pattern)
  - Property-based access (`.aks_client`, `.network_client`, `.compute_client`, `.privatedns_client`)
  - Uses `DefaultAzureCredential` for authentication (needs to be adapted to CLI's auth)
  - Helper methods like `get_cluster()` for common operations
  - `parse_resource_id()` utility for parsing Azure resource IDs

#### 3. Analysis Modules
All analyzers follow a consistent pattern:
- Inherit from `BaseAnalyzer`
- Accept Azure SDK client and cluster info
- Have an `analyze()` method that returns structured findings
- Generate `Finding` objects with severity levels
- Analysis logic can be reused with minimal changes

### Dependencies Analysis

#### Current aks-net-diagnostics Dependencies
```python
# requirements.txt
azure-identity>=1.15.0
azure-mgmt-containerservice>=20.0.0
azure-mgmt-network>=23.0.0
azure-mgmt-compute>=30.0.0
azure-mgmt-privatedns>=1.0.0
azure-mgmt-resource>=23.0.0
```

#### Azure CLI ACS Module Dependencies
The ACS module uses:
- `azure.cli.core` - Core CLI framework
- `azure.cli.command_modules.acs.*` - Module-specific code
- Azure SDK packages (via requirements)
- Client factories that leverage CLI's authentication

## 2. Flag Conflict Analysis

### Flags Handled by Azure CLI Framework
These are **already provided** by Azure CLI and should NOT be reimplemented:

| Flag | Description | Action |
|------|-------------|--------|
| `-n, --name` | Resource name | ✅ Use CLI's standard `-n` |
| `-g, --resource-group` | Resource group | ✅ Use CLI's standard `-g` |
| `--subscription` | Subscription ID | ✅ Use CLI's built-in |
| `--help, -h` | Help text | ✅ CLI handles automatically |
| `--version` | Version info | ✅ CLI handles automatically |

### Flags Unique to aks-net-diagnostics
These need to be added as command-specific parameters:

| Flag | Description | Keep? |
|------|-------------|-------|
| `--details` | Show detailed output | ✅ YES - Add as boolean flag |
| `--probe-test` | Enable connectivity tests | ✅ YES - Add as boolean flag |
| `--json-report [FILE]` | Save JSON report | ✅ YES - Add as optional string parameter |

### Argument Parsing Changes Required

**BEFORE (aks-net-diagnostics.py):**
```python
def parse_arguments(self):
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("-n", "--name", required=True, help="AKS cluster name")
    parser.add_argument("-g", "--resource-group", required=True, help="AKS resource group")
    parser.add_argument("--subscription", help="Azure subscription ID")
    parser.add_argument("--probe-test", action="store_true", help="Enable active connectivity checks")
    parser.add_argument("--json-report", nargs="?", const="auto", help="Save JSON report")
    parser.add_argument("--details", action="store_true", help="Show detailed output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()
```

**AFTER (Azure CLI integration):**
```python
# In _params.py
def load_arguments(self, _):
    with self.argument_context('aks net-diagnostics') as c:
        c.argument('name', options_list=['--name', '-n'], help='AKS cluster name')
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], 
                   help='Resource group name')
        c.argument('details', action='store_true', 
                   help='Show detailed analysis and test results')
        c.argument('probe_test', action='store_true', 
                   help='Enable active connectivity tests from nodes')
        c.argument('json_report', 
                   help='Save JSON report (optional filename)')
```

## 3. Authentication Changes Required

### Current Approach (Azure SDK)
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Then pass to Azure SDK clients
```

### Required Approach (Azure CLI)
```python
# Use CLI's client factories
from azure.cli.command_modules.acs._client_factory import cf_container_services

def my_command(cmd, cluster_name, resource_group_name):
    client = cf_container_services(cmd.cli_ctx)
    # CLI handles authentication automatically
    cluster = client.managed_clusters.get(resource_group_name, cluster_name)
```

## 4. Code Execution Model Changes

### Current Model (Standalone)
```
User runs Python script
    ↓
Script parses args with argparse
    ↓
Script creates AzureSDKClient with DefaultAzureCredential
    ↓
AzureSDKClient uses Azure SDK to fetch cluster data
    ↓
Analyzers process data and generate findings
    ↓
Output formatted and displayed
```

### Required Model (Azure CLI Integration)
```
User runs: az aks net-diagnostics -n foo -g bar
    ↓
Azure CLI framework loads ACS module
    ↓
Framework calls net_diagnostics_command(cmd, name, resource_group_name, ...)
    ↓
Command uses CLI's client factories with cmd.cli_ctx
    ↓
Analyzers process data and generate findings
    ↓
Output formatted and returned via CLI framework
```

## 5. Major Code Changes Required

### Authentication Adaptation

**File:** `aks_diagnostics/azure_sdk_client.py` (azure-sdk branch)

**Current Code:**
```python
class AzureSDKClient:
    """Thin wrapper for Azure SDK clients following Azure CLI pattern"""
    
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        # Lazy initialization
        self._aks_client = None
        self._network_client = None
        self._compute_client = None
        self._privatedns_client = None
    
    @property
    def aks_client(self) -> ContainerServiceClient:
        if not self._aks_client:
            self._aks_client = ContainerServiceClient(
                self.credential, self.subscription_id)
        return self._aks_client
    
    def get_cluster(self, resource_group: str, cluster_name: str):
        cluster = self.aks_client.managed_clusters.get(
            resource_group, cluster_name)
        return cluster
```

**Required Change for CLI Integration:**
Adapt to use Azure CLI's authentication context:
```python
def get_cluster(self, cmd, resource_group_name: str, cluster_name: str):
    from azure.cli.command_modules.acs._client_factory import cf_container_services
    client = cf_container_services(cmd.cli_ctx)
    return client.managed_clusters.get(resource_group_name, cluster_name)
```

### Summary of Changes Needed

1. **Remove:** `parse_arguments()` method - CLI framework handles argument parsing
2. **Adapt:** `azure_sdk_client.py` to use CLI's `cmd.cli_ctx` instead of `DefaultAzureCredential`
3. **Update:** Analyzers to accept `cmd` parameter and use CLI's client factories
4. **Modify:** Main orchestrator to be a command handler function instead of standalone script
5. **Add:** Parameter definitions in `_params.py`
6. **Add:** Command registration in `commands.py`
7. **Adapt:** Output formatting to use CLI's output system

## 6. File Organization in Azure CLI

### Where Code Should Go

```
src/azure-cli/azure/cli/command_modules/acs/
├── __init__.py                    # Update to include new command
├── commands.py                    # Register 'net-diagnostics' command
├── _params.py                     # Define parameters for net-diagnostics
├── custom.py                      # Main command implementation (or new file)
├── net_diagnostics/               # NEW: Net diagnostics modules
│   ├── __init__.py
│   ├── orchestrator.py            # Main analysis orchestrator
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── nsg_analyzer.py
│   │   ├── dns_analyzer.py
│   │   ├── route_table_analyzer.py
│   │   ├── api_server_analyzer.py
│   │   ├── connectivity_tester.py
│   │   └── outbound_analyzer.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── cluster_data_collector.py
│   ├── report_generator.py
│   ├── models.py
│   ├── exceptions.py
│   └── validators.py
└── tests/
    └── latest/
        └── test_aks_net_diagnostics.py  # NEW: Tests
```

## 7. Integration Complexity Assessment

| Component | Complexity | Estimated Effort | Risk |
|-----------|------------|------------------|------|
| Remove argparse | Low | 1 hour | Low |
| Adapt SDK client authentication | Low | 3-4 hours | Low |
| Register command in CLI | Low | 2 hours | Low |
| Define parameters | Low | 2 hours | Low |
| Port analyzer modules | Low | 2 hours | Low |
| Update tests | Medium | 8 hours | Medium |
| Documentation | Low | 4 hours | Low |
| **TOTAL** | - | **22-32 hours** | - |

## 8. Risk Factors

### Medium Risk
1. **Testing coverage:** Need to ensure all functionality works within CLI context
2. **Error handling:** CLI's error patterns may differ from standalone tool
3. **Output formatting:** CLI may have specific output requirements
4. **Performance:** SDK call patterns may differ in CLI environment
5. **Authentication edge cases:** Different auth scenarios to handle (managed identity, service principal, etc.)

### Low Risk
1. **Parameter definition:** Well-documented CLI patterns to follow
2. **Command registration:** Straightforward process with clear examples
3. **Module organization:** Clear structure to follow in existing ACS module
4. **SDK client adaptation:** Simple credential swap from DefaultAzureCredential to cmd.cli_ctx

## Next Steps

Proceed to `02-integration-strategy.md` for the proposed approach.
