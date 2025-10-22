# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
AKS Network Diagnostics Orchestrator
Adapted from aks-net-diagnostics tool (azure-sdk branch) for Azure CLI integration
"""

import logging
import sys
from typing import Any, Dict, List, Optional

from azure.cli.command_modules.acs.net_diagnostics._version import __version__
from azure.cli.command_modules.acs.net_diagnostics.api_server_analyzer import (
    APIServerAccessAnalyzer
)
from azure.cli.command_modules.acs.net_diagnostics.cluster_data_collector import (
    ClusterDataCollector
)
from azure.cli.command_modules.acs.net_diagnostics.connectivity_tester import (
    ConnectivityTester
)
from azure.cli.command_modules.acs.net_diagnostics.dns_analyzer import DNSAnalyzer
from azure.cli.command_modules.acs.net_diagnostics.misconfiguration_analyzer import (
    MisconfigurationAnalyzer
)
from azure.cli.command_modules.acs.net_diagnostics.models import FindingCode
from azure.cli.command_modules.acs.net_diagnostics.nsg_analyzer import NSGAnalyzer
from azure.cli.command_modules.acs.net_diagnostics.outbound_analyzer import (
    OutboundConnectivityAnalyzer
)
from azure.cli.command_modules.acs.net_diagnostics.report_generator import (
    ReportGenerator
)
from azure.cli.command_modules.acs.net_diagnostics.route_table_analyzer import (
    RouteTableAnalyzer
)


def run_diagnostics(  # pylint: disable=too-many-locals
    aks_client,
    agent_pools_client,
    network_client,
    compute_client,
    privatedns_client,
    credential,
    resource_group_name: str,
    cluster_name: str,
    subscription_id: str,
    details: bool = False,
    probe_test: bool = False,
    json_report_path: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Run comprehensive network diagnostics on an AKS cluster.

    This function orchestrates all diagnostic modules to analyze:
    - Cluster configuration
    - VNet and subnet configuration
    - Outbound connectivity
    - Network Security Groups
    - Private DNS configuration
    - API server access
    - Connectivity tests (if probe_test enabled)
    - Misconfigurations

    Args:
        aks_client: ContainerServiceClient for AKS operations
        agent_pools_client: AgentPoolsOperations for agent pool operations
        network_client: NetworkManagementClient for network operations
        compute_client: ComputeManagementClient for VMSS operations
        privatedns_client: PrivateDnsManagementClient for DNS operations
        credential: Azure credential for cross-subscription scenarios
        resource_group_name: Resource group name
        cluster_name: AKS cluster name
        subscription_id: Azure subscription ID
        details: Show detailed output
        probe_test: Enable active connectivity checks (executes commands on nodes)
        json_report_path: Path to save JSON report (if provided)
        logger: Optional logger instance

    Returns:
        Dictionary containing complete diagnostic results

    Raises:
        CLIError: If cluster not found or other validation errors
    """
    # Setup logger if not provided
    if logger is None:
        logger = _setup_logging()

    # Use warning level for progress messages so they show in Azure CLI
    logger.warning("Starting AKS network diagnostics for cluster: %s", cluster_name)

    # Create clients dictionary for analyzers
    clients = {
        "aks_client": aks_client,
        "network_client": network_client,
        "compute_client": compute_client,
        "privatedns_client": privatedns_client,
        "subscription_id": subscription_id,
        "credential": credential
    }

    # Initialize result containers
    findings: List[Dict[str, Any]] = []
    cluster_info: Dict[str, Any] = {}
    agent_pools: List[Dict[str, Any]] = []
    vnets_analysis: List[Dict[str, Any]] = []
    outbound_analysis: Dict[str, Any] = {}
    outbound_ips: List[str] = []
    private_dns_analysis: Dict[str, Any] = {}
    api_server_access_analysis: Dict[str, Any] = {}
    vmss_analysis: List[Dict[str, Any]] = []
    nsg_analysis: Dict[str, Any] = {}
    api_probe_results: Optional[Dict[str, Any]] = None

    # Phase 1: Collect cluster information
    logger.warning("[1/9] Collecting cluster information...")
    collector = ClusterDataCollector(
        aks_client=aks_client,
        agent_pools_client=agent_pools_client,
        network_client=network_client,
        compute_client=compute_client,
        logger=logger
    )
    cluster_data = collector.collect_cluster_info(
        cluster_name,
        resource_group_name
    )
    cluster_info = cluster_data["cluster_info"]
    agent_pools = cluster_data["agent_pools"]

    # Phase 2: Analyze VNet configuration
    logger.warning("[2/9] Analyzing VNet configuration...")
    vnets_analysis = collector.collect_vnet_info(agent_pools)

    # Collect VMSS configuration (needed for Route Table analysis)
    logger.warning("  Collecting VMSS network configuration...")
    vmss_analysis = collector.collect_vmss_info(cluster_info)

    # Check if we have permission issues that might affect subsequent analysis
    has_vmss_permission_issues = any(
        f.code in [
            FindingCode.PERMISSION_INSUFFICIENT_VMSS,
            FindingCode.PERMISSION_INSUFFICIENT_VNET
        ]
        for f in collector.findings
    )

    # Phase 3: Analyze User Defined Routes (UDRs)
    logger.warning("[3/9] Analyzing Route Tables (UDRs)...")
    route_table_analyzer = RouteTableAnalyzer(
        agent_pools=agent_pools,
        vmss_analysis=vmss_analysis,
        network_client=clients.get('network_client'),
        logger=logger
    )
    route_table_analysis = route_table_analyzer.analyze()

    # Add note if route table analysis is incomplete due to permissions
    if has_vmss_permission_issues and not route_table_analysis.get("route_tables"):
        route_table_analysis["incomplete_due_to_permissions"] = True
        logger.warning(
            "  Route table analysis may be incomplete due to "
            "insufficient permissions to read VMSS/VNet configuration"
        )

    # Phase 4: Analyze outbound connectivity
    logger.warning("[4/9] Analyzing outbound connectivity...")
    outbound_analyzer = OutboundConnectivityAnalyzer(
        cluster_info=cluster_info,
        agent_pools=agent_pools,
        clients=clients,
        route_table_analysis=route_table_analysis,
        logger=logger
    )
    outbound_analysis = outbound_analyzer.analyze(show_details=details)
    outbound_ips = outbound_analyzer.get_outbound_ips()

    # Add UDR analysis to outbound analysis (expected by misconfiguration analyzer)
    outbound_analysis["udr_analysis"] = route_table_analysis

    # Phase 6: Analyze Network Security Groups...
    logger.warning("[6/9] Analyzing Network Security Groups...")
    nsg_analyzer = NSGAnalyzer(
        clients=clients,
        cluster_info=cluster_info,
        vmss_info=vmss_analysis,
        logger=logger
    )
    nsg_analysis = nsg_analyzer.analyze()

    # Add note if NSG analysis is incomplete due to permissions
    if has_vmss_permission_issues and nsg_analysis.get("nsgs_analyzed", 0) == 0:
        nsg_analysis["incomplete_due_to_permissions"] = True
        logger.warning(
            "  NSG analysis may be incomplete due to "
            "insufficient permissions to read VMSS/VNet configuration"
        )

    # Phase 7: Analyze Private DNS configuration
    logger.warning("[7/9] Analyzing Private DNS configuration...")
    dns_analyzer = DNSAnalyzer(clients=clients, cluster_info=cluster_info, logger=logger)
    private_dns_analysis = dns_analyzer.analyze()

    # Phase 8: Analyze API server access
    logger.warning("[8/9] Analyzing API server access configuration...")
    api_server_analyzer = APIServerAccessAnalyzer(
        cluster_info=cluster_info,
        outbound_ips=outbound_ips,
        outbound_analysis=outbound_analysis,
        logger=logger
    )
    api_server_access_analysis = api_server_analyzer.analyze()

    # Phase 9: Run connectivity tests (if enabled)
    if probe_test:
        logger.warning("[9/9] Running connectivity tests (probe mode enabled)...")
        connectivity_tester = ConnectivityTester(
            cluster_info=cluster_info,
            clients=clients,
            dns_analyzer=dns_analyzer,
            show_details=details,
            logger=logger
        )
        api_probe_results = connectivity_tester.test_connectivity(
            enable_probes=True
        )
    else:
        logger.warning(
            "[9/9] Skipping connectivity tests "
            "(use --probe-test to enable)"
        )
        api_probe_results = {"skipped": True, "reason": "Not requested"}

    # Phase 9: Analyze misconfigurations and generate findings
    logger.warning("Analyzing potential misconfigurations...")

    # First, collect permission findings from data collection phase
    permission_findings = []
    if hasattr(collector, 'findings') and collector.findings:
        logger.debug("Collecting %d findings from cluster data collector", len(collector.findings))
        permission_findings.extend([f.to_dict() for f in collector.findings])

    if hasattr(outbound_analyzer, 'findings') and outbound_analyzer.findings:
        logger.debug("Collecting %d findings from outbound analyzer", len(outbound_analyzer.findings))
        permission_findings.extend([f.to_dict() for f in outbound_analyzer.findings])

    if hasattr(dns_analyzer, 'findings') and dns_analyzer.findings:
        logger.debug("Collecting %d findings from DNS analyzer", len(dns_analyzer.findings))
        permission_findings.extend([f.to_dict() for f in dns_analyzer.findings])

    # Run misconfiguration analysis with permission findings context
    misconfiguration_analyzer = MisconfigurationAnalyzer(
        clients=clients,
        logger=logger
    )
    findings, _ = misconfiguration_analyzer.analyze(
        cluster_info=cluster_info,
        outbound_analysis=outbound_analysis,
        outbound_ips=outbound_ips,
        private_dns_analysis=private_dns_analysis,
        api_server_access_analysis=api_server_access_analysis,
        nsg_analysis=nsg_analysis,
        api_probe_results=api_probe_results,
        vmss_analysis=vmss_analysis,
        permission_findings=permission_findings
    )

    # Add permission findings to the final findings list
    findings.extend(permission_findings)

    # Collect findings from individual analyzers
    # DNS analyzer creates findings via add_finding() but they're not
    # included in misconfiguration_analyzer's findings
    if hasattr(dns_analyzer, 'findings') and dns_analyzer.findings:
        logger.debug("Collecting %d findings from DNS analyzer", len(dns_analyzer.findings))
        # Convert Finding objects to dicts for report generator
        findings.extend([f.to_dict() for f in dns_analyzer.findings])

    if hasattr(nsg_analyzer, 'findings') and nsg_analyzer.findings:
        logger.debug("Collecting %d findings from NSG analyzer", len(nsg_analyzer.findings))
        # Convert Finding objects to dicts for report generator
        findings.extend([f.to_dict() for f in nsg_analyzer.findings])

    # Phase 10: Generate report
    logger.info("Generating diagnostic report...")
    report_generator = ReportGenerator(
        cluster_name=cluster_name,
        resource_group=resource_group_name,
        subscription=subscription_id,
        cluster_info=cluster_info,
        findings=findings,
        vnets_analysis=vnets_analysis,
        route_table_analysis=route_table_analysis,
        outbound_analysis=outbound_analysis,
        outbound_ips=outbound_ips,
        private_dns_analysis=private_dns_analysis,
        api_server_access_analysis=api_server_access_analysis,
        vmss_analysis=vmss_analysis,
        nsg_analysis=nsg_analysis,
        api_probe_results=api_probe_results,
        failure_analysis={"enabled": False},
        script_version=__version__,
        logger=logger
    )

    # Generate JSON report if requested
    if json_report_path:
        report_generator.save_json_report(json_report_path)

    # Print console report
    report_generator.print_console_report(
        show_details=details,
        json_report_path=json_report_path
    )

    # Return complete diagnostic data
    result = report_generator.generate_json_report()

    logger.info("Diagnostic analysis complete")

    return result


def _setup_logging() -> logging.Logger:
    """
    Configure logging with appropriate handlers and formatters.

    Returns:
        Configured logger instance
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger("aks_net_diagnostics")
    logger.propagate = False

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)

    return logger
