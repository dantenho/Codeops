"""Generic Asset Publishing System - Extensible Plugin Architecture.

This module provides an abstract asset publishing system that can be extended
with different publishing backends (local, IPFS, S3, Cloudinary, etc.).
Replaces blockchain-specific publishing with a generic, plugin-based approach.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import uuid
import shutil


class PublishPlatform(Enum):
    """Supported publishing platforms."""
    LOCAL = "local"
    IPFS = "ipfs"
    S3 = "s3"
    CLOUDINARY = "cloudinary"
    CUSTOM = "custom"


@dataclass
class PublishResult:
    """Result of asset publishing operation."""
    transaction_id: str
    url: str
    status: str
    metadata: Dict[str, Any]
    platform: str


class AssetPublisher(ABC):
    """Abstract base class for asset publishers."""

    @abstractmethod
    def publish(self, asset_path: str, metadata: Dict[str, Any]) -> PublishResult:
        """
        Publish asset to platform.

        Args:
            asset_path: Path to asset file
            metadata: Asset metadata (title, description, tags, etc.)

        Returns:
            PublishResult with transaction ID, URL, and status
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """Get platform identifier."""
        pass


class LocalAssetPublisher(AssetPublisher):
    """Publish assets to local file system."""

    def __init__(self, output_dir: str = "./published_assets"):
        """
        Initialize local asset publisher.

        Args:
            output_dir: Directory to store published assets
        """
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def publish(self, asset_path: str, metadata: Dict[str, Any]) -> PublishResult:
        """Publish asset to local directory."""
        asset_id = str(uuid.uuid4())
        source_path = Path(asset_path)

        if not source_path.exists():
            return PublishResult(
                transaction_id=asset_id,
                url="",
                status=f"error: file not found - {asset_path}",
                metadata=metadata,
                platform=self.get_platform_name()
            )

        dest_filename = f"{asset_id}_{source_path.name}"
        dest_path = Path(self.output_dir) / dest_filename

        try:
            shutil.copy(asset_path, dest_path)

            return PublishResult(
                transaction_id=asset_id,
                url=f"file://{dest_path.absolute()}",
                status="published",
                metadata={**metadata, "local_path": str(dest_path)},
                platform=self.get_platform_name()
            )
        except Exception as e:
            return PublishResult(
                transaction_id=asset_id,
                url="",
                status=f"error: {str(e)}",
                metadata=metadata,
                platform=self.get_platform_name()
            )

    def get_platform_name(self) -> str:
        """Get platform identifier."""
        return "local"


class IPFSAssetPublisher(AssetPublisher):
    """Publish assets to IPFS."""

    def __init__(self, ipfs_endpoint: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Initialize IPFS asset publisher.

        Args:
            ipfs_endpoint: IPFS HTTP client endpoint
        """
        self.ipfs_endpoint = ipfs_endpoint

    def publish(self, asset_path: str, metadata: Dict[str, Any]) -> PublishResult:
        """Publish asset to IPFS."""
        try:
            import ipfshttpclient

            client = ipfshttpclient.connect(self.ipfs_endpoint)
            res = client.add(asset_path)

            return PublishResult(
                transaction_id=res['Hash'],
                url=f"ipfs://{res['Hash']}",
                status="published",
                metadata={
                    **metadata,
                    "ipfs_hash": res['Hash'],
                    "size": res.get('Size', 0)
                },
                platform=self.get_platform_name()
            )
        except ImportError:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status="error: ipfshttpclient not installed",
                metadata=metadata,
                platform=self.get_platform_name()
            )
        except Exception as e:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status=f"error: {str(e)}",
                metadata=metadata,
                platform=self.get_platform_name()
            )

    def get_platform_name(self) -> str:
        """Get platform identifier."""
        return "ipfs"


class S3AssetPublisher(AssetPublisher):
    """Publish assets to AWS S3."""

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        public_read: bool = True
    ):
        """
        Initialize S3 asset publisher.

        Args:
            bucket: S3 bucket name
            region: AWS region
            public_read: Make uploaded files publicly readable
        """
        self.bucket = bucket
        self.region = region
        self.public_read = public_read

    def publish(self, asset_path: str, metadata: Dict[str, Any]) -> PublishResult:
        """Publish asset to S3."""
        try:
            import boto3

            s3 = boto3.client('s3', region_name=self.region)
            source_path = Path(asset_path)
            asset_id = str(uuid.uuid4())

            key = f"assets/{asset_id}/{source_path.name}"

            extra_args = {}
            if self.public_read:
                extra_args['ACL'] = 'public-read'

            s3.upload_file(asset_path, self.bucket, key, ExtraArgs=extra_args)

            url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

            return PublishResult(
                transaction_id=asset_id,
                url=url,
                status="published",
                metadata={
                    **metadata,
                    "s3_bucket": self.bucket,
                    "s3_key": key,
                    "s3_region": self.region
                },
                platform=self.get_platform_name()
            )
        except ImportError:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status="error: boto3 not installed",
                metadata=metadata,
                platform=self.get_platform_name()
            )
        except Exception as e:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status=f"error: {str(e)}",
                metadata=metadata,
                platform=self.get_platform_name()
            )

    def get_platform_name(self) -> str:
        """Get platform identifier."""
        return "s3"


class CloudinaryAssetPublisher(AssetPublisher):
    """Publish assets to Cloudinary CDN."""

    def __init__(
        self,
        cloud_name: str,
        api_key: str,
        api_secret: str
    ):
        """
        Initialize Cloudinary asset publisher.

        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key
            api_secret: Cloudinary API secret
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret

    def publish(self, asset_path: str, metadata: Dict[str, Any]) -> PublishResult:
        """Publish asset to Cloudinary."""
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret
            )

            result = cloudinary.uploader.upload(asset_path, **metadata)

            return PublishResult(
                transaction_id=result.get('public_id', str(uuid.uuid4())),
                url=result.get('secure_url', ''),
                status="published",
                metadata={
                    **metadata,
                    "cloudinary_id": result.get('public_id'),
                    "cloudinary_version": result.get('version'),
                    "format": result.get('format'),
                    "width": result.get('width'),
                    "height": result.get('height')
                },
                platform=self.get_platform_name()
            )
        except ImportError:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status="error: cloudinary not installed",
                metadata=metadata,
                platform=self.get_platform_name()
            )
        except Exception as e:
            return PublishResult(
                transaction_id=str(uuid.uuid4()),
                url="",
                status=f"error: {str(e)}",
                metadata=metadata,
                platform=self.get_platform_name()
            )

    def get_platform_name(self) -> str:
        """Get platform identifier."""
        return "cloudinary"


# Publisher Registry
_publishers: Dict[str, AssetPublisher] = {
    "local": LocalAssetPublisher(),
}


def register_publisher(platform: str, publisher: AssetPublisher):
    """
    Register a custom publisher.

    Args:
        platform: Platform identifier
        publisher: AssetPublisher instance
    """
    _publishers[platform] = publisher


def unregister_publisher(platform: str):
    """
    Remove a publisher from registry.

    Args:
        platform: Platform identifier
    """
    if platform in _publishers and platform != "local":
        del _publishers[platform]


def get_publisher(platform: str = "local") -> AssetPublisher:
    """
    Get publisher for platform.

    Args:
        platform: Platform identifier (local, ipfs, s3, cloudinary, custom)

    Returns:
        AssetPublisher instance

    Raises:
        ValueError: If platform not registered
    """
    if platform not in _publishers:
        raise ValueError(
            f"No publisher registered for '{platform}'. "
            f"Available: {list(_publishers.keys())}"
        )

    return _publishers[platform]


def list_publishers() -> Dict[str, str]:
    """
    List all registered publishers.

    Returns:
        Dict mapping platform names to their class names
    """
    return {
        platform: publisher.__class__.__name__
        for platform, publisher in _publishers.items()
    }


# Initialize common publishers (if dependencies available)
def _initialize_optional_publishers():
    """Initialize optional publishers if dependencies are available."""
    try:
        import ipfshttpclient
        if "ipfs" not in _publishers:
            register_publisher("ipfs", IPFSAssetPublisher())
    except ImportError:
        pass

    try:
        import boto3
        # S3 requires configuration, so don't auto-register
        pass
    except ImportError:
        pass

    try:
        import cloudinary
        # Cloudinary requires credentials, so don't auto-register
        pass
    except ImportError:
        pass


# Auto-initialize on import
_initialize_optional_publishers()
