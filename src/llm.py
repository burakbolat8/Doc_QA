'''
===========================================
        Module: Open-source LLM Setup
===========================================
'''
from langchain.llms import CTransformers
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from dotenv import find_dotenv, load_dotenv
import box
import yaml
import os 


# Load environment variables from .env file
load_dotenv(find_dotenv())




def build_llm():
    
    # Import config vars
    with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
        cfg = box.Box(yaml.safe_load(ymlfile))
    
    if cfg.MODEL_TYPE == 'openai':

        #os.environ['OPENAI_API_KEY'] = cfg.OPENAI_API_KEY

        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=cfg.TEMPERATURE)

    else:

        llm = CTransformers(model=cfg.MODEL_BIN_PATH,
                                model_type=cfg.MODEL_TYPE,
                                config={'max_new_tokens': cfg.MAX_NEW_TOKENS,
                                        'temperature': cfg.TEMPERATURE}
                                )
    #print(llm)
        
    return llm
