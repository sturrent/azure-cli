# Azure CLI Output Format Analysis

**Date:** October 19, 2025  
**Purpose:** Analyze how Azure CLI handles output formatting and determine approach for `az aks net-diagnostics`

## Azure CLI Output Requirements

Based on reviewing `doc/command_guidelines.md` and existing ACS commands:

### Key Requirements

1. **Commands must support all output types**: JSON, TSV, table, YAML
2. **Return Python objects**: Commands must return dictionaries, lists, or `None` - NOT strings or custom text
3. **stdout vs stderr**: 
   - Command output → `stdout` (handled automatically by CLI framework)
   - Logs, status, errors → `stderr` (use `logger.info()`, `logger.warning()`, `logger.error()`)
4. **No print() statements**: Use logger instead
5. **Table transformers**: Provide custom table formatters for pretty table output

## How Other ACS Commands Handle Output

### Pattern 1: Return Structured Data (Most Common)

**Example: `az aks show`**
```python
def aks_show(cmd, client, resource_group_name, name):
    mc = client.get(resource_group_name, name)
    return _remove_nulls([mc])[0]  # Returns Python dictionary
```

**Table Transformer:**
```python
def aks_show_table_format(result):
    """Format a managed cluster as summary results for display with "-o table"."""
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        kubernetesVersion: kubernetesVersion,
        currentKubernetesVersion: currentKubernetesVersion,
        provisioningState: provisioningState,
        fqdn: fqdn || privateFqdn
    }""")
    return parsed.search(result, Options(dict_cls=OrderedDict))
```

**Command Registration:**
```python
g.show_command('show', 'aks_show',
              table_transformer=aks_show_table_format)
```

**Result:**
- `--output json`: Full cluster object as JSON (default CLI behavior)
- `--output table`: Custom formatted table using transformer
- `--output yaml`: Full cluster object as YAML (default CLI behavior)
- `--output tsv`: Tab-separated values (default CLI behavior)

### Pattern 2: Return Complex Results with Custom Formatting

**Example: `az aks command invoke`**
```python
def aks_run_command_invoke(...):
    # ... execute command ...
    return cmdResult  # Returns dictionary with exitCode, logs, provisioningState
```

**Table Transformer:**
```python
def aks_run_command_result_format(cmdResult):
    result = OrderedDict()
    if cmdResult['provisioningState'] == "Succeeded":
        result['exit code'] = cmdResult['exitCode']
        result['logs'] = cmdResult['logs']
        return result
    if cmdResult['provisioningState'] == "Failed":
        result['provisioning state'] = cmdResult['provisioningState']
        result['reason'] = cmdResult['reason']
        return result
    result['provisioning state'] = cmdResult['provisioningState']
    result['started At'] = cmdResult['startedAt']
    return result
```

### Pattern 3: Commands with Side Effects (Print to Console)

**Example: `az aks check-acr`**
```python
def aks_check_acr(cmd, client, resource_group_name, name, acr, node_name=None):
    # ... run checks ...
    if output:
        print(output)  # ⚠️ Exception to the rule - diagnostic output
    return return_msg
```

**Note:** This command is similar to ours - it's a diagnostic tool. It uses `print()` for console output but still returns structured data.

## Current aks-net-diagnostics Output

### Standalone Tool Output Structure

1. **Console Output** (plain text):
   - Header with cluster info
   - Analysis sections with findings
   - Color-coded severity (ERROR, WARNING, INFO)
   - Summary at the end
   - Progress indicators during execution

2. **JSON Report** (`--json-report`):
   - Complete structured output
   - All findings with details
   - Cluster information
   - Analysis metadata

### Example Output

```
================================================================================
AKS Network Diagnostics - v2.2.0
================================================================================

Cluster: my-cluster
Resource Group: my-rg
Subscription: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Region: eastus

[INFO] Fetching cluster information...
[INFO] Analyzing VNet configuration...

FINDINGS:
--------
[ERROR] Private DNS Zone not configured
  - Private cluster requires Private DNS Zone
  - Impact: Nodes cannot resolve API server
  - Recommendation: Configure Private DNS Zone

[WARNING] NSG rule allows 0.0.0.0/0
  - Rule 'AllowInternet' is too permissive
  - Recommendation: Restrict to specific IPs

SUMMARY:
--------
Total Findings: 2
Errors: 1
Warnings: 1
Info: 0
```

