"""
[CLI] Skeleton Generator CLI

Command-line interface for the skeleton generator.

Agent: Composer
Timestamp: 2025-12-03T15:00:00Z
"""

import argparse
import sys
from pathlib import Path

# Add project root to path to ensure imports work
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from CodeAgents.core.skeleton_generator import create_skeleton_generator

def main():
    parser = argparse.ArgumentParser(description="CodeAgents Skeleton Generator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Skeleton command
    skeleton_parser = subparsers.add_parser("skeleton", help="Create agent skeleton")
    skeleton_parser.add_argument("agent_id", nargs="?", help="Agent ID (e.g., Composer)")
    skeleton_parser.add_argument("--timestamp", help="Custom timestamp (ISO 8601)")
    skeleton_parser.add_argument("--all", action="store_true", help="Create for all agents (not implemented in this CLI yet)")

    args = parser.parse_args()

    if args.command == "skeleton":
        generator = create_skeleton_generator()

        if args.all:
            print("Error: --all flag requires a list of agents, which is not yet configured.")
            sys.exit(1)

        if not args.agent_id:
            print("Error: Agent ID is required unless --all is specified.")
            sys.exit(1)

        try:
            path = generator.create_agent_skeleton(args.agent_id, args.timestamp)
            print(f"Created skeleton for {args.agent_id} at: {path}")
        except Exception as e:
            print(f"Error creating skeleton: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
