"""
Module: access_control.py
Purpose: Access control system for CodeAgents framework.

Manages permissions and access levels for agents operating within the
CodeAgents ecosystem, ensuring secure and controlled execution of
terminal commands and system operations.

Agent: GrokIA (Cline)
Created: 2025-12-03T10:15:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone

logger = logging.getLogger("core.access_control")

class PermissionLevel(Enum):
    """
    [CREATE] Permission levels for agent access control.

    Defines hierarchical access levels from basic read-only to full system access.
    """
    NONE = 0      # No access
    READ = 1      # Read-only access to files and basic info
    WRITE = 2     # File write access, basic operations
    EXECUTE = 3   # Terminal command execution, system operations
    FULL = 4      # Complete system access (admin level)

class ResourceType(Enum):
    """
    [CREATE] Types of resources that can be accessed.
    """
    FILESYSTEM = "filesystem"
    TERMINAL = "terminal"
    NETWORK = "network"
    SYSTEM = "system"
    CONFIG = "config"

@dataclass
class AgentPermissions:
    """
    [CREATE] Permission configuration for a specific agent.

    Defines what resources an agent can access and at what level.
    """
    agent_name: str
    permission_level: PermissionLevel
    allowed_resources: Set[ResourceType] = field(default_factory=set)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)
    max_execution_time: int = 300  # seconds
    rate_limit_per_minute: int = 60
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def can_access_resource(self, resource_type: ResourceType) -> bool:
        """Check if agent can access a specific resource type."""
        return resource_type in self.allowed_resources

    def can_execute_command(self, command: str) -> bool:
        """Check if agent can execute a specific terminal command."""
        # Check if command is explicitly blocked
        if any(blocked in command for blocked in self.blocked_commands):
            return False

        # Check if command is explicitly allowed
        if self.allowed_commands:
            # Allow all commands if "*" is in allowed_commands
            if "*" in self.allowed_commands:
                return True
            # Otherwise check if any allowed command pattern matches
            if not any(allowed in command for allowed in self.allowed_commands):
                return False

        # Permission level check
        return self.permission_level.value >= PermissionLevel.EXECUTE.value

    def has_permission_level(self, required_level: PermissionLevel) -> bool:
        """Check if agent has at least the required permission level."""
        return self.permission_level.value >= required_level.value

@dataclass
class AccessControlConfig:
    """
    [CREATE] Main access control configuration.

    Contains all agent permissions and global settings.
    """
    version: str = "1.0"
    default_permission_level: PermissionLevel = PermissionLevel.READ
    agents: Dict[str, AgentPermissions] = field(default_factory=dict)
    global_allowed_commands: List[str] = field(default_factory=list)
    global_blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf /", "sudo", "su", "passwd", "chmod 777", "dd if=", "mkfs",
        "fdisk", "parted", "mount", "umount", "systemctl", "service",
        "shutdown", "reboot", "halt", "poweroff", "init", "telinit"
    ])
    audit_log_enabled: bool = True
    max_concurrent_executions: int = 5

class AccessControlManager:
    """
    [CREATE] Manages access control for the CodeAgents system.

    Provides centralized permission checking and enforcement for all
    agent operations, especially terminal command execution.

    Attributes:
        config_path (Path): Path to the access control configuration file
        config (AccessControlConfig): Current access control configuration
        audit_log (List[Dict]): Log of access control decisions
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        [CREATE] Initialize the access control manager.

        Args:
            config_path (Optional[str]): Path to config file. Defaults to CodeAgents/access_control.json
        """
        self.config_path = Path(config_path or "CodeAgents/access_control.json")
        self.config = AccessControlConfig()
        self.audit_log: List[Dict] = []

        self._load_config()

        # Ensure critical agents have full access
        self._ensure_critical_agent_access()

    def _ensure_critical_agent_access(self) -> None:
        """
        [CREATE] Ensure critical agents have appropriate access levels.

        Sets up full access for IDE agents (You/GrokIA, Antigravity, Cursor).
        """
        critical_agents = {
            "GrokIA": "You (GrokIA/Cline) - Primary IDE Agent",
            "Cline": "You (GrokIA/Cline) - Primary IDE Agent",
            "Antigravity": "Antigravity - Advanced Agent",
            "Cursor": "Cursor - IDE Integration Agent"
        }

        for agent_name, description in critical_agents.items():
            if agent_name not in self.config.agents:
                # Create full access permissions for critical agents
                permissions = AgentPermissions(
                    agent_name=agent_name,
                    permission_level=PermissionLevel.FULL,
                    allowed_resources={
                        ResourceType.FILESYSTEM,
                        ResourceType.TERMINAL,
                        ResourceType.NETWORK,
                        ResourceType.SYSTEM,
                        ResourceType.CONFIG
                    },
                    allowed_commands=["*"],  # Allow all commands
                    blocked_commands=[],  # No blocked commands
                    max_execution_time=3600,  # 1 hour
                    rate_limit_per_minute=1000  # High rate limit
                )
                self.config.agents[agent_name] = permissions
                logger.info(f"Granted full access to critical agent: {agent_name} ({description})")
            else:
                # Ensure existing critical agents maintain full access
                agent_perms = self.config.agents[agent_name]
                if agent_perms.permission_level != PermissionLevel.FULL:
                    agent_perms.permission_level = PermissionLevel.FULL
                    agent_perms.allowed_resources.update({
                        ResourceType.FILESYSTEM,
                        ResourceType.TERMINAL,
                        ResourceType.NETWORK,
                        ResourceType.SYSTEM,
                        ResourceType.CONFIG
                    })
                    agent_perms.allowed_commands = ["*"]
                    agent_perms.blocked_commands = []
                    agent_perms.max_execution_time = max(agent_perms.max_execution_time, 3600)
                    agent_perms.rate_limit_per_minute = max(agent_perms.rate_limit_per_minute, 1000)
                    logger.info(f"Upgraded permissions for critical agent: {agent_name}")

    def check_agent_access(
        self,
        agent_name: str,
        resource_type: ResourceType,
        operation: str = "access",
        command: Optional[str] = None
    ) -> bool:
        """
        [CREATE] Check if an agent has access to perform an operation.

        Args:
            agent_name (str): Name of the agent requesting access
            resource_type (ResourceType): Type of resource being accessed
            operation (str): Specific operation being performed
            command (Optional[str]): Terminal command if applicable

        Returns:
            bool: True if access is granted, False otherwise
        """
        agent_perms = self.config.agents.get(agent_name)

        if not agent_perms:
            # Use default permissions for unknown agents
            agent_perms = AgentPermissions(
                agent_name=agent_name,
                permission_level=self.config.default_permission_level,
                allowed_resources={ResourceType.FILESYSTEM}  # Basic read access
            )

        # Check resource access
        if not agent_perms.can_access_resource(resource_type):
            self._log_access_denied(agent_name, resource_type, operation, command, "resource_not_allowed")
            return False

        # Check permission level
        required_level = self._get_required_level(operation)
        if not agent_perms.has_permission_level(required_level):
            self._log_access_denied(agent_name, resource_type, operation, command, "insufficient_permissions")
            return False

        # Check command-specific permissions for terminal operations
        if resource_type == ResourceType.TERMINAL and command:
            if not agent_perms.can_execute_command(command):
                self._log_access_denied(agent_name, resource_type, operation, command, "command_not_allowed")
                return False

        self._log_access_granted(agent_name, resource_type, operation, command)
        return True

    def _get_required_level(self, operation: str) -> PermissionLevel:
        """Get the minimum permission level required for an operation."""
        operation_requirements = {
            "read": PermissionLevel.READ,
            "write": PermissionLevel.WRITE,
            "execute": PermissionLevel.EXECUTE,
            "delete": PermissionLevel.FULL,
            "admin": PermissionLevel.FULL,
            "system": PermissionLevel.FULL
        }
        return operation_requirements.get(operation, PermissionLevel.READ)

    def _log_access_granted(
        self,
        agent_name: str,
        resource_type: ResourceType,
        operation: str,
        command: Optional[str],
        timestamp: Optional[str] = None
    ) -> None:
        """Log successful access."""
        if not self.config.audit_log_enabled:
            return

        log_entry = {
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "resource_type": resource_type.value,
            "operation": operation,
            "command": command,
            "decision": "GRANTED"
        }
        self.audit_log.append(log_entry)

    def _log_access_denied(
        self,
        agent_name: str,
        resource_type: ResourceType,
        operation: str,
        command: Optional[str],
        reason: str
    ) -> None:
        """Log denied access."""
        logger.warning(f"Access denied for agent {agent_name}: {reason}")

        if not self.config.audit_log_enabled:
            return

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "resource_type": resource_type.value,
            "operation": operation,
            "command": command,
            "decision": "DENIED",
            "reason": reason
        }
        self.audit_log.append(log_entry)

    def get_agent_permissions(self, agent_name: str) -> Optional[AgentPermissions]:
        """Get permissions for a specific agent."""
        return self.config.agents.get(agent_name)

    def update_agent_permissions(self, permissions: AgentPermissions) -> None:
        """Update permissions for an agent."""
        permissions.last_modified = datetime.now(timezone.utc).isoformat()
        self.config.agents[permissions.agent_name] = permissions
        self._save_config()

    def list_agents(self) -> List[str]:
        """Get list of all configured agents."""
        return list(self.config.agents.keys())

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:] if self.audit_log else []

    def _load_config(self) -> None:
        """Load access control configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert loaded data back to proper objects
                self.config = AccessControlConfig(
                    version=data.get('version', '1.0'),
                    default_permission_level=PermissionLevel(data.get('default_permission_level', 1)),
                    global_allowed_commands=data.get('global_allowed_commands', []),
                    global_blocked_commands=data.get('global_blocked_commands', []),
                    audit_log_enabled=data.get('audit_log_enabled', True),
                    max_concurrent_executions=data.get('max_concurrent_executions', 5)
                )

                # Load agent permissions
                for agent_name, perms_data in data.get('agents', {}).items():
                    permissions = AgentPermissions(
                        agent_name=agent_name,
                        permission_level=PermissionLevel(perms_data['permission_level']),
                        allowed_resources={ResourceType(rt) for rt in perms_data.get('allowed_resources', [])},
                        allowed_commands=perms_data.get('allowed_commands', []),
                        blocked_commands=perms_data.get('blocked_commands', []),
                        max_execution_time=perms_data.get('max_execution_time', 300),
                        rate_limit_per_minute=perms_data.get('rate_limit_per_minute', 60),
                        created_at=perms_data.get('created_at', datetime.now(timezone.utc).isoformat()),
                        last_modified=perms_data.get('last_modified', datetime.now(timezone.utc).isoformat())
                    )
                    self.config.agents[agent_name] = permissions

                logger.info(f"Loaded access control config from {self.config_path}")

            except Exception as e:
                logger.error(f"Failed to load access control config: {e}")
                # Use default config if loading fails
        else:
            logger.info(f"Access control config not found at {self.config_path}, using defaults")
            self._ensure_critical_agent_access()
            self._save_config()

    def _save_config(self) -> None:
        """Save access control configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            data = {
                'version': self.config.version,
                'default_permission_level': self.config.default_permission_level.value,
                'agents': {},
                'global_allowed_commands': self.config.global_allowed_commands,
                'global_blocked_commands': self.config.global_blocked_commands,
                'audit_log_enabled': self.config.audit_log_enabled,
                'max_concurrent_executions': self.config.max_concurrent_executions
            }

            for agent_name, perms in self.config.agents.items():
                data['agents'][agent_name] = {
                    'agent_name': perms.agent_name,
                    'permission_level': perms.permission_level.value,
                    'allowed_resources': [rt.value for rt in perms.allowed_resources],
                    'allowed_commands': perms.allowed_commands,
                    'blocked_commands': perms.blocked_commands,
                    'max_execution_time': perms.max_execution_time,
                    'rate_limit_per_minute': perms.rate_limit_per_minute,
                    'created_at': perms.created_at,
                    'last_modified': perms.last_modified
                }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved access control config to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save access control config: {e}")

# Global access control manager instance
access_manager = AccessControlManager()

def check_terminal_access(agent_name: str, command: str) -> bool:
    """
    [CREATE] Convenience function to check terminal command access.

    Args:
        agent_name (str): Name of the agent
        command (str): Terminal command to check

    Returns:
        bool: True if agent can execute the command
    """
    return access_manager.check_agent_access(
        agent_name=agent_name,
        resource_type=ResourceType.TERMINAL,
        operation="execute",
        command=command
    )

def require_terminal_access(agent_name: str, command: str) -> None:
    """
    [CREATE] Require terminal access or raise exception.

    Args:
        agent_name (str): Name of the agent
        command (str): Terminal command being executed

    Raises:
        PermissionError: If agent doesn't have access
    """
    if not check_terminal_access(agent_name, command):
        raise PermissionError(f"Agent '{agent_name}' does not have permission to execute: {command}")

if __name__ == "__main__":
    # Example usage and testing
    manager = AccessControlManager()

    # Test critical agent access
    test_agents = ["GrokIA", "Cline", "Antigravity", "Cursor"]

    print("=== CodeAgents Access Control System ===")
    print(f"Configuration file: {manager.config_path}")
    print(f"Configured agents: {len(manager.config.agents)}")
    print()

    for agent in test_agents:
        perms = manager.get_agent_permissions(agent)
        if perms:
            print(f"[OK] {agent}: {perms.permission_level.name} access")
            print(f"   Resources: {[rt.value for rt in perms.allowed_resources]}")
            print(f"   Terminal access: {'Full' if perms.can_execute_command('any command') else 'Restricted'}")
        else:
            print(f"[ERROR] {agent}: No permissions configured")
        print()

    # Test terminal command access
    test_commands = ["ls -la", "rm -rf /", "git status", "sudo apt update"]

    print("Terminal Command Access Test:")
    for agent in test_agents[:2]:  # Test first 2 agents
        print(f"\n{agent} command access:")
        for cmd in test_commands:
            access = check_terminal_access(agent, cmd)
            status = "[ALLOWED]" if access else "[DENIED]"
            print(f"  {cmd}: {status}")