## Integration Challenges

### Challenge 1: Custom Text Output vs. Structured Data

**Problem:**
- aks-net-diagnostics produces rich formatted text output
- Azure CLI expects structured data (dicts/lists)
- Users are used to the current text format

**Options:**

#### Option A: Return Structured Data Only (Recommended)
**Approach:**
- Return Python dictionary with findings
- Create custom table transformer for `--output table`
- Users can use `--output json` for full data
- Logs/progress go to `logger.info()`

**Pros:**
- ✅ Follows Azure CLI guidelines
- ✅ Supports all output formats
- ✅ Integrates with jq, grep, etc.
- ✅ Consistent with other az commands

**Cons:**
- ❌ Table output won't be as rich as current text format
- ❌ Users need to learn `--output json | jq` for complex queries

**Example Return:**
```python
return {
    "cluster": {
        "name": "my-cluster",
        "resourceGroup": "my-rg",
        "subscription": "...",
        "region": "eastus"
    },
    "findings": [
        {
            "category": "dns",
            "severity": "error",
            "title": "Private DNS Zone not configured",
            "description": "Private cluster requires Private DNS Zone",
            "impact": "Nodes cannot resolve API server",
            "recommendation": "Configure Private DNS Zone",
            "details": { ... }
        }
    ],
    "summary": {
        "totalFindings": 2,
        "errors": 1,
        "warnings": 1,
        "info": 0
    }
}
```

**Table Transformer:**
```python
def aks_net_diagnostics_table_format(result):
    # Show summary + findings list
    findings = []
    for finding in result.get('findings', []):
        findings.append(OrderedDict([
            ('severity', finding['severity'].upper()),
            ('category', finding['category']),
            ('title', finding['title']),
            ('recommendation', finding['recommendation'][:50] + '...')
        ]))
    return findings
```

#### Option B: Hybrid Approach
**Approach:**
- Return structured data
- Use `logger.info()` to print formatted analysis to console during execution
- Structured data available for `--output json`

**Pros:**
- ✅ Preserves rich console experience
- ✅ Still supports all output formats
- ✅ Best of both worlds

**Cons:**
- ⚠️ Console output appears regardless of `--output` setting
- ⚠️ Might be confusing (text to console + JSON/table output)

**Example:**
```python
def aks_net_diagnostics(cmd, name, resource_group_name, ...):
    logger.info("=" * 80)
    logger.info("AKS Network Diagnostics - v2.2.0")
    logger.info("=" * 80)
    
    # ... analysis ...
    
    for finding in findings:
        severity_marker = "[ERROR]" if finding.severity == "error" else "[WARNING]"
        logger.info(f"{severity_marker} {finding.title}")
        logger.info(f"  - {finding.description}")
    
    # Return structured data
    return {
        "findings": findings,
        "summary": summary
    }
```

#### Option C: Keep `--json-report` Flag + Return Structured Data
**Approach:**
- Use `logger.info()` for console output (like current tool)
- Return structured data for CLI's output system
- Keep `--json-report` flag to save separate detailed JSON file

**Pros:**
- ✅ Most backward compatible
- ✅ Rich console experience
- ✅ Separate detailed report file
- ✅ Still supports all CLI output formats

**Cons:**
- ⚠️ Duplication: JSON output from both `--output json` and `--json-report`
- ⚠️ Users might be confused about difference

### Challenge 2: Progress Indicators

**Problem:**
- aks-net-diagnostics shows progress: "Analyzing VNet...", "Testing connectivity..."
- Long-running operations (especially `--probe-test`)

**Solution:**
Use `logger.info()` for progress messages - these go to stderr and don't interfere with structured output.

```python
logger.info("Fetching cluster information...")
cluster_info = get_cluster(...)
logger.info("✓ Cluster information retrieved")

logger.info("Analyzing network security groups...")
nsg_findings = analyze_nsgs(...)
logger.info(f"✓ Found {len(nsg_findings)} NSG issues")
```

### Challenge 3: `--details` Flag

**Problem:**
- Current tool has `--details` flag for verbose output
- In Azure CLI, this is typically handled by output format

**Solution:**
- Keep `--details` flag to control what's included in structured return
- Minimal mode: Just summary and findings
- Details mode: Include full analysis, raw data, test results

