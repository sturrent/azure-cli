"""
NSG Analyzer for AKS Network Diagnostics

This module analyzes Network Security Groups (NSGs) associated with AKS clusters,
checking for misconfigurations, blocking rules, and compliance with AKS requirements.
"""

from typing import Any, Dict, List, Set

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from .base_analyzer import BaseAnalyzer
from .exceptions import AzureSDKError
from .models import Finding, FindingCode


# pylint: disable=too-many-instance-attributes
class NSGAnalyzer(BaseAnalyzer):
    """Analyzes Network Security Group configurations for AKS clusters."""

    def __init__(self, clients: Dict[str, Any], cluster_info: Dict[str, Any],
                 vmss_info: List[Dict[str, Any]], logger=None):
        """
        Initialize NSG Analyzer.

        Args:
            clients: Dictionary containing authenticated Azure clients
            cluster_info: AKS cluster information
            vmss_info: VMSS information from VMSS analyzer
            logger: Optional logger instance
        """
        super().__init__(clients, cluster_info, logger=logger)
        self.vmss_info = vmss_info
        self.network_client = clients.get('network_client')
        self.subscription_id = clients.get('subscription_id')
        self.nsg_analysis = {
            "subnet_nsgs": [],
            "nic_nsgs": [],
            "required_rules": [],
            "blocking_rules": [],
            "inter_node_communication": {"status": "unknown", "issues": []},
        }

    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive NSG analysis.

        Returns:
            Dictionary containing NSG analysis results
        """
        self.logger.info("Analyzing NSG configuration...")

        # Determine if cluster is private
        is_private_cluster = self._is_private_cluster()

        # Get required AKS rules
        required_rules = self._get_required_aks_rules(is_private_cluster)
        self.nsg_analysis["required_rules"] = required_rules

        # Analyze NSGs on subnets
        self._analyze_subnet_nsgs()

        # Analyze NSGs on NICs
        self._analyze_nic_nsgs()

        # Check inter-node communication
        self._analyze_inter_node_communication()

        # Check for blocking rules
        self._analyze_nsg_compliance()

        return self.nsg_analysis

    def _is_private_cluster(self) -> bool:
        """Check if cluster is private."""
        api_server_profile = self.cluster_info.get("api_server_access_profile")
        if api_server_profile:
            return api_server_profile.get("enable_private_cluster", False)
        return False

    def _get_required_aks_rules(self, is_private_cluster: bool) -> Dict[str, List[Dict[str, str]]]:
        """
        Get required NSG rules for AKS based on cluster type.

        Args:
            is_private_cluster: Whether the cluster is private

        Returns:
            Dictionary of required inbound and outbound rules
        """
        rules = {
            "outbound": [
                {
                    "name": "AKS_Registry_Access",
                    "protocol": "TCP",
                    "destination": "MicrosoftContainerRegistry",
                    "ports": ["443"],
                    "description": "Access to Microsoft Container Registry",
                },
                {
                    "name": "AKS_Azure_Management",
                    "protocol": "TCP",
                    "destination": "AzureCloud",
                    "ports": ["443"],
                    "description": "Azure management endpoints",
                },
                {
                    "name": "AKS_DNS",
                    "protocol": "UDP",
                    "destination": "*",
                    "ports": ["53"],
                    "description": "DNS resolution",
                },
                {
                    "name": "AKS_NTP",
                    "protocol": "UDP",
                    "destination": "*",
                    "ports": ["123"],
                    "description": "Network Time Protocol",
                },
            ],
            "inbound": [
                {
                    "name": "AKS_Inter_Node_Communication",
                    "protocol": "*",
                    "source": "VirtualNetwork",
                    "ports": ["*"],
                    "description": "Communication between cluster nodes",
                },
                {
                    "name": "AKS_Load_Balancer",
                    "protocol": "*",
                    "source": "AzureLoadBalancer",
                    "ports": ["*"],
                    "description": "Azure Load Balancer health probes",
                },
            ],
        }

        if not is_private_cluster:
            # Public clusters need API server access
            rules["outbound"].append(
                {
                    "name": "AKS_API_Server_Access",
                    "protocol": "TCP",
                    "destination": "*",
                    "ports": ["443"],
                    "description": "Access to AKS API server",
                }
            )

        return rules

    def _analyze_subnet_nsgs(self) -> None:
        """Analyze NSGs associated with node subnets."""
        processed_subnets: Set[str] = set()

        for vmss in self.vmss_info:
            vm_profile = vmss.get("virtual_machine_profile", {})
            network_profile = vm_profile.get("network_profile", {})
            network_interfaces = network_profile.get("network_interface_configurations", [])

            for nic in network_interfaces:
                ip_configs = nic.get("ip_configurations", [])
                for ip_config in ip_configs:
                    subnet = ip_config.get("subnet", {})
                    subnet_id = subnet.get("id")

                    if not subnet_id or subnet_id in processed_subnets:
                        continue

                    processed_subnets.add(subnet_id)
                    self._process_subnet_nsg(subnet_id)

    def _process_subnet_nsg(self, subnet_id: str) -> None:
        """Process NSG for a single subnet."""
        try:
            # Parse subnet ID to get components
            parsed = self._parse_resource_id(subnet_id)
            subnet_rg = parsed["resource_group"]
            vnet_name = parsed["parent_name"]  # VNet is parent of subnet
            subnet_name = parsed["resource_name"]

            # Get subnet info using SDK
            subnet_info = self.network_client.subnets.get(subnet_rg, vnet_name, subnet_name)

            nsg_info = subnet_info.network_security_group
            if nsg_info:
                nsg_id = nsg_info.id
                nsg_name = nsg_id.split("/")[-1] if nsg_id else "unknown"

                # Parse NSG ID to get resource group
                nsg_parsed = self._parse_resource_id(nsg_id)
                nsg_rg = nsg_parsed["resource_group"]

                # Get NSG details using SDK
                nsg_details = self.network_client.network_security_groups.get(nsg_rg, nsg_name)

                if nsg_details:
                    # Convert to dictionary with snake_case keys
                    nsg_dict = self._to_dict(nsg_details)

                    self.nsg_analysis["subnet_nsgs"].append(
                        {
                            "subnet_id": subnet_id,
                            "subnet_name": subnet_info.name,
                            "nsg_id": nsg_id,
                            "nsg_name": nsg_name,
                            "rules": nsg_dict.get("security_rules", []),
                            "default_rules": nsg_dict.get("default_security_rules", []),
                        }
                    )

                    self.logger.info("  Found NSG on subnet %s: %s", subnet_info.name, nsg_name)
            else:
                self.logger.info("  No NSG found on subnet %s", subnet_info.name)

        except (ResourceNotFoundError, HttpResponseError) as e:
            self.logger.error("  Failed to analyze subnet %s: %s", subnet_id, e)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("  Error parsing subnet ID %s: %s", subnet_id, e)

    def _analyze_nic_nsgs(self) -> None:
        """Analyze NSGs associated with node NICs."""
        for vmss in self.vmss_info:
            vmss_name = vmss.get("name")
            if not vmss_name:
                continue

            vm_profile = vmss.get("virtual_machine_profile", {})
            network_profile = vm_profile.get("network_profile", {})
            network_interfaces = network_profile.get("network_interface_configurations", [])

            for nic_config in network_interfaces:
                nsg_info = nic_config.get("network_security_group")
                if nsg_info:
                    nsg_id = nsg_info.get("id")
                    nsg_name = nsg_id.split("/")[-1] if nsg_id else "unknown"

                    try:
                        # Parse NSG ID to get resource group
                        nsg_parsed = self._parse_resource_id(nsg_id)
                        nsg_rg = nsg_parsed["resource_group"]

                        # Get NSG details using SDK
                        nsg_details = self.network_client.network_security_groups.get(nsg_rg, nsg_name)

                        if nsg_details:
                            # Convert to dictionary with snake_case keys
                            nsg_dict = self._to_dict(nsg_details)

                            self.nsg_analysis["nic_nsgs"].append(
                                {
                                    "vmss_name": vmss_name,
                                    "nic_name": nic_config.get("name", "unknown"),
                                    "nsg_id": nsg_id,
                                    "nsg_name": nsg_name,
                                    "rules": nsg_dict.get("security_rules", []),
                                    "default_rules": nsg_dict.get("default_security_rules", []),
                                }
                            )

                            self.logger.info("  Found NSG on VMSS %s NIC: %s", vmss_name, nsg_name)

                    except (AzureSDKError, HttpResponseError) as e:
                        self.logger.error("  Failed to analyze NIC NSG %s: %s", nsg_id, e)
                else:
                    self.logger.info("  No NSG found on VMSS %s NIC", vmss_name)

    def _analyze_inter_node_communication(self) -> None:
        """Analyze if NSG rules could block inter-node communication."""
        all_nsgs = self.nsg_analysis["subnet_nsgs"] + self.nsg_analysis["nic_nsgs"]
        issues = []

        for nsg in all_nsgs:
            blocking_rules = []
            all_rules = nsg.get("rules", []) + nsg.get("default_rules", [])

            for rule in all_rules:
                if (rule.get("access", "").lower() == "deny" and
                        rule.get("direction", "").lower() == "inbound" and
                        rule.get("priority", 0) < 65000):

                    source = rule.get("source_address_prefix", "")
                    if self._is_vnet_source(source):
                        blocking_rules.append(
                            {
                                "rule_name": rule.get("name", "unknown"),
                                "priority": rule.get("priority", 0),
                                "source": source,
                                "destination": rule.get("destination_address_prefix", ""),
                                "protocol": rule.get("protocol", ""),
                                "ports": rule.get("destination_port_range", ""),
                            }
                        )

            if blocking_rules:
                issues.append(
                    {
                        "nsg_name": nsg.get("nsg_name"),
                        "location": "subnet" if "subnet_id" in nsg else "nic",
                        "blocking_rules": blocking_rules,
                    }
                )

        self.nsg_analysis["inter_node_communication"] = {
            "status": "potential_issues" if issues else "ok",
            "issues": issues,
        }

        if issues:
            for issue in issues:
                self.add_finding(
                    Finding.create_warning(
                        FindingCode.NSG_INTER_NODE_BLOCKED,
                        message=f"NSG '{issue['nsg_name']}' has rules that may block inter-node communication",
                        recommendation=f"Review blocking rules in NSG on {issue['location']}",
                        nsg_name=issue["nsg_name"],
                        blocking_rules=issue["blocking_rules"],
                    )
                )

    def _is_vnet_source(self, source: str) -> bool:
        """Check if source is VirtualNetwork or private IP range."""
        if source in ["*", "VirtualNetwork"]:
            return True
        # Check for private IP ranges
        if source.startswith("10.") or source.startswith("192.168.") or source.startswith("172."):
            return True
        return False

    # pylint: disable=too-many-nested-blocks
    def _analyze_nsg_compliance(self) -> None:
        """Analyze NSG compliance with AKS requirements."""
        all_nsgs = self.nsg_analysis["subnet_nsgs"] + self.nsg_analysis["nic_nsgs"]
        blocking_rules = []

        for nsg in all_nsgs:
            nsg_name = nsg.get("nsg_name", "unknown")
            all_rules = nsg.get("rules", []) + nsg.get("default_rules", [])

            # Sort by priority
            sorted_rules = sorted(all_rules, key=lambda x: x.get("priority", 65000))

            # Check for rules that might block AKS traffic
            for rule in sorted_rules:
                if rule.get("access", "").lower() == "deny" and rule.get("priority", 0) < 65000:
                    if rule.get("direction", "").lower() == "outbound":
                        dest = rule.get("destination_address_prefix", "")
                        ports = rule.get("destination_port_range", "")
                        protocol = rule.get("protocol", "")

                        # Check if blocks essential AKS traffic
                        if self._blocks_aks_traffic(dest, ports, protocol):
                            is_overridden, overriding_rules = self._check_rule_precedence(rule, sorted_rules)

                            blocking_rule = {
                                "nsg_name": nsg_name,
                                "rule_name": rule.get("name", "unknown"),
                                "priority": rule.get("priority", 0),
                                "direction": rule.get("direction", ""),
                                "protocol": protocol,
                                "destination": dest,
                                "ports": ports,
                                "impact": "Could block AKS management traffic",
                                "is_overridden": is_overridden,
                                "overridden_by": overriding_rules,
                                "effective_severity": "warning" if is_overridden else "critical",
                            }

                            blocking_rules.append(blocking_rule)

                            # Add finding
                            if is_overridden:
                                self.add_finding(
                                    Finding.create_warning(
                                        FindingCode.NSG_POTENTIAL_BLOCK,
                                        message=f"NSG rule '{rule.get('name')}' in '{nsg_name}' "
                                                f"may block AKS traffic but is overridden",
                                        recommendation="Verify that override rules are correctly configured",
                                        **blocking_rule,
                                    )
                                )
                            else:
                                self.add_finding(
                                    Finding.create_critical(
                                        FindingCode.NSG_BLOCKING_AKS_TRAFFIC,
                                        message=f"NSG rule '{rule.get('name')}' in '{nsg_name}' "
                                                f"may block AKS traffic",
                                        recommendation=f"Review NSG rule priority {rule.get('priority')} - "
                                                       f"Could block AKS management traffic",
                                        **blocking_rule,
                                    )
                                )

        self.nsg_analysis["blocking_rules"] = blocking_rules

    def _blocks_aks_traffic(self, dest: str, ports: str, protocol: str) -> bool:
        """Check if rule blocks essential AKS traffic."""
        # Check destination
        if dest in ["*", "Internet"] or "MicrosoftContainerRegistry" in str(dest) or "AzureCloud" in str(dest):
            # Check ports and protocol
            if ("443" in str(ports) or "*" in str(ports)) and protocol.upper() in ["TCP", "*"]:
                return True
        return False

    def _check_rule_precedence(
        self, deny_rule: Dict[str, Any], sorted_rules: List[Dict[str, Any]]
    ) -> tuple:
        """
        Check if a deny rule is overridden by higher priority allow rules.

        Args:
            deny_rule: The deny rule to check
            sorted_rules: All rules sorted by priority

        Returns:
            Tuple of (is_overridden, overriding_rules)
        """
        deny_priority = deny_rule.get("priority", 65000)
        overriding_rules = []

        for rule in sorted_rules:
            rule_priority = rule.get("priority", 65000)

            if rule_priority >= deny_priority:
                break

            if (rule.get("access", "").lower() == "allow" and
                    rule.get("direction", "").lower() == deny_rule.get("direction", "").lower()):

                if self._rules_overlap(deny_rule, rule):
                    overriding_rules.append(
                        {
                            "rule_name": rule.get("name", "unknown"),
                            "priority": rule_priority,
                            "destination": rule.get("destination_address_prefix", ""),
                            "ports": rule.get("destination_port_range", ""),
                            "protocol": rule.get("protocol", ""),
                        }
                    )

        return len(overriding_rules) > 0, overriding_rules

    def _rules_overlap(self, deny_rule: Dict[str, Any], allow_rule: Dict[str, Any]) -> bool:
        """
        Check if an allow rule overlaps with a deny rule for AKS traffic.

        This method properly validates that the allow rule actually covers
        the specific traffic that AKS needs.
        """
        # Check destination overlap with proper service tag semantics
        deny_dest = deny_rule.get("destination_address_prefix", "").lower()
        allow_dest = allow_rule.get("destination_address_prefix", "").lower()

        dest_overlap = False

        # Allow rule with '*' covers everything
        if allow_dest == "*":
            dest_overlap = True
        # Allow rule with same destination as deny
        elif allow_dest == deny_dest:
            dest_overlap = True
        # Special case: Internet traffic requirements
        elif deny_dest == "internet":
            # For Internet-blocking rules, only these service tags actually help:
            # - Internet (explicit allow)
            # - AzureContainerRegistry (covers MCR)
            # - * (covers everything)
            # NOTE: AzureCloud does NOT cover general Internet destinations like MCR
            if allow_dest in ["internet", "azurecontainerregistry"]:
                dest_overlap = True
        # If deny is wildcard, allow must also be wildcard
        elif deny_dest == "*":
            if allow_dest in ["*", "internet", "azurecloud", "azurecontainerregistry"]:
                dest_overlap = True
        # AzureCloud covers Azure-specific services but not general Internet
        elif deny_dest in ["azurecloud", "microsoftcontainerregistry", "azurecontainerregistry"]:
            if allow_dest in ["*", "azurecloud", "azurecontainerregistry"]:
                dest_overlap = True

        if not dest_overlap:
            return False

        # Check port overlap
        deny_ports = str(deny_rule.get("destination_port_range", "")).lower()
        allow_ports = str(allow_rule.get("destination_port_range", "")).lower()

        port_overlap = False
        if allow_ports == "*" or deny_ports == "*":
            port_overlap = True
        elif "443" in deny_ports and ("443" in allow_ports or "*" in allow_ports):
            port_overlap = True
        elif deny_ports == allow_ports:
            port_overlap = True

        if not port_overlap:
            return False

        # Check protocol overlap
        deny_protocol = deny_rule.get("protocol", "").upper()
        allow_protocol = allow_rule.get("protocol", "").upper()

        protocol_overlap = (allow_protocol == "*" or
                            deny_protocol == "*" or
                            deny_protocol == allow_protocol or
                            (deny_protocol in ["TCP", "*"] and allow_protocol in ["TCP", "*"]))

        return protocol_overlap

    def _parse_resource_id(self, resource_id: str) -> Dict[str, str]:
        """
        Parse Azure resource ID into components.

        Args:
            resource_id: Azure resource ID string

        Returns:
            Dictionary with parsed components
        """
        parts = resource_id.split('/')
        result = {}

        # Extract subscription and resource group
        for i, part in enumerate(parts):
            if part.lower() == 'subscriptions' and i + 1 < len(parts):
                result['subscription'] = parts[i + 1]
            elif part.lower() == 'resourcegroups' and i + 1 < len(parts):
                result['resource_group'] = parts[i + 1]
            elif part.lower() == 'providers' and i + 1 < len(parts):
                result['provider'] = parts[i + 1]

        # Extract resource types and names after provider
        # Format: /providers/{provider}/{type1}/{name1}/{type2}/{name2}/...
        provider_index = -1
        for i, part in enumerate(parts):
            if part.lower() == 'providers':
                provider_index = i
                break

        if provider_index >= 0 and provider_index + 2 < len(parts):
            # Skip provider namespace, start with first resource type/name pair
            resource_parts = parts[provider_index + 2:]

            # Process resource type/name pairs
            for i in range(0, len(resource_parts) - 1, 2):
                resource_type = resource_parts[i]
                resource_name = resource_parts[i + 1]

                # First pair is parent (e.g., virtualNetworks)
                # Last pair is the actual resource (e.g., subnets)
                if i == 0 and len(resource_parts) > 2:
                    result['parent_type'] = resource_type
                    result['parent_name'] = resource_name
                elif i == len(resource_parts) - 2:
                    result['resource_type'] = resource_type
                    result['resource_name'] = resource_name

            # Handle simple resources without parent (only one type/name pair)
            if 'resource_name' not in result and 'parent_name' in result:
                result['resource_type'] = result.get('parent_type', '')
                result['resource_name'] = result.get('parent_name', '')
                result.pop('parent_type', None)
                result.pop('parent_name', None)

        return result

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert SDK object to dictionary with snake_case keys.

        Args:
            obj: Azure SDK object

        Returns:
            Dictionary representation with snake_case keys
        """
        if hasattr(obj, 'as_dict'):
            result = obj.as_dict()
        elif isinstance(obj, dict):
            result = obj
        else:
            return {}

        # Convert all keys to snake_case
        def to_snake_case(name: str) -> str:
            """Convert camelCase to snake_case."""
            import re
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

        def convert_dict(d: Dict) -> Dict:
            """Recursively convert dict keys to snake_case."""
            if not isinstance(d, dict):
                return d
            return {
                to_snake_case(k): convert_dict(v) if isinstance(v, dict)
                else [convert_dict(i) if isinstance(i, dict) else i for i in v] if isinstance(v, list)
                else v
                for k, v in d.items()
            }

        return convert_dict(result)
