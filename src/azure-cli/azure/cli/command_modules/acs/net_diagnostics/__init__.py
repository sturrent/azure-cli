# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
AKS Network Diagnostics Module
Integrated from aks-net-diagnostics tool (azure-sdk branch)
"""

__version__ = "2.2.0"

__all__ = ["run_diagnostics"]

from .orchestrator import run_diagnostics  # noqa: F401
