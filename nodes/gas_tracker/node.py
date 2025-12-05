import os
from typing import Optional

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field
from web3 import Web3


class GasTrackerInput(NodeInput):
    rpc_url: Optional[str] = Field(default=None, description="RPC URL to check gas on")
    threshold_gwei: float = Field(default=50.0, description="Max gas price in Gwei to approve")

class GasTrackerOutput(NodeOutput):
    gas_price_gwei: float = Field(..., description="Current gas price in Gwei")
    approved: bool = Field(..., description="Is gas below threshold?")

class GasTrackerNode(NodeBase):
    """Node for tracking gas prices."""

    def execute(self, input_data: GasTrackerInput) -> GasTrackerOutput:
        rpc_url = input_data.rpc_url or os.getenv("WEB3_RPC_URL")
        if not rpc_url:
             # Fallback to a public node
             rpc_url = "https://eth.public-rpc.com"

        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                # Try to connect, if fail, return high gas
                print(f"Failed to connect to {rpc_url}")
                return GasTrackerOutput(gas_price_gwei=999.0, approved=False)

            gas_price_wei = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')

            approved = gas_price_gwei <= input_data.threshold_gwei

            return GasTrackerOutput(gas_price_gwei=float(gas_price_gwei), approved=approved)
        except Exception as e:
            print(f"Error checking gas: {e}")
            return GasTrackerOutput(gas_price_gwei=999.0, approved=False)
