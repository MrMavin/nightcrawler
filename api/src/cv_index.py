from typing import Sequence, Any, Dict, List, DefaultDict
from collections import defaultdict
from dataclasses import dataclass, field
import json
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.indices.base import BaseIndex
from llama_index.core.response_synthesizers.base import BaseSynthesizer
from llama_index.core import Document
from llama_index.core.data_structs.data_structs import IndexStruct
from llama_index.core.data_structs.struct_type import IndexStructType
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.llms import LLM
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate
from llama_index.core.base.response.schema import Response
from llama_index.core.schema import QueryBundle


@dataclass
class CVIndexStruct(IndexStruct):
    """Data structure for CV Index."""

    metadata_index: DefaultDict[str, List[str]] = field(
        default_factory=lambda: defaultdict(list))
    node_metadata: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def get_type(cls) -> IndexStructType:
        return IndexStructType.DICT


class CVSynthesizer(BaseSynthesizer):
    def __init__(self, llm: LLM = None, **kwargs):
        # Pass the LLM explicitly to avoid default OpenAI LLM initialization
        super().__init__(llm=llm, **kwargs)
        self._llm = llm
        self._response_template = PromptTemplate(
            """You are an AI assistant specialized in CV evaluation and candidate assessment.

Based on the following query: {query_str}

And the relevant CV information retrieved:
{context_str}

Provide a short response.

Only use the provided context without assumptions.

Response:"""
        )

    def _get_prompts(self) -> Dict[str, PromptTemplate]:
        return {"response_template": self._response_template}

    def _update_prompts(self, prompts: Dict[str, PromptTemplate]) -> None:
        if "response_template" in prompts:
            self._response_template = prompts["response_template"]

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> str:
        """Get response by synthesizing information from text chunks."""
        if not text_chunks:
            return "No relevant information found in the CV to answer this query."

        # Combine all text chunks into context
        context_str = "\n\n".join(text_chunks)

        # If LLM is available, use it for synthesis
        if self._llm:
            formatted_prompt = self._response_template.format(
                query_str=query_str,
                context_str=context_str
            )
            response = self._llm.complete(formatted_prompt)
            return response.text
        else:
            # Fallback: return the context with basic formatting
            return f"Based on the query '{query_str}', here is the relevant CV information:\n\n{context_str}"

    def synthesize(
        self,
        query: QueryBundle,
        nodes: List[NodeWithScore],
        additional_source_nodes: Sequence[NodeWithScore] = None,
        **response_kwargs: Any,
    ) -> Response:
        """Synthesize response from nodes."""
        # Extract text chunks from nodes
        text_chunks = []
        for node_with_score in nodes:
            node = node_with_score.node
            # Use the proper method to get text content from TextNode
            if hasattr(node, 'get_content'):
                content = node.get_content()
                if content:
                    text_chunks.append(content)
            elif hasattr(node, 'text'):
                if node.text:
                    text_chunks.append(node.text)

        # Use the existing get_response method
        response_text = self.get_response(
            query_str=query.query_str,
            text_chunks=text_chunks,
            **response_kwargs
        )

        # Return Response object
        return Response(
            response=response_text,
            source_nodes=nodes,
        )

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> str:
        """Async version of get_response."""
        if not text_chunks:
            return "No relevant information found in the CV to answer this query."

        # Combine all text chunks into context
        context_str = "\n\n".join(text_chunks)

        # If LLM is available, use it for synthesis
        if self._llm:
            formatted_prompt = self._response_template.format(
                query_str=query_str,
                context_str=context_str
            )
            response = await self._llm.acomplete(formatted_prompt)
            return response.text
        else:
            # Fallback: return the context with basic formatting
            return f"Based on the query '{query_str}', here is the relevant CV information:\n\n{context_str}"


