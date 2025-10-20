# Integration Strategy

## Chosen Approach: Hybrid Integration

After analyzing the codebase, we'll use a **hybrid approach** that balances preservation of existing logic with Azure CLI best practices.

## Strategy Overview

### Phase 1: Preparation (Current Phase)
- ✅ Create planning documents
- ✅ Analyze aks-net-diagnostics code structure
- ✅ Identify required changes
- Create prototype of key changes

### Phase 2: Code Adaptation
1. Copy aks-net-diagnostics modules to Azure CLI
2. Adapt Azure SDK client for CLI authentication
3. Refactor main orchestrator to accept parameters
4. Integrate with Azure CLI command system

### Phase 3: Testing & Validation
1. Unit tests for new code
2. Integration tests
3. Manual testing with real clusters
4. Compare output with standalone tool

### Phase 4: Documentation & Polish
1. Update help text
2. Add examples
3. Update Azure CLI documentation
4. Create migration guide for users

## Detailed Integration Plan

### 1. Module Organization

```
src/azure-cli/azure/cli/command_modules/acs/
├── net_diagnostics/                      # NEW DIRECTORY
│   ├── __init__.py
│   ├── orchestrator.py                   # Adapted from aks-net-diagnostics.py
│   ├── sdk_client.py                     # Adapted from azure_sdk_client.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base_analyzer.py              # FROM: base_analyzer.py
│   │   ├── nsg_analyzer.py               # FROM: nsg_analyzer.py
│   │   ├── dns_analyzer.py               # FROM: dns_analyzer.py
│   │   ├── route_table_analyzer.py       # FROM: route_table_analyzer.py
│   │   ├── api_server_analyzer.py        # FROM: api_server_analyzer.py
│   │   ├── connectivity_tester.py        # FROM: connectivity_tester.py
│   │   ├── outbound_analyzer.py          # FROM: outbound_analyzer.py
│   │   └── misconfiguration_analyzer.py  # FROM: misconfiguration_analyzer.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── cluster_data_collector.py     # FROM: cluster_data_collector.py
│   ├── report_generator.py               # FROM: report_generator.py
│   ├── models.py                         # FROM: models.py
│   ├── exceptions.py                     # FROM: exceptions.py
│   └── validators.py                     # FROM: validators.py (adapted)
```

### 2. Key File Modifications

#### A. Command Registration (`commands.py`)

Add command registration:

```python
def load_command_table(self, _):
    # ... existing commands ...
    
    # Net-diagnostics command
    with self.command_group('aks') as g:
        g.custom_command('net-diagnostics', 
                        'aks_net_diagnostics',
                        supports_no_wait=False)
```

#### B. Parameter Definition (`_params.py`)

Add parameter definitions:

```python
def load_arguments(self, _):
    # ... existing parameters ...
    
    with self.argument_context('aks net-diagnostics') as c:
        c.argument('name', options_list=['--name', '-n'],
                   help='Name of the managed cluster.')
        c.argument('resource_group_name', options_list=['--resource-group', '-g'],
                   help='Name of resource group.')
        c.argument('details', action='store_true',
                   help='Show detailed analysis and test results.')
        c.argument('probe_test', action='store_true',
                   help='Enable active connectivity tests from cluster nodes. '
                        'Warning: Executes commands inside cluster nodes.')
        c.argument('json_report', 
                   help='Save JSON report to file. Optionally specify filename, '
                        'otherwise auto-generated.')
```

#### C. Command Implementation (`custom.py` or new file)

Create main command function:

