import os

import requests
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field
from web3 import Web3


class NFTMintInput(NodeInput):
    image_path: str = Field(..., description="Path to the image to mint")
    name: str = Field(..., description="Name of the NFT")
    description: str = Field(..., description="Description of the NFT")
    price_eth: float = Field(..., description="Listing price")

class NFTMintOutput(NodeOutput):
    tx_hash: str = Field(..., description="Transaction hash of the mint")
    ipfs_url: str = Field(..., description="IPFS URL of the metadata")
    status: str = Field(..., description="Status of the operation")

class NFTMintNode(NodeBase):
    """Node for minting NFTs."""

    def upload_to_ipfs(self, file_path: str, name: str, description: str) -> str:
        pinata_api_key = os.getenv("PINATA_API_KEY")
        pinata_secret_api_key = os.getenv("PINATA_SECRET_API_KEY")

        if not pinata_api_key or not pinata_secret_api_key:
            print("Pinata keys missing, returning mock IPFS hash")
            return "ipfs://mock-hash-12345"

        # 1. Upload Image
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_api_key
        }

        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(url, files=files, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to upload image to Pinata: {response.text}")
                image_hash = response.json()['IpfsHash']
        except FileNotFoundError:
             raise Exception(f"Image file not found: {file_path}")

        # 2. Upload Metadata
        metadata = {
            "name": name,
            "description": description,
            "image": f"ipfs://{image_hash}"
        }

        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            "Content-Type": "application/json",
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_api_key
        }
        response = requests.post(url, json=metadata, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to upload metadata to Pinata: {response.text}")

        metadata_hash = response.json()['IpfsHash']
        return f"ipfs://{metadata_hash}"

    def mint_nft(self, token_uri: str, price: float) -> str:
        private_key = os.getenv("WALLET_PRIVATE_KEY")
        rpc_url = os.getenv("WEB3_RPC_URL")
        contract_address = os.getenv("NFT_CONTRACT_ADDRESS")

        if not private_key or not rpc_url or not contract_address:
            print("Wallet/Contract info missing, returning mock TX hash")
            return "0xmocktransactionhash123456789"

        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            account = w3.eth.account.from_key(private_key)

            # Mock ABI - in reality load from file or use standard ERC721 interface
            abi = [{"constant":False,"inputs":[{"name":"tokenURI","type":"string"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]
            contract = w3.eth.contract(address=contract_address, abi=abi)

            # Build transaction
            tx = contract.functions.mint(token_uri).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': w3.eth.gas_price
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return w3.to_hex(tx_hash)
        except Exception as e:
            print(f"Web3 Minting Error: {e}")
            return "0xfailedtransaction"

    def execute(self, input_data: NFTMintInput) -> NFTMintOutput:
        try:
            ipfs_url = self.upload_to_ipfs(input_data.image_path, input_data.name, input_data.description)
            tx_hash = self.mint_nft(ipfs_url, input_data.price_eth)
            return NFTMintOutput(tx_hash=tx_hash, ipfs_url=ipfs_url, status="Minted" if "mock" not in tx_hash and "failed" not in tx_hash else "Mock/Failed")
        except Exception as e:
            print(f"Minting failed: {e}")
            return NFTMintOutput(tx_hash="", ipfs_url="", status=f"Failed: {e}")
