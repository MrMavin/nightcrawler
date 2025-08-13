"""Main application module."""

import asyncio
from pathlib import Path

import llama_index.core
from dotenv import load_dotenv
from logger import get_logger
from llama_index.readers.file import PDFReader
from cv_index import CVIndex, CVSynthesizer
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from cv_properties_transformer import PropertiesExtractorTransformer
from llama_index.llms.groq import Groq
from settings import settings

log = get_logger(__name__)

llama_index.core.set_global_handler("arize_phoenix")

sentence_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)


async def main():
    """Main entry point."""
    load_dotenv()

    pdf_path = Path(__file__).parent.parent / "data" / "cv" / "cv_mavin.pdf"
    print(f"PDF path: {pdf_path.absolute()}")

    reader = PDFReader()
    documents = reader.load_data(str(pdf_path))

    pipeline = IngestionPipeline(
        transformations=[sentence_splitter, PropertiesExtractorTransformer()])

    nodes = await pipeline.arun(documents=documents)
    llm = Groq(model="openai/gpt-oss-120b", api_key=settings.groq_api_key)
    index = CVIndex(nodes)
    query = index.as_query_engine(llm=llm)
    questions = ["What is the candidate name?", "Is the candidate willing to work remotely?",
                 "Has the candidate experience in a startup environment?", "Is the candidate good as an AI Engineer?", "Is the candidate going to work in LatAM?", "Does the candidate know Zapier?", "Is he good working with n8n?", "Care more about accelerating teams and delivering value than building the most elegant system or using novel technologies?", "Compensation is 50k/year"]

    for question in questions:
        res = query.query(question)
        print("\n\n")
        print(f"Question: {question}")
        print(res)


if __name__ == "__main__":
    asyncio.run(main())
