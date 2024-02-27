from unstructured.ingest.connector.s3 import SimpleS3Config
from unstructured.ingest.connector.weaviate import SimpleWeaviateConfig, WeaviateAccessConfig, WeaviateWriteConfig
from unstructured.ingest.interfaces import ChunkingConfig, EmbeddingConfig, ProcessorConfig
from unstructured.ingest.runner import S3Runner
from unstructured.ingest.runner.writers.weaviate import WeaviateWriter

def get_writer():
    return WeaviateWriter(
        connector_config=SimpleWeaviateConfig(
            access_config=WeaviateAccessConfig(),
            host_url="http://localhost:8080",
            class_name="elements",
        ),
        write_config=WeaviateWriteConfig(),
    )

if __name__ == "__main__":
    writer = get_writer()
    runner = S3Runner(
        processor_config=ProcessorConfig(verbose=True, output_dir="minio-output-to-weaviate", num_processes=2),
        connector_config=SimpleS3Config(
            bucket_name="your-minio-bucket-name",
            access_key="your-minio-access-key",
            secret_key="your-minio-secret-key",
            endpoint_url="your-minio-endpoint-url", # e.g., "http://localhost:9000"
            input_prefix="path/to/your/documents/", # Adjust as needed
        ),
        read_config=ReadConfig(),
        partition_config=PartitionConfig(),
        chunking_config=ChunkingConfig(chunk_elements=True),
        embedding_config=EmbeddingConfig(provider="langchain-huggingface"),
        writer=writer,
    )
    runner.run()
