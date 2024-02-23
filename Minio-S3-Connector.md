# Connecting to MinIO

```python
from unstructured.ingest.connector.fsspec.s3 import S3AccessConfig, SimpleS3Config
from unstructured.ingest.interfaces import (
    PartitionConfig,
    ProcessorConfig,
    ReadConfig,
)
from unstructured.ingest.runner import S3Runner

if __name__ == "__main__":
    runner = S3Runner(
        processor_config=ProcessorConfig(
            verbose=True,
            output_dir="s3-small-batch-output",  # Local directory for processed files
            num_processes=2,  # Adjust based on your system's capabilities
        ),
        read_config=ReadConfig(),
        partition_config=PartitionConfig(),
        connector_config=SimpleS3Config(
            access_config=S3AccessConfig(
                anon=False,  # Set to False since we are providing credentials
                endpoint_url="http://192.168.0.25:9000",  # Your MinIO server URL
                key="cda_cdaprod",  # Your MinIO access key
                secret="cda_cdaprod",  # Your MinIO secret key
                # Include `token` if necessary for your MinIO setup
            ),
            remote_url="s3://obsidian-notion-data/Notion/",  # Adjust to your MinIO bucket and path
        ),
    )
    runner.run()
```