class CVRetriever(BaseRetriever):
    def __init__(self, index: 'CVIndex', llm: LLM = None):
        self._index = index
        self._llm = llm

    def _get_keyword_selection_prompt(self, query: str, keywords: List[str]) -> str:
        """Generate prompt for LLM to select relevant keywords."""
        keywords_str = ", ".join(keywords)
        prompt = f"""Given the following query: "{query}"

And the following available keywords from our index: {keywords_str}

Return a JSON list of all the keywords that are relevant to this query. Only return keywords that exist in the provided list. The response should be a valid JSON array of strings.

Example response format: ["keyword1", "keyword2", "keyword3"]

Relevant keywords:"""
        return prompt

    def _retrieve(self, query_str: str) -> List[NodeWithScore]:
        """Retrieve nodes based on keyword matching using LLM."""
        if not self._llm:
            return []

        # Get all unique keywords from the metadata index
        all_keywords = list(self._index._index_struct.metadata_index.keys())

        if not all_keywords:
            return []

        # Use LLM to select relevant keywords
        prompt = self._get_keyword_selection_prompt(query_str, all_keywords)
        llm_response = self._llm.complete(prompt)

        try:
            # Parse the LLM response as JSON
            selected_keywords = json.loads(llm_response.text.strip())
            if not isinstance(selected_keywords, list):
                selected_keywords = []
        except (json.JSONDecodeError, AttributeError):
            # Fallback: try to extract keywords from text response
            selected_keywords = [
                kw for kw in all_keywords if kw.lower() in llm_response.text.lower()]

        # Find all nodes that have the selected keywords
        relevant_nodes = []
        relevant_node_ids = set()

        # Since metadata_index only stores keyword->values mapping,
        # we still need to check each node to see if it has any of the selected keywords
        for node_id, node_metadata in self._index._index_struct.node_metadata.items():
            if 'properties' in node_metadata:
                try:
                    properties_dict = json.loads(node_metadata['properties'])
                    # Check if this node has any of the selected keywords as property keys
                    if any(keyword in properties_dict for keyword in selected_keywords):
                        relevant_node_ids.add(node_id)
                except json.JSONDecodeError:
                    continue

        # Create Document nodes for all relevant node IDs
        for node_id in relevant_node_ids:
            node_metadata = self._index._index_struct.node_metadata[node_id]

            # Transform metadata into readable text - ONLY for selected keywords
            text_parts = []

            # Add original content if available
            if 'content' in node_metadata and node_metadata['content']:
                text_parts.append(f"Content: {node_metadata['content']}")

            # Add ONLY the selected keywords as properties
            if 'properties' in node_metadata:
                try:
                    properties_dict = json.loads(node_metadata['properties'])
                    relevant_properties = {
                        k: v for k, v in properties_dict.items() if k in selected_keywords}

                    if relevant_properties:
                        text_parts.append("Properties:")
                        for key, value in relevant_properties.items():
                            text_parts.append(f"  {key}: {value}")
                except json.JSONDecodeError:
                    pass

            # Add other metadata fields
            for key, value in node_metadata.items():
                if key not in ['content', 'properties'] and value:
                    text_parts.append(f"{key}: {value}")

            # Combine all text parts
            formatted_text = "\n".join(text_parts)

            doc = TextNode(
                text=formatted_text,
                metadata=node_metadata,
                node_id=node_id
            )
            relevant_nodes.append(NodeWithScore(node=doc, score=1.0))

        return relevant_nodes


class CVIndex(BaseIndex):
    index_struct_cls = CVIndexStruct

    def _add_node_to_index(self, node: Document) -> None:
        if hasattr(node, 'metadata') and node.metadata:
            node_id = node.id_ if hasattr(node, 'id_') else str(id(node))
            self._index_struct.node_metadata[node_id] = node.metadata

            # Only index properties (validated JSON)
            if 'properties' in node.metadata:
                properties_dict = json.loads(node.metadata['properties'])
                for prop_key, prop_value in properties_dict.items():
                    str_value = str(prop_value)
                    if str_value not in self._index_struct.metadata_index[prop_key]:
                        self._index_struct.metadata_index[prop_key].append(
                            str_value)

    def _build_index_from_nodes(self, nodes: Sequence[Document]) -> CVIndexStruct:
        index_struct = CVIndexStruct()
        self._index_struct = index_struct
        for node in nodes:
            self._add_node_to_index(node)
        return index_struct

    def _delete_node(self, node_id: str) -> None:
        if node_id in self._index_struct.node_metadata:
            # Get the metadata for this node
            node_metadata = self._index_struct.node_metadata[node_id]

            # Remove properties from the metadata index
            if 'properties' in node_metadata:
                properties_dict = json.loads(node_metadata['properties'])
                for prop_key, prop_value in properties_dict.items():
                    str_value = str(prop_value)
                    if prop_key in self._index_struct.metadata_index and str_value in self._index_struct.metadata_index[prop_key]:
                        self._index_struct.metadata_index[prop_key].remove(
                            str_value)
                        # Clean up empty lists
                        if not self._index_struct.metadata_index[prop_key]:
                            del self._index_struct.metadata_index[prop_key]

            # Remove node metadata
            del self._index_struct.node_metadata[node_id]

    def _insert(self, node: Document) -> None:
        self._add_node_to_index(node)

    def as_retriever(self, llm: LLM = None) -> BaseRetriever:
        return CVRetriever(self, llm)

    def as_query_engine(self, llm: LLM = None, **kwargs):
        retriever = self.as_retriever(llm=llm)
        synthesizer = CVSynthesizer(llm=llm)
        return RetrieverQueryEngine(retriever=retriever, response_synthesizer=synthesizer)

    def ref_doc_info(self) -> Dict[str, Dict[str, Any]]:
        return self._index_struct.node_metadata
