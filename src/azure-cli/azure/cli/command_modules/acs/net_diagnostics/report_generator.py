"""
Report Generator for AKS Network Diagnostics

This module handles generating and formatting diagnostic reports in multiple
formats:
- Console output (summary and detailed modes)
- JSON output for programmatic consumption
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ReportGenerator:  # pylint: disable=too-many-instance-attributes
    """Generates diagnostic reports in various formats"""

    def __init__(
        self,
        cluster_name: str,
        resource_group: str,
        subscription: str,
        *,
        cluster_info: Dict[str, Any],
        findings: List[Dict[str, Any]],
        vnets_analysis: List[Dict[str, Any]],
        route_table_analysis: Dict[str, Any],
        outbound_analysis: Dict[str, Any],
        outbound_ips: List[str],
        private_dns_analysis: Dict[str, Any],
        api_server_access_analysis: Dict[str, Any],
        vmss_analysis: List[Dict[str, Any]],
        nsg_analysis: Dict[str, Any],
        api_probe_results: Optional[Dict[str, Any]] = None,
        failure_analysis: Optional[Dict[str, Any]] = None,
        script_version: str = "2.2.0",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the ReportGenerator

        Args:
            cluster_name: AKS cluster name
            resource_group: Resource group name
            subscription: Azure subscription ID
            cluster_info: Cluster configuration dictionary
            findings: List of diagnostic findings
            vnets_analysis: VNet analysis results
            route_table_analysis: Route table/UDR analysis results
            outbound_analysis: Outbound connectivity analysis
            outbound_ips: List of outbound public IPs
            private_dns_analysis: Private DNS analysis results
            api_server_access_analysis: API server access analysis
            vmss_analysis: VMSS configuration analysis
            nsg_analysis: NSG analysis results
            api_probe_results: API connectivity probe results
            failure_analysis: Failure analysis results
            script_version: Script version number
            logger: Optional logger instance
        """
        self.cluster_name = cluster_name
        self.resource_group = resource_group
        self.subscription = subscription
        self.cluster_info = cluster_info
        self.findings = findings
        self.vnets_analysis = vnets_analysis
        self.route_table_analysis = route_table_analysis
        self.outbound_analysis = outbound_analysis
        self.outbound_ips = outbound_ips
        self.private_dns_analysis = private_dns_analysis
        self.api_server_access_analysis = api_server_access_analysis
        self.vmss_analysis = vmss_analysis
        self.nsg_analysis = nsg_analysis
        self.api_probe_results = api_probe_results
        self.failure_analysis = failure_analysis or {"enabled": False}
        self.script_version = script_version
        self.logger = logger or logging.getLogger(__name__)

    def generate_json_report(self) -> Dict[str, Any]:
        """
        Generate JSON report data

        Returns:
            Dictionary containing complete report data
        """
        return {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": self.script_version,
                "generated_by": "AKS Network Diagnostics Script (Python)",
            },
            "cluster": {
                "name": self.cluster_name,
                "resource_group": self.resource_group,
                "subscription": self.subscription,
                "provisioning_state": self.cluster_info.get(
                    "provisioning_state",
                    ""
                ),
                "location": self.cluster_info.get("location", ""),
                "node_resource_group": self.cluster_info.get(
                    "node_resource_group",
                    ""
                ),
                "network_profile": self.cluster_info.get(
                    "network_profile",
                    {}
                ),
                "api_server_access": self.cluster_info.get(
                    "api_server_access_profile",
                    {}
                ),
            },
            "networking": {
                "vnets": self.vnets_analysis,
                "outbound": self.outbound_analysis,
                "private_dns": self.private_dns_analysis,
                "api_server_access": self.api_server_access_analysis,
                "vmss_configuration": self.vmss_analysis,
                "nsg_configuration": self.nsg_analysis,
                "routing_analysis": {
                    "outbound_type": (
                        self.cluster_info.get("network_profile", {}).get(
                            "outbound_type",
                            "loadBalancer"
                        )
                    ),
                    "udr_analysis": (
                        self.outbound_analysis.get("udr_analysis")
                    ),
                },
            },
            "diagnostics": {
                "api_connectivity_probe": self.api_probe_results,
                "failure_analysis": self.failure_analysis,
                "findings": self.findings,
            },
        }

    def save_json_report(
        self,
        filepath: str,
        file_permissions: int = 0o600
    ) -> bool:
        """
        Save JSON report to file

        Args:
            filepath: Path to save the JSON report
            file_permissions: File permissions (default: owner read/write only)

        Returns:
            True if successful, False otherwise
        """
        try:
            report_data = self.generate_json_report()

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)

            # Set secure file permissions
            os.chmod(filepath, file_permissions)
            self.logger.info("[DOC] JSON report saved to: %s", filepath)
            return True

        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Failed to save JSON report: %s", e)
            return False

    def print_console_report(
        self,
        show_details: bool = False,
        json_report_path: Optional[str] = None
    ):
        """
        Print console report

        Args:
            show_details: Enable detailed output
            json_report_path: Path to JSON report if saved
        """
        print("\n" + "=" * 74)

        if show_details:
            self._print_detailed_report()
        else:
            self._print_summary_report(json_report_path)

        print("\n[OK] AKS network assessment completed successfully!")

    def _print_summary_report(self, json_report_path: Optional[str] = None):
        """Print summary report"""
        print("# AKS Network Assessment Summary")
        print()
        print(
            f"**Cluster:** {self.cluster_name} "
            f"({self.cluster_info.get('provisioning_state', 'Unknown')})"
        )
        print(f"**Resource Group:** {self.resource_group}")
        print(
            f"**Generated:** "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        print()

        print("**Configuration:**")
        network_profile = self.cluster_info.get("network_profile", {})
        print(
            f"- Network Plugin: "
            f"{network_profile.get('network_plugin', 'kubenet')}"
        )
        print(
            f"- Outbound Type: "
            f"{network_profile.get('outbound_type', 'loadBalancer')}"
        )

        api_server_profile = self.cluster_info.get("api_server_access_profile")
        is_private = (
            api_server_profile.get("enable_private_cluster", False)
            if api_server_profile else False
        )
        print(f"- Private Cluster: {str(is_private).lower()}")

        if (self.outbound_ips or
                (self.outbound_analysis and
                 self.outbound_analysis.get("effective_outbound"))):
            print()
            print("**Outbound Configuration:**")

            effective_outbound = (
                self.outbound_analysis.get("effective_outbound", {})
                if self.outbound_analysis else {}
            )

            if effective_outbound.get("overridden_by_udr"):
                # UDR overrides the load balancer
                print("- Configured Load Balancer IPs (not effective):")
                for ip in self.outbound_ips:
                    print(f"  - {ip}")
                print("- Effective Outbound (via UDR):")
                for ip in effective_outbound.get("virtual_appliance_ips", []):
                    print(f"  - Virtual Appliance: {ip}")
            else:
                # No UDR override, show based on configured mechanism
                outbound_type = (
                    self.outbound_analysis.get("type", "loadBalancer")
                    if self.outbound_analysis else "loadBalancer"
                )

                if outbound_type == "loadBalancer" and self.outbound_ips:
                    print("- Load Balancer IPs:")
                    for ip in self.outbound_ips:
                        print(f"  - {ip}")
                elif (outbound_type == "userDefinedRouting" and
                      effective_outbound.get("virtual_appliance_ips")):
                    print("- Virtual Appliance IPs:")
                    for ip in effective_outbound.get(
                        "virtual_appliance_ips",
                        []
                    ):
                        print(f"  - {ip}")
                elif self.outbound_ips:
                    # Fallback to showing configured IPs
                    print("- Outbound IPs:")
                    for ip in self.outbound_ips:
                        print(f"  - {ip}")

        # Show connectivity test results if probe tests were run
        if self.api_probe_results and isinstance(self.api_probe_results, dict):
            # Check if tests were skipped
            if self.api_probe_results.get("skipped"):
                # Don't show anything if skipped (user didn't request --probe-test)
                pass
            elif self.api_probe_results.get("enabled"):
                # Tests were run
                print()
                print("**Connectivity Tests:**")
                
                summary = self.api_probe_results.get("summary", {})
                total_tests = summary.get("total_tests", 0)
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                errors = summary.get("errors", 0)
                
                if total_tests == 0:
                    print("- No connectivity tests were performed")
                elif failed == 0 and errors == 0:
                    print(f"- [OK] All {passed}/{total_tests} connectivity tests passed")
                else:
                    print(
                        f"- [WARNING] {failed + errors}/{total_tests} "
                        f"connectivity tests failed"
                    )
                    print(f"  - Passed: {passed}, Failed: {failed}, Errors: {errors}")

        print()
        print("**Findings Summary:**")

        critical_findings = [
            f for f in self.findings
            if f.get("severity") in ["critical", "error"]
        ]
        warning_findings = [
            f for f in self.findings
            if f.get("severity") == "warning"
        ]

        if len(critical_findings) == 0 and len(warning_findings) == 0:
            print("- [OK] No critical issues detected")
        else:
            # Show critical/error findings
            for finding in critical_findings:
                # For cluster operation failures, show only the error code
                # in summary mode
                if (finding.get("code") == "CLUSTER_OPERATION_FAILURE" and
                        finding.get("error_code")):
                    print(
                        f"- [ERROR] Cluster failed with error: "
                        f"{finding.get('error_code')}"
                    )
                else:
                    message = finding.get("message", "Unknown issue")
                    print(f"- [ERROR] {message}")

            # Show warning findings
            for finding in warning_findings:
                message = finding.get("message", "Unknown issue")
                print(f"- [WARNING] {message}")

        print()
        if json_report_path:
            print(f"[DOC] JSON report saved to: {json_report_path}")
        print("Tip: Use --details flag for detailed analysis")

    def _print_detailed_report(self):
        """Print detailed report"""
        print("# AKS Network Assessment Report")
        print()
        print(f"**Cluster:** {self.cluster_name}")
        print(f"**Resource Group:** {self.resource_group}")
        print(f"**Subscription:** {self.subscription}")
        print(
            f"**Generated:** "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        print()

        # Cluster overview
        self._print_cluster_overview()

        # Network configuration
        self._print_network_configuration()

        # Connectivity test results
        self._print_connectivity_tests()

        # NSG Analysis
        self._print_nsg_analysis()

        # Findings
        self._print_findings()

    def _print_cluster_overview(self):
        """Print cluster overview section"""
        print("## Cluster Overview")
        print()
        print("| Property | Value |")
        print("|----------|-------|")
        print(
            f"| Provisioning State | "
            f"{self.cluster_info.get('provisioning_state', '')} |"
        )

        # Show power state
        power_state = self.cluster_info.get("power_state", {})
        power_code = (
            power_state.get("code", "Unknown")
            if isinstance(power_state, dict)
            else str(power_state)
        )
        print(f"| Power State | {power_code} |")

        print(f"| Location | {self.cluster_info.get('location', '')} |")

        network_profile = self.cluster_info.get("network_profile", {})
        print(
            f"| Network Plugin | "
            f"{network_profile.get('network_plugin', 'kubenet')} |"
        )
        print(
            f"| Outbound Type | "
            f"{network_profile.get('outbound_type', 'loadBalancer')} |"
        )

        api_server_profile = self.cluster_info.get("api_server_access_profile")
        is_private = (
            api_server_profile.get("enable_private_cluster", False)
            if api_server_profile else False
        )
        print(f"| Private Cluster | {str(is_private).lower()} |")
        print()

    def _print_network_configuration(self):
        """Print network configuration section"""
        print("## Network Configuration")
        print()

        # Service Network
        network_profile = self.cluster_info.get("network_profile", {})
        print("### Service Network")
        print(f"- **Service CIDR:** {network_profile.get('service_cidr', '')}")
        print(
            f"- **DNS Service IP:** "
            f"{network_profile.get('dns_service_ip', '')}"
        )
        print(f"- **Pod CIDR:** {network_profile.get('pod_cidr', '')}")
        print()

        # API Server access
        self._print_api_server_access()

        # Outbound connectivity
        self._print_outbound_connectivity()

        # UDR Analysis
        self._print_udr_analysis()

    def _print_api_server_access(self):
        """Print API server access section"""
        print("### API Server Access")
        api_server_profile = self.cluster_info.get("api_server_access_profile")
        is_private = (
            api_server_profile.get("enable_private_cluster", False)
            if api_server_profile else False
        )

        if is_private and api_server_profile:
            print("- **Type:** Private cluster")

            # Try multiple sources for private FQDN
            private_fqdn = ""
            if api_server_profile.get("private_fqdn"):
                private_fqdn = api_server_profile.get("private_fqdn", "")
            elif self.cluster_info.get("private_fqdn"):
                private_fqdn = self.cluster_info.get("private_fqdn", "")

            print(f"- **Private FQDN:** {private_fqdn}")
            print(
                f"- **Private DNS Zone:** "
                f"{api_server_profile.get('private_dns_zone', '')}"
            )
        else:
            print("- **Type:** Public cluster")
            print(f"- **Public FQDN:** {self.cluster_info.get('fqdn', '')}")

        # Add authorized IP ranges information
        if api_server_profile:
            authorized_ranges = api_server_profile.get(
                "authorized_ip_ranges",
                []
            )
            if authorized_ranges:
                print(
                    f"- **Authorized IP Ranges:** "
                    f"{len(authorized_ranges)} range(s)"
                )
                for range_cidr in authorized_ranges:
                    print(f"  - {range_cidr}")

                # Show access implications if we have the analysis
                if self.api_server_access_analysis:
                    access_restrictions = (
                        self.api_server_access_analysis.get(
                            "access_restrictions",
                            {}
                        )
                    )
                    implications = access_restrictions.get(
                        "implications",
                        []
                    )
                    if implications:
                        print("- **Access Implications:**")
                        for implication in implications:
                            print(f"  {implication}")
            else:
                print(
                    "- **Access Restrictions:** None "
                    "(unrestricted public access)"
                )
                if not is_private:
                    print(
                        "  [WARNING] API server is accessible from any IP "
                        "address on the internet"
                    )

        print()

    def _print_outbound_connectivity(self):
        """Print outbound connectivity section"""
        if self.outbound_ips:
            network_profile = self.cluster_info.get("network_profile", {})
            print("### Outbound Connectivity")
            print(
                f"- **Type:** "
                f"{network_profile.get('outbound_type', 'loadBalancer')}"
            )
            print("- **Effective Public IPs:**")
            for ip in self.outbound_ips:
                print(f"  - {ip}")
            print()

    def _print_udr_analysis(self):
        """Print UDR analysis section"""
        udr_analysis = (
            self.outbound_analysis.get("udr_analysis")
            if self.outbound_analysis else None
        )
        if udr_analysis:
            print("### User Defined Routes Analysis")
            route_tables = udr_analysis.get("route_tables", [])
            if route_tables:
                print(f"- **Route Tables Found:** {len(route_tables)}")

                for rt in route_tables:
                    print(f"- **Route Table:** {rt.get('name', 'unnamed')}")
                    print(
                        f"  - **Resource Group:** "
                        f"{rt.get('resource_group', '')}"
                    )
                    print(
                        f"  - **BGP Propagation:** "
                        f"{'Disabled' if rt.get('disable_bgp_route_propagation') else 'Enabled'}"
                    )
                    print(f"  - **Routes:** {len(rt.get('routes', []))}")

                    # Show critical routes
                    critical_routes = [
                        r for r in rt.get("routes", [])
                        if r.get("impact", {}).get("severity") in [
                            "critical",
                            "high"
                        ]
                    ]
                    if critical_routes:
                        print("  - **Critical Routes:**")
                        for route in critical_routes:
                            impact = route.get("impact", {})
                            print(
                                f"    - {route.get('name', 'unnamed')} "
                                f"({route.get('address_prefix', '')}) -> "
                                f"{route.get('next_hop_type', '')} - "
                                f"{impact.get('description', '')}"
                            )

                # Show virtual appliance routes summary
                va_routes = udr_analysis.get("virtual_appliance_routes", [])
                if va_routes:
                    print(
                        f"- **Virtual Appliance Routes:** "
                        f"{len(va_routes)}"
                    )
                    for route in va_routes:
                        print(
                            f"  - {route.get('name', 'unnamed')} "
                            f"({route.get('address_prefix', '')}) -> "
                            f"{route.get('next_hop_ip_address', '')}"
                        )

                print()
            else:
                print("- **No route tables found on node subnets**")
                print()

    def _print_connectivity_tests(self):
        """Print connectivity test results section"""
        if self.api_probe_results:
            print("### Connectivity Tests")

            if self.api_probe_results.get("skipped"):
                reason = self.api_probe_results.get("reason", "Unknown reason")
                print(f"- **Status:** Skipped ({reason})")
                print()
            else:
                summary = self.api_probe_results.get("summary", {})
                total = summary.get("total_tests", 0)
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                errors = summary.get("errors", 0)

                print(f"- **Tests Executed:** {total}")
                if passed > 0:
                    print(f"- **[OK] Passed:** {passed}")
                if failed > 0:
                    print(f"- **[ERROR] Failed:** {failed}")
                if errors > 0:
                    print(f"- **[WARNING] Errors:** {errors}")

                # Show detailed results
                tests = self.api_probe_results.get("tests", [])
                if tests:
                    print("\n**Test Details:**")
                    for test in tests:
                        status_icon = {
                            "passed": "[OK]",
                            "failed": "[ERROR]",
                            "error": "[WARNING]",
                            "skipped": "[SKIP]",
                        }.get(test.get("status"), "[?]")

                        test_name = test.get("test_name", "Unknown Test")
                        vmss_name = test.get("vmss_name", "unknown")
                        exit_code = test.get("exit_code", -1)
                        print(
                            f"- {status_icon} **{test_name}** "
                            f"(VMSS: {vmss_name}, Exit Code: {exit_code})"
                        )

                        # Show full test result in JSON format with compacted
                        # newlines
                        test_copy = test.copy()
                        # Compact stdout and stderr for single-line display
                        if test_copy.get("stdout"):
                            test_copy["stdout"] = test_copy["stdout"].replace(
                                "\n",
                                "\\n"
                            )
                        if test_copy.get("stderr"):
                            test_copy["stderr"] = test_copy["stderr"].replace(
                                "\n",
                                "\\n"
                            )

                        print("  - **Full Test Result:**")
                        print("    ```json")
                        print(f"    {json.dumps(test_copy, indent=2)}")
                        print("    ```")
                print()

    def _print_nsg_analysis(self):
        """Print NSG analysis section"""
        if self.nsg_analysis:
            print("### Network Security Group (NSG) Analysis")

            # NSG Analysis Summary
            subnet_nsgs = self.nsg_analysis.get("subnet_nsgs", [])
            nic_nsgs = self.nsg_analysis.get("nic_nsgs", [])
            total_nsgs = len(subnet_nsgs) + len(nic_nsgs)
            blocking_rules = self.nsg_analysis.get("blocking_rules", [])
            inter_node_communication = self.nsg_analysis.get(
                "inter_node_communication",
                {}
            )
            inter_node_status = inter_node_communication.get(
                "status",
                "unknown"
            )

            print(f"- **NSGs Analyzed:** {total_nsgs}")
            print(f"- **Issues Found:** {len(blocking_rules)}")

            # Inter-node communication status
            status_icon = {
                "ok": "[OK]",
                "potential_issues": "[WARNING]",
                "blocked": "[ERROR]",
                "unknown": "[?]"
            }.get(inter_node_status, "[?]")
            status_messages = {
                "ok": "Not blocked",
                "potential_issues": "Potential issues",
                "blocked": "Blocked",
                "unknown": "Unknown",
            }
            status_text = status_messages.get(
                inter_node_status,
                inter_node_status.replace("_", " ").title()
            )
            print(
                f"- **Inter-node Communication:** "
                f"{status_icon} {status_text}"
            )

            # Show detailed NSG information
            if total_nsgs > 0:
                print()
                self._print_subnet_nsgs(subnet_nsgs)
                self._print_nic_nsgs(nic_nsgs)
                self._print_blocking_rules(blocking_rules)

            print()

    def _print_subnet_nsgs(self, subnet_nsgs: List[Dict[str, Any]]):
        """Print subnet NSGs section"""
        if subnet_nsgs:
            print("**Subnet NSGs:**")
            for nsg in subnet_nsgs:
                nsg_name = nsg.get("nsg_name", "unknown")
                subnet_name = nsg.get("subnet_name", "unknown")
                custom_rules = len(nsg.get("rules", []))
                default_rules = len(nsg.get("default_rules", []))

                print(f"- **{subnet_name}** -> NSG: {nsg_name}")
                print(
                    f"  - Custom Rules: {custom_rules}, "
                    f"Default Rules: {default_rules}"
                )

                # Show custom rules
                if custom_rules > 0 and nsg.get("rules"):
                    print("  - **Custom Rules:**")
                    for rule in nsg.get("rules", []):
                        self._print_nsg_rule(rule)

    def _print_nic_nsgs(self, nic_nsgs: List[Dict[str, Any]]):
        """Print NIC NSGs section"""
        if nic_nsgs:
            print("\n**NIC NSGs:**")

            # Group NICs by NSG name to avoid duplicates
            nsg_groups = {}
            for nsg in nic_nsgs:
                nsg_name = nsg.get("nsg_name", "unknown")
                vmss_name = nsg.get("vmss_name", "unknown")

                if nsg_name not in nsg_groups:
                    nsg_groups[nsg_name] = {
                        "nsg_data": nsg,
                        "vmss_list": []
                    }
                nsg_groups[nsg_name]["vmss_list"].append(vmss_name)

            # Display each unique NSG with its associated VMSS instances
            for nsg_name, group_data in nsg_groups.items():
                nsg = group_data["nsg_data"]
                vmss_list = group_data["vmss_list"]
                custom_rules = len(nsg.get("rules", []))
                default_rules = len(nsg.get("default_rules", []))

                # Show NSG with all VMSS instances using it
                vmss_names = ", ".join(vmss_list)
                print(f"- **{nsg_name}** (used by: {vmss_names})")
                print(
                    f"  - Custom Rules: {custom_rules}, "
                    f"Default Rules: {default_rules}"
                )

                # Show custom rules if any
                if custom_rules > 0 and nsg.get("rules"):
                    print("  - **Custom Rules:**")
                    for rule in nsg.get("rules", []):
                        self._print_nsg_rule(rule)

    def _print_nsg_rule(self, rule: Dict[str, Any]):
        """Print NSG rule details"""
        access = rule.get("access", "Unknown")
        direction = rule.get("direction", "Unknown")
        priority = rule.get("priority", "Unknown")
        protocol = rule.get("protocol", "Unknown")
        dest = rule.get("destination_address_prefix", "Unknown")
        ports = rule.get("destination_port_range", "Unknown")

        access_icon = "[OK]" if access.lower() == "allow" else "[X]"
        print(
            f"    - {access_icon} **{rule.get('name', 'Unknown')}** "
            f"(Priority: {priority})"
        )
        print(f"      - {direction} {protocol} to {dest} on ports {ports}")

    def _print_blocking_rules(self, blocking_rules: List[Dict[str, Any]]):
        """Print blocking rules section"""
        if blocking_rules:
            print("\n**[WARNING] Potentially Blocking Rules:**")
            for rule in blocking_rules:
                print(
                    f"- **{rule.get('rule_name', 'Unknown')}** "
                    f"in NSG {rule.get('nsg_name', 'Unknown')}"
                )
                print(f"  - Priority: {rule.get('priority', 'Unknown')}")
                print(f"  - Direction: {rule.get('direction', 'Unknown')}")
                print(f"  - Protocol: {rule.get('protocol', 'Unknown')}")
                print(f"  - Destination: {rule.get('destination', 'Unknown')}")
                print(f"  - Ports: {rule.get('ports', 'Unknown')}")
                print(f"  - Impact: {rule.get('impact', 'Unknown')}")

    def _print_findings(self):
        """Print findings section"""
        if self.findings:
            print("## Findings")
            print()

            # Count findings by severity
            critical_count = len([
                f for f in self.findings
                if f.get("severity") == "critical"
            ])
            error_count = len([
                f for f in self.findings
                if f.get("severity") == "error"
            ])
            warning_count = len([
                f for f in self.findings
                if f.get("severity") == "warning"
            ])
            info_count = len([
                f for f in self.findings
                if f.get("severity") == "info"
            ])

            # Display findings summary
            print("**Findings Summary:**")
            if critical_count > 0:
                print(f"- [CRITICAL] {critical_count}")
            if error_count > 0:
                print(f"- [ERROR] {error_count}")
            if warning_count > 0:
                print(f"- [WARNING] {warning_count}")
            if info_count > 0:
                print(f"- [INFO] {info_count}")
            print()

            # Define severity order (most severe first)
            severity_order = {
                "critical": 0,
                "high": 1,
                "error": 1,
                "warning": 2,
                "info": 3
            }

            # Sort findings by severity
            sorted_findings = sorted(
                self.findings,
                key=lambda f: severity_order.get(f.get("severity", "info"), 3)
            )

            # Display all findings in detail
            for finding in sorted_findings:
                severity_icon = {
                    "critical": "[CRITICAL]",
                    "error": "[ERROR]",
                    "warning": "[WARNING]",
                    "info": "[INFO]",
                }.get(finding.get("severity", "info"), "[INFO]")

                print(
                    f"### {severity_icon} "
                    f"{finding.get('code', 'UNKNOWN')}"
                )
                print(f"**Message:** {finding.get('message', '')}")
                if finding.get("recommendation"):
                    print(
                        f"**Recommendation:** "
                        f"{finding.get('recommendation', '')}"
                    )
                print()
        else:
            print("[OK] No issues detected in the network configuration!")
            print()
