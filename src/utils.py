'''
===========================================
        Module: Util functions
===========================================
'''
import box
import yaml

from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chains import create_qa_with_sources_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from src.prompts import qa_template,condense_question_template
from src.llm import build_llm

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def set_qa_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=qa_template,
                            input_variables=['context','question'])
    return prompt

def set_condenser_prompt():
    """
    Prompt template to generate standalone quuestion from chat history
    """

    prompt = PromptTemplate.from_template(condense_question_template)

    return prompt


def build_retrieval_qa(llm, qa_prompt,condenser_prompt, memory,retriever):

    dbqa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=condenser_prompt,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        return_source_documents=cfg.RETURN_SOURCE_DOCUMENTS
        )
    
    
    return dbqa



    """

    dbqa = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type='stuff',
                                        retriever=vectordb.as_retriever(search_kwargs={'k': cfg.VECTOR_COUNT}),
                                        return_source_documents=cfg.RETURN_SOURCE_DOCUMENTS,
                                        chain_type_kwargs={'prompt': qa_prompt}
                                        )

        
    condense_question_chain = LLMChain(
        llm=llm,
        prompt=condenser_prompt,
    )

    dbqa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            memory=memory,
            retriever=vectordb.as_retriever(search_kwargs={'k': cfg.VECTOR_COUNT}),
            return_source_documents=True,
            question_generator=condense_question_chain,
            combine_docs_chain_kwargs={'prompt': qa_prompt}
        )
        qa_chain = create_qa_with_sources_chain(llm)

        final_qa_chain = StuffDocumentsChain(
            llm_chain=qa_chain,
            document_variable_name="context",
            document_prompt=qa_prompt,
        )
            
        dbqa = ConversationalRetrievalChain(
        question_generator=condense_question_chain,
        retriever=vectordb.as_retriever(search_kwargs={'k': cfg.VECTOR_COUNT}),
        memory=memory,
        combine_docs_chain=final_qa_chain,
    )
    """

    return dbqa

def setup_dbqa():

    with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
        cfg = box.Box(yaml.safe_load(ymlfile))


    if cfg.EMBEDDING_MODEL.startswith("OpenAI"):
        embeddings = OpenAIEmbeddings()
    else:
        embeddings = HuggingFaceEmbeddings(model_name=cfg.EMBEDDING_MODEL,
                                       model_kwargs={'device': 'cpu'})

    vectordb = FAISS.load_local(cfg.DB_FAISS_PATH, embeddings)
    retriever = vectordb.as_retriever(search_kwargs={'k': cfg.VECTOR_COUNT})
    llm = build_llm()
    qa_prompt = set_qa_prompt()
    condenser_prompt = set_condenser_prompt()
    memory = ConversationBufferMemory(memory_key="chat_history",input_key='question', output_key='answer', return_messages=True)

    dbqa = build_retrieval_qa(llm, qa_prompt,condenser_prompt, memory,retriever)

    return dbqa
