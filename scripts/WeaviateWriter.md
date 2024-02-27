To automatically ingest text files into Weaviate using Unstructured, you can leverage the `unstructured-ingest` command-line interface (CLI) or write custom Python scripts utilizing Unstructured's connectors and runner classes. Here's an outline of both approaches based on the information from Unstructured's documentation:

### Using the CLI

You can use the `unstructured-ingest` CLI command to ingest documents from a local directory into Weaviate. Here's an example command:

```bash
unstructured-ingest local \
  --input-path example-docs/book-war-and-peace-1225p.txt \
  --output-dir local-output-to-weaviate \
  --strategy fast \
  --chunk-elements \
  --embedding-provider "langchain-huggingface" \
  --num-processes 2 \
  --verbose \
  weaviate \
  --host-url http://localhost:8080 \
  --class-name elements
```

This command processes a local text file (`book-war-and-peace-1225p.txt`), chunks it into elements, applies embeddings using the specified provider, and then ingests the processed data into Weaviate under the class `elements`. You'll need to adjust the `--input-path`, `--host-url`, and `--class-name` to match your specific files and Weaviate setup.

### Using Python Scripts

For a more flexible approach, you can write a Python script that utilizes Unstructured's connectors and runner to ingest data into Weaviate. Here's a simplified example to get you started:

```python
from unstructured.ingest.connector.local import SimpleLocalConfig
from unstructured.ingest.connector.weaviate import SimpleWeaviateConfig, WeaviateAccessConfig, WeaviateWriteConfig
from unstructured.ingest.interfaces import ChunkingConfig, EmbeddingConfig, ProcessorConfig
from unstructured.ingest.runner import LocalRunner
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
    runner = LocalRunner(
        processor_config=ProcessorConfig(verbose=True, output_dir="local-output-to-weaviate", num_processes=2),
        connector_config=SimpleLocalConfig(input_path="example-docs/book-war-and-peace-1225p.txt"),
        read_config=ReadConfig(),
        partition_config=PartitionConfig(),
        chunking_config=ChunkingConfig(chunk_elements=True),
        embedding_config=EmbeddingConfig(provider="langchain-huggingface"),
        writer=writer,
    )
    runner.run()
```

This script sets up a local file ingestion process with chunking and embedding, targeting the Weaviate instance at `http://localhost:8080` under the `elements` class. You'll need to customize the script with the correct file paths, Weaviate URL, and class name as per your requirements.

For more detailed information and to explore other integration capabilities offered by Unstructured, you can visit their [documentation page](https://unstructured-io.github.io/unstructured/integrations.html).