```python
def aks_net_diagnostics(cmd, 
                       name, 
                       resource_group_name,
                       details=False,
                       probe_test=False,
                       json_report=None):
    """
    Perform comprehensive network diagnostics on an AKS cluster.
    
    :param cmd: CLI context
    :param name: Cluster name
    :param resource_group_name: Resource group name
    :param details: Show detailed output
    :param probe_test: Enable active connectivity tests
    :param json_report: JSON report filename
    :return: Diagnostic results
    """
    from azure.cli.command_modules.acs.net_diagnostics.orchestrator import NetDiagnosticsOrchestrator
    
    orchestrator = NetDiagnosticsOrchestrator(
        cmd=cmd,
        cluster_name=name,
        resource_group_name=resource_group_name,
        show_details=details,
        probe_test=probe_test,
        json_report=json_report
    )
    
    return orchestrator.run()
```

### 3. Critical Code Changes

#### ✅ Adapt `azure_sdk_client.py` for CLI Authentication

**CURRENT (`aks_diagnostics/azure_sdk_client.py` on azure-sdk branch):**
```python
class AzureSDKClient:
    """Thin wrapper for Azure SDK clients"""
    
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()  # ⚠️ Replace this
        self._aks_client = None
        self._network_client = None
    
    @property
    def aks_client(self) -> ContainerServiceClient:
        if not self._aks_client:
            self._aks_client = ContainerServiceClient(
                self.credential, self.subscription_id)
        return self._aks_client
```

**ADAPTED for Azure CLI (`net_diagnostics/sdk_client.py`):**
```python
class SDKClient:
    """Azure SDK client wrapper using CLI authentication"""
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.cli_ctx = cmd.cli_ctx
        # Get subscription from CLI context
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=self.cli_ctx)
        self.subscription_id = profile.get_subscription_id()
    
    def get_aks_client(self):
        """Get ContainerServiceClient using CLI's client factory"""
        from azure.cli.command_modules.acs._client_factory import cf_container_services
        return cf_container_services(self.cli_ctx)
    
    def get_network_client(self):
        """Get NetworkManagementClient using CLI's client factory"""
        from azure.cli.core.commands.client_factory import get_mgmt_service_client
        from azure.mgmt.network import NetworkManagementClient
        return get_mgmt_service_client(self.cli_ctx, NetworkManagementClient)
    
    # ... adapt other client properties similarly
```

**Key Changes:**
- Replace `DefaultAzureCredential()` with `cmd.cli_ctx`
- Use CLI's client factories (`cf_container_services`, `get_mgmt_service_client`)
- Get subscription from CLI's Profile instead of parameter

#### Adapt Main Orchestrator

**OLD (`aks-net-diagnostics.py`):**
```python
class AKSNetworkDiagnostics:
    def __init__(self):
        self.aks_name = None
        self.aks_rg = None
        # ...
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        # ... argparse setup
        args = parser.parse_args()
        self.aks_name = args.name
        # ...
    
    def run(self):
        self.parse_arguments()  # ❌ Remove this
        # ... analysis steps
```

**NEW (`net_diagnostics/orchestrator.py`):**
```python
class NetDiagnosticsOrchestrator:
    def __init__(self, cmd, cluster_name, resource_group_name, 
                 show_details=False, probe_test=False, json_report=None):
        self.cmd = cmd
        self.cluster_name = cluster_name
        self.resource_group_name = resource_group_name
        self.show_details = show_details
        self.probe_test = probe_test
        self.json_report = json_report
        
        # Create SDK client wrapper
        self.sdk_client = SDKClient(cmd)
        # ... rest of initialization
    
    def run(self):
        # NO parse_arguments() - parameters already provided
        # ... analysis steps (same as before)
```

### 4. Testing Strategy

#### Unit Tests

Create `test_aks_net_diagnostics.py`:

```python
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

class AksNetDiagnosticsTest(ScenarioTest):
    
    @ResourceGroupPreparer()
    def test_net_diagnostics_basic(self, resource_group):
        """Test basic net-diagnostics command"""
        self.cmd('aks net-diagnostics -n testcluster -g {rg}',
                checks=[
                    self.exists('findings'),
                    self.exists('cluster_info')
                ])
    
    @ResourceGroupPreparer()
    def test_net_diagnostics_with_details(self, resource_group):
        """Test net-diagnostics with --details flag"""
        self.cmd('aks net-diagnostics -n testcluster -g {rg} --details',
                checks=[
                    self.exists('findings'),
                    self.exists('detailed_analysis')
                ])
```