```python
if details:
    result["analysis_details"] = {
        "vnet_config": {...},
        "nsg_rules": [...],
        "route_tables": [...],
        "test_results": [...]
    }
```

## Recommended Approach

### Option A + Custom Table Formatter (Recommended)

**Rationale:**
1. Follows Azure CLI best practices
2. Users already expect this pattern from other az commands
3. Rich data available via `--output json`
4. Can still show progress via logger
5. Table output can show summary + key findings

**Implementation Steps:**

1. **Return Structure:**
```python
{
    "cluster": {...},
    "findings": [...],
    "summary": {...},
    "analysisDetails": {...}  # When --details is specified
}
```

2. **Table Transformer:**
   - Show findings list with severity, category, title
   - Add summary footer

3. **Console Feedback:**
   - Use `logger.info()` for progress
   - Keep it minimal (just major steps)

4. **JSON Report Flag:**
   - Keep `--json-report` for detailed file output
   - Make it more comprehensive than `--output json`
   - Include full test results, raw data

**Example Usage:**

```bash
# Table output (default)
az aks net-diagnostics -n cluster -g rg
# Shows:
# SEVERITY  CATEGORY  TITLE                           RECOMMENDATION
# ERROR     dns       Private DNS not configured      Configure Private DNS Zone
# WARNING   nsg       NSG rule too permissive         Restrict to specific IPs
# 
# Summary: 2 findings (1 error, 1 warning)

# JSON output
az aks net-diagnostics -n cluster -g rg --output json
# Full structured JSON to stdout

# Table with details
az aks net-diagnostics -n cluster -g rg --details
# More columns in table

# JSON with details + save report
az aks net-diagnostics -n cluster -g rg --details --json-report report.json --output json
# Structured JSON to stdout + detailed report to file
```

## Implementation Plan

### Phase 1: Restructure Output (During Integration)

1. **Modify orchestrator to return dictionary:**
```python
def run(self):
    findings = []
    # ... analysis ...
    
    return {
        "cluster": self.cluster_info,
        "findings": [f.to_dict() for f in findings],
        "summary": {
            "totalFindings": len(findings),
            "errors": sum(1 for f in findings if f.severity == "error"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "info": sum(1 for f in findings if f.severity == "info")
        }
    }
```

2. **Use logger for progress:**
```python
logger.info("Analyzing VNet configuration...")
# ... analysis ...
logger.info(f"✓ VNet analysis complete ({len(vnet_findings)} findings)")
```

3. **Create table transformer:**
```python
# In _format.py
def aks_net_diagnostics_table_format(result):
    findings = []
    for f in result.get('findings', []):
        findings.append(OrderedDict([
            ('severity', f['severity'].upper()),
            ('category', f['category']),
            ('title', f['title']),
            ('impact', f.get('impact', '')[:40])
        ]))
    return findings
```

4. **Register with table transformer:**
```python
# In commands.py
g.custom_command('net-diagnostics', 
                'aks_net_diagnostics',
                supports_no_wait=False,
                table_transformer=aks_net_diagnostics_table_format)
```

### Phase 2: Enhance JSON Report

Keep `--json-report` but make it even more comprehensive:
- Include all raw data
- Include full test outputs
- Include timestamps
- Include CLI version, tool version
- Make it suitable for offline analysis

## Questions for Consideration

1. **Should we keep color coding?**
   - Table output doesn't support colors
   - Could use symbols instead: ❌ ⚠️ ℹ️

2. **How much to show in table mode by default?**
   - Just findings list?
   - Include summary footer?
   - Show cluster info header?

3. **Should `--details` add columns to table?**
   - Or just include more in JSON return?

4. **Should `--json-report` be deprecated?**
   - Or keep it as "enhanced detailed report"?

## Recommendation Summary

**Adopt Option A with these specifics:**

1. ✅ Return structured Python dictionary
2. ✅ Create custom table transformer
3. ✅ Use `logger.info()` for progress/status
4. ✅ Keep `--json-report` for enhanced detailed output
5. ✅ Support `--details` flag (controls what's in return dict)
6. ✅ All output formats work automatically

**Benefits:**
- Follows Azure CLI patterns
- Users can use jq, grep, etc.
- Works with `--query` parameter
- Integrates with Azure CLI ecosystem
- Still provides rich analysis

**Trade-offs:**
- Table output won't be as pretty as current text
- Need to educate users on `--output json` for full data
- Some formatting changes required in codebase
