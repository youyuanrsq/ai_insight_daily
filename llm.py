from pathlib import Path
from typing import Tuple

from langchain import OpenAI, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

from utils import get_file_path


def run_summarization(file_path: Path, num_docs: int = 3) -> Tuple[str]:
    """summary the content of a file using LLM

    Args:
        file_path (str): txt file path
        num_docs (int, optional): length of docs for summary. Defaults to 3.

    Returns:
        str: final summary
    """
    llm = OpenAI(temperature=0.)
    text_splitter = CharacterTextSplitter()

    with open(file_path) as f:
        state_of_the_union = f.read()

    texts = text_splitter.split_text(state_of_the_union)
    docs = [Document(page_content=t) for t in texts[:num_docs]]
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.run(docs)

    file_name = file_path.stem
    f_path = get_file_path(f"{file_name}-summary")

    with open(f_path, "w") as f:
        f.write(summary)

    return summary, f_path
