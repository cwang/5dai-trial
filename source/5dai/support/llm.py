"""Functions for utilising LLMs."""

import logging as log
import os
from typing import Any

from langchain.chat_models import ChatOpenAI
from llama_index import (
    Document,
    GPTVectorStoreIndex,
    LLMPredictor,
    OpenAIEmbedding,
    Response,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.chat_engine import SimpleChatEngine
from llama_index.llms import ChatMessage, MessageRole

from ..models.tasks import TaskConversation
from .paths import get_index_dir_path, get_upload_dir_path

PROMPT_USER_QUESTION = """
You are an AI assistant helping a human to find information in a collection of documents.
You are given a question and a collection of documents.
You need to find the best answer to the question from the given collection of documents.
Your conversation with the human is recorded in the chat history below.

History:
"{history}"

Now continue the conversation with the human. If you do not know the answer, say "I don't know".
Human: {input}
Assistant:"""


PROMPT_AGENT_SELECTION = """

"""


# def _get_model() -> OpenAI:
#     return OpenAI(temperature=0, model_name="text-davinci-003")


def _get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
    )


def _get_embedding_model() -> Any:
    # FIXME: This is a hack to explicitly set up the API key for the embedding model to avoid auth errors.
    return OpenAIEmbedding(api_key=os.environ["OPENAI_API_KEY"])


def _get_llm_predictor() -> LLMPredictor:
    return LLMPredictor(llm=_get_chat_model())


def _get_default_storage_context() -> StorageContext:
    return StorageContext.from_defaults()


def _get_storage_context(id_: int) -> StorageContext:
    return StorageContext.from_defaults(persist_dir=get_index_dir_path(id_))


def _get_service_context() -> ServiceContext:
    return ServiceContext.from_defaults(
        llm_predictor=_get_llm_predictor(), embed_model=_get_embedding_model()
    )


def _load_index_from_storage(id_: int) -> GPTVectorStoreIndex:
    return load_index_from_storage(
        storage_context=_get_storage_context(id_),
        service_context=_get_service_context(),
    )


def _create_index(documents: list[Document]) -> GPTVectorStoreIndex:
    # Use default storage and service context to initialise index purely for persisting
    return GPTVectorStoreIndex.from_documents(
        documents,
        storage_context=_get_default_storage_context(),
        service_context=_get_service_context(),
    )


def _persist_index(index: GPTVectorStoreIndex, id_: int) -> None:
    index.storage_context.persist(persist_dir=get_index_dir_path(id_))


def reindex(id_: int) -> None:
    """Reindex documents for a task."""
    try:
        documents = SimpleDirectoryReader(get_upload_dir_path(id_)).load_data()
        log.debug("docs to index, %s", len(documents))
        index = _create_index(documents)
        _persist_index(index, id_)
    except Exception as e:
        log.exception("Error indexing docs for task %d: %s", id_, e)


def _convert_to_chat_data(
    conversations: list[TaskConversation],
) -> (str, list[ChatMessage]):
    data = sorted(conversations, key=lambda x: x.generated_at)
    input_ = data.pop().question
    history = []
    for x in data:
        log.debug("Q %s A %s", x.question, x.answer)
        history.append(ChatMessage(content=x.question, role=MessageRole.USER))
        if x.answer is not None:
            history.append(
                ChatMessage(content=x.answer, role=MessageRole.ASSISTANT)
            )
    log.debug("converted history %s input_ %s", history, input_)
    return (input_, history)


def run_chat(conversations: list[TaskConversation], id_: int) -> Response:
    """Chat directly with a LLM with history."""
    engine = SimpleChatEngine.from_defaults(
        service_context=_get_service_context()
    )
    output = engine.chat(*_convert_to_chat_data(conversations))

    log.debug("(Chat) task: %d, answer: %s", id_, output)
    return output


def run_ask(
    conversations: list[TaskConversation],
    id_: int,
) -> Response:
    """Ask questions with a LLM against existing index(es) of the documents plus history."""
    index = _load_index_from_storage(id_)
    engine = index.as_chat_engine(
        verbose=True, similarity_top_k=3, vector_store_query_mode="default"
    )
    output = engine.chat(*_convert_to_chat_data(conversations))
    log.debug("(Ask) task: %d, answer: %s", id_, output)
    return output
