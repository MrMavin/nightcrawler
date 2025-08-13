from llama_index.core.schema import Node, TransformComponent
from flows.job_extractor.simple_extract_properties import create_extract_properties_workflow


class PropertiesExtractorTransformer(TransformComponent):
    def __call__(self, nodes, **kwargs):
        return self.acall(nodes, **kwargs)

    async def acall(self, nodes, **kwargs):
        for node in nodes:
            workflow = create_extract_properties_workflow()
            result = await workflow.run(job_description=node.text)
            node.metadata["properties"] = result
        return nodes
