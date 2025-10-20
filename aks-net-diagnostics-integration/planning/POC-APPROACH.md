# POC Approach: Simplified Integration Strategy

**Date:** October 19, 2025  
**Purpose:** Define simplified approach for Proof of Concept phase

## Objective

Build a working POC of Azure CLI with `az aks net-diagnostics` subcommand to **prove feasibility** of integration before investing in full refinement.

## Simplified Approach

### What We're Doing for POC

1. **Keep Existing Output Format**
   - Use aks-net-diagnostics' current text output with colors
   - Keep `--json-report` flag functionality
   - Similar to how `az aks check-acr` uses `print()` for diagnostic output

2. **Minimal Code Changes**
   - Adapt authentication (DefaultAzureCredential → CLI credentials)
   - Integrate argument parsing
   - Add as subcommand to `az aks`
   - No output refactoring

3. **Focus on Integration Points**
   - Authentication adapter
   - Command registration
   - Argument mapping
   - Basic functionality

### What We're Deferring to Post-POC

1. **Output Format Refinement**
   - Azure CLI standard output modes (--output json/table/yaml/tsv)
   - Table transformers
   - Structured data return
   - *(See OUTPUT-FORMAT-ANALYSIS.md for full analysis)*

2. **Advanced Features**
   - Comprehensive error handling
   - Advanced testing
   - Performance optimization
   - Documentation

3. **Code Optimization**
   - Refactoring for CLI patterns
   - Code cleanup
   - Best practices alignment

## POC Success Criteria

A successful POC means we can:

✅ Run: `az aks net-diagnostics -n myCluster -g myRG`  
✅ See diagnostic output (same as standalone tool)  
✅ Use flags: `--details`, `--probe-test`, `--json-report`  
✅ Authentication works with Azure CLI credentials  
✅ No major architectural blockers identified  

## Benefits of POC Approach

1. **Faster Validation**
   - Prove integration is feasible
   - Identify real blockers early
   - Avoid premature optimization

2. **Lower Risk**
   - Don't refactor output until integration proven
   - Can abandon if major issues found
   - Easier to iterate

3. **Clear Decision Point**
   - After POC: decide if full integration worth it
   - Can assess effort vs. value
   - Can plan post-POC work with real data

## Implementation Strategy

### Phase 2: Code Preparation (Unchanged)
- Clone aks-net-diagnostics (azure-sdk branch)
- Set up azdev environment
- Analyze existing code

### Phase 3: Create Authentication Adapter (Simplified)
**Original Plan:** Create wrapper for Azure SDK client
**POC Approach:** Create minimal adapter that:
- Takes `cmd.cli_ctx` from Azure CLI
- Provides credentials to aks-net-diagnostics
- No other changes to tool's code

```python
# Simple adapter
class CLIAuthenticationAdapter:
    def __init__(self, cli_ctx):
        self.cli_ctx = cli_ctx
    
    def get_credential(self):
        # Return credential compatible with aks-net-diagnostics
        return self.cli_ctx.get_credential()
```

### Phase 4: Integrate Code (Simplified)
**Keep:**
- All aks-net-diagnostics modules as-is
- Existing output format
- Existing argument structure

**Change:**
- Add command registration in commands.py
- Add command function in custom.py
- Map CLI arguments to tool parameters

```python
# In custom.py
def aks_net_diagnostics(cmd, name, resource_group_name, 
                       details=False, probe_test=False, 
                       json_report=None):
    # Get credentials from CLI
    credential = cmd.cli_ctx.get_credential()
    
    # Run diagnostics (existing code)
    orchestrator = DiagnosticsOrchestrator(
        cluster_name=name,
        resource_group=resource_group_name,
        credential=credential,
        details=details,
        probe_test=probe_test,
        json_report=json_report
    )
    
    result = orchestrator.run()
    
    # For POC: just return result (let tool handle output)
    return result
```

### Phase 5: Testing (Simplified)
**Focus on:**
- Does command run?
- Does authentication work?
- Do arguments pass through?
- Does output appear?

**Skip for POC:**
- Comprehensive unit tests
- Output format tests
- Edge case testing

### Phase 6: Documentation (Minimal)
- Basic README
- How to build and test
- Known limitations

## Timeline Adjustment

### Original Timeline: 33-48 hours
- Phase 1: 5-6 hours ✅ COMPLETE
- Phase 2: 4-5 hours
- Phase 3: 6-8 hours
- Phase 4: 8-12 hours
- Phase 5: 6-10 hours
- Phase 6: 4-7 hours

### POC Timeline: ~25-35 hours
- Phase 1: 5-6 hours ✅ COMPLETE
- Phase 2: 4-5 hours (unchanged)
- Phase 3: 3-4 hours (simplified - minimal adapter)
- Phase 4: 6-8 hours (simplified - keep output as-is)
- Phase 5: 3-5 hours (basic testing only)
- Phase 6: 2-3 hours (minimal docs)

**Savings:** ~10-15 hours by deferring output refactoring

## Post-POC Decision Tree

After POC is working:

### If Successful ✅
**Options:**
1. **Keep as-is** - Ship with text output (like az aks check-acr)
2. **Refactor output** - Implement structured data + table transformers (see OUTPUT-FORMAT-ANALYSIS.md)
3. **Hybrid** - Structured data but keep rich console experience

**Decision factors:**
- User feedback
- Maintenance burden
- Consistency with other commands
- Value of additional output formats

### If Major Blockers Found ❌
**Possible Issues:**
- Authentication adapter too complex
- Performance problems
- Dependency conflicts
- Architecture incompatibilities

**Response:**
- Document blockers
- Assess workarounds
- Decide if integration viable

## Next Steps

1. ✅ Update planning documents to reflect POC approach
2. ⏭️ Begin Phase 2: Clone repo and set up environment
3. ⏭️ Phase 3: Create minimal authentication adapter
4. ⏭️ Phase 4: Integrate with minimal changes
5. ⏭️ Test POC
6. ⏭️ Evaluate and decide on post-POC work

## References

- **OUTPUT-FORMAT-ANALYSIS.md** - Full analysis of output formatting options (for post-POC)
- **03-task-list.md** - Updated with POC approach
- **05-questions-and-decisions.md** - Q2 marked as deferred