#### Integration Testing

1. **Manual Testing Checklist:**
   - [ ] Command appears in `az aks --help`
   - [ ] Help text displays correctly: `az aks net-diagnostics --help`
   - [ ] Basic execution works: `az aks net-diagnostics -n cluster -g rg`
   - [ ] All flags work: `--details`, `--probe-test`, `--json-report`
   - [ ] Output matches standalone tool output
   - [ ] Errors are handled gracefully
   - [ ] Works with different auth scenarios

2. **Comparison Testing:**
   - Run standalone tool on cluster
   - Run Azure CLI command on same cluster
   - Compare outputs (should be nearly identical)

### 5. Migration Path

#### Update Analyzer Imports

**Before (azure-sdk branch):**
```python
from aks_diagnostics.nsg_analyzer import NSGAnalyzer
from aks_diagnostics.azure_sdk_client import AzureSDKClient
```

**After (Azure CLI):**
```python
from azure.cli.command_modules.acs.net_diagnostics.analyzers.nsg_analyzer import NSGAnalyzer
from azure.cli.command_modules.acs.net_diagnostics.sdk_client import SDKClient
```

#### Update Analyzer Constructor Calls

**Before (azure-sdk branch):**
```python
self.sdk_client = AzureSDKClient(subscription_id)
analyzer = NSGAnalyzer(self.sdk_client, cluster_info, vmss_info)
```

**After (Azure CLI):**
```python
self.sdk_client = SDKClient(cmd)
analyzer = NSGAnalyzer(self.sdk_client, cluster_info, vmss_info)
```

### 6. Rollout Plan

#### Step 1: Local Development Setup
1. Clone both repos (azure-cli and aks-net-diagnostics)
2. Set up Azure CLI dev environment with azdev
3. Create feature branch

#### Step 2: Copy & Initial Adaptation
1. Copy aks_diagnostics modules to net_diagnostics
2. Create sdk_client.py with basic methods
3. Update imports throughout

#### Step 3: Command Integration
1. Update commands.py
2. Update _params.py
3. Create command function in custom.py

#### Step 4: Testing
1. Run unit tests: `azdev test acs`
2. Manual testing with real clusters
3. Fix any issues found

#### Step 5: Documentation
1. Add help text
2. Update module documentation
3. Create examples

#### Step 6: Pull Request
1. Ensure all tests pass
2. Run style checkers: `azdev style acs`
3. Submit PR following Azure CLI guidelines

## Decision Log

### Decision 1: Where to Place Net-Diagnostics Code?
**Options:**
- A. Put in existing `custom.py` (becomes too large)
- B. Create new subdirectory `net_diagnostics/` ✅ **CHOSEN**
- C. Create as separate extension

**Rationale:** Subdirectory keeps code organized while being part of core ACS module.

### Decision 2: How to Handle Authentication?
**Options:**
- A. Keep `DefaultAzureCredential` from azure-sdk branch (auth mismatch with CLI)
- B. Adapt to use CLI's client factories ✅ **CHOSEN**

**Rationale:** The azure-sdk branch already uses Azure SDK clients directly. We just need to adapt the authentication mechanism from `DefaultAzureCredential()` to CLI's `cmd.cli_ctx` using client factories like `cf_container_services()` and `get_mgmt_service_client()`.

### Decision 3: How to Handle Arguments?
**Options:**
- A. Keep argparse (conflicts with CLI)
- B. Use CLI's argument system ✅ **CHOSEN**

**Rationale:** Must integrate with CLI's parameter system.

## Open Questions

See `05-questions-and-decisions.md` for unresolved items.

## Next Steps

1. Review this strategy document
2. Start implementing Phase 2 (Code Adaptation)
3. Follow task list in `03-task-list.md`
