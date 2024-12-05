
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.callbacks import get_openai_callback
from langchain.schema import format_document
import os
import json
from models import llm, embeddings
from prompts import engg_prompt_standalone, rephrasing_prompt, followup_prompt
from langchain.schema import HumanMessage

sessionId = "session123"
previousContext={}
previousSources={}
json_file_path = "conversation.json"
from pydantic import BaseModel, Field

class KMS_Response(BaseModel):
    '''Response to show user.'''
    content: str = Field(description="Actual content or response generated for question")
    answered: bool = Field(description="True if we received the answer and its present in context. False otherwise")
    is_followup: bool = Field(description="True if new query is followup of previous query False otherwise")
         
store = {}

async def chatting(query,department , chatrequest, is_followup, username):
    print(chatrequest)
    persist_directory="./chroma_langchain_db_v1"
    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory=persist_directory,  
        )
    list =[]
    for dept in department:
        list.append({'department':dept})

    filter = {}
    if(len(list)>1):
        filter = {
            '$or': list
        }
    else:
        filter = list[0]

    intent = ""
    engg_prompt=engg_prompt_standalone
    
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id == persist_directory + username:
            if session_id not in store:
                store[session_id]=ChatMessageHistory()
                print(f"stored chat message history {ChatMessageHistory()}")
                return store[session_id]
            history = store[session_id]
            limited_history = history.messages[-6:]  # Adjust the slice as needed
            store[session_id].messages=limited_history
            print(store[session_id])
            return store[session_id]
        else:
            return ChatMessageHistory()
        
    Default_Prompt = PromptTemplate.from_template(template="{page_content}")

    def _combine_documents(docs, document_prompt=Default_Prompt, document_separator="\n\n"):
        documents=[]
        for x in docs:
            if(x[1] >= 0.70):
                documents.append(x[0])
        doc_strings=[format_document(doc,document_prompt) for doc in documents]
        return document_separator.join(doc_strings)

    session_history = get_session_history_chat(chatrequest.ChatHistory[0].conversationId)
    conversations=[]
    conversation_text=''
    conversations = session_history[-2:]
    conversations.append({'user_query':query})
    conversation_text = "\n".join([
            f"User: {msg['user_query']}\nAssistant: {msg.get('bot_response', '')}"
            for msg in conversations
        ])
        
    prompt = rephrasing_prompt.replace('{conversation_text}',conversation_text)
    structured_llm = llm.with_structured_output(KMS_Response) 
    
    message = [
            HumanMessage(content=prompt)
        ] 
    is_followup=False
    with get_openai_callback() as cb:
            response = structured_llm.invoke(message)
    is_followup=response.is_followup
    query  = response.content
    if(is_followup and len(session_history) > 0):
        engg_prompt= followup_prompt
        prompt_new = ChatPromptTemplate.from_messages([
            (
                "system",
                engg_prompt + '\n' +"{context}"
            ),
            MessagesPlaceholder(variable_name='history'),
            ("human","{input}")
        ])

        structured_llm = llm.with_structured_output(KMS_Response)
        runnable= prompt_new | structured_llm

        with_message_history=RunnableWithMessageHistory(
            runnable,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
        context = previousContext["previousContext"]
        sources =previousSources["sources"]
        intent=identify_intent(query)

        if(intent["category"]=="Product-Specific"):
            Rule="""
                You follow below explicit rules while generating response format.
                Format Rule : 
                    •	Specific (not more than 350 words) 
                    •	If the response is longer than 100 words, then put it in a mark-down format 
                    •	Answer should be relevant to the subject-matter identified in the question, and should not include additional information related to the product that is not mentioned in the question. 
                    •	Numbers and taxes (VAT) should be included for product wherever necessary.
            """
            engg_prompt+=Rule
        elif(intent["category"]=="Customer-Queries"):
            Rule="""
                You follow below explicit rules while generating response format.
                Format Rule : 
                    -	Information should be step-by-step, displayed as a process
                    -	Response should be displayed in a conversational tone and the steps should be simple to understand
                    -	Response should include the expected outcome (what the customer should see when they follow the steps that the contact center agent gives them
            """
            engg_prompt+=Rule
        elif(intent["category"]=="Customer-Requests"):
                Rule="""
                    You follow below explicit rules while generating response format.
                    Format Rule : 
                        -	Information should be step-by-step
                        -	Should include information about how to navigate internal systems (more technical jargon – will be enhanced if we also upload a glossary) 
                        -   The structure of the response should be similar to a step-by-step guide. It should follow a chronological order based on how someone reading would do it.  
                """
                engg_prompt+=Rule
            
        with get_openai_callback() as cb:
            response = with_message_history.invoke(
                {
                    "context": context,
                    "input": query
                },
                config={"configurable":{"session_id":persist_directory + username, "verbose": True}}
            )

        if(not response.answered):
            engg_prompt=engg_prompt_standalone
            
            get_session_history(persist_directory + username)
    
            session_history = get_session_history_chat(chatrequest.ChatHistory[0].conversationId)
            print(session_history)
            history = ""
            for msg in session_history:
                history += f'User: {msg["user_query"]}; '
            

            intent=identify_intent(query)

            if(intent["category"]=="Product-Specific"):
                Rule="""
                    You follow below explicit rules while generating response format.
                    Format Rule : 
                        •	Specific (not more than 350 words) 
                        •	If the response is longer than 100 words, then put it in a mark-down format 
                        •	Answer should be relevant to the subject-matter identified in the question, and should not include additional information related to the product that is not mentioned in the question. 
                        •	Numbers and taxes (VAT) should be included for product wherever necessary.

                """
                engg_prompt+=Rule
            elif(intent["category"]=="Customer-Queries"):
                Rule="""
                    You follow below explicit rules while generating response format.
                    Format Rule : 
                        -	Information should be step-by-step, displayed as a process
                        -	Response should be displayed in a conversational tone and the steps should be simple to understand
                        -	Response should include the expected outcome (what the customer should see when they follow the steps that the contact center agent gives them
                """
                engg_prompt+=Rule
            elif(intent["category"]=="Customer-Requests"):
                    Rule="""
                        You follow below explicit rules while generating response format.
                        Format Rule : 
                            -	Information should be step-by-step
                            -	Should include information about how to navigate internal systems (more technical jargon – will be enhanced if we also upload a glossary) 
                            -   The structure of the response should be similar to a step-by-step guide. It should follow a chronological order based on how someone reading would do it.  
                    """
                    engg_prompt+=Rule
                
                
            documents = await vector_store.asimilarity_search_with_relevance_scores(
                query, k=7, filter=filter
            )
            sources = []
            for doc in documents:
                # print(doc.page_content)
                data=doc[0].metadata["source"]
                # print(Mapping["KFS-Rakbank.pdf"])
                print(doc[0].page_content)
                print(doc[0].metadata["page"])
                source=data
                if(doc[1]>=0.70):
                    sources.append(source)
                    sources.append(doc[0].metadata["page"])
            
            context=_combine_documents(documents)
            previousContext["previousContext"]=context
            previousSources["sources"]=sources
            
            template=ChatPromptTemplate.from_template(template=engg_prompt)
            print(template.messages[0].prompt)
            print(template.messages[0].prompt.input_variables)
            message=template.format_messages(Question=query,Context=context)
            # Default_Prompt = PromptTemplate.from_template(template="{page_content}")
            # runnable = message | llm
            with get_openai_callback() as cb:
                response = llm(message)
    else:
        get_session_history(persist_directory + username)

        documents = await vector_store.asimilarity_search_with_relevance_scores(
            query, k=7, filter=filter
        )
        sources=[]
        for doc in documents:
            data=doc[0].metadata["source"]
            print(doc[0].page_content)
            print(doc[0].metadata["page"])
            source=data
            if(doc[1]>=0.70):
                sources.append(source)
                sources.append(doc[0].metadata["page"])

        context=_combine_documents(documents)
        previousContext["previousContext"]=context
        previousSources["sources"]=sources
        
        intent=identify_intent(query)

        if(intent["category"]=="Product-Specific"):
            Rule="""
                You follow below explicit rules while generating response format.
                Format Rule : 
                    •	Specific (not more than 350 words) 
                    •	If the response is longer than 100 words, then put it in a mark-down format 
                    •	Answer should be relevant to the subject-matter identified in the question, and should not include additional information related to the product that is not mentioned in the question. 
                    •	Numbers and taxes (VAT) should be included for product wherever necessary.

            """
            engg_prompt+=Rule
        elif(intent["category"]=="Customer-Queries"):
            Rule="""
                You follow below explicit rules while generating response format.
                Format Rule : 
                    -	Information should be step-by-step, displayed as a process
                    -	Response should be displayed in a conversational tone and the steps should be simple to understand
                    -	Response should include the expected outcome (what the customer should see when they follow the steps that the contact center agent gives them
            """
            engg_prompt+=Rule
        elif(intent["category"]=="Customer-Requests"):
                Rule="""
                    You follow below explicit rules while generating response format.
                    Format Rule : 
                        -	Information should be step-by-step
                        -	Should include information about how to navigate internal systems (more technical jargon – will be enhanced if we also upload a glossary) 
                        -   The structure of the response should be similar to a step-by-step guide. It should follow a chronological order based on how someone reading would do it.  
                """
                engg_prompt+=Rule
            
        template=ChatPromptTemplate.from_template(template=engg_prompt)
        print(template.messages[0].prompt)
        print(template.messages[0].prompt.input_variables)
        message=template.format_messages(Question=query,Context=context)
        with get_openai_callback() as cb:
            response = llm(message)
    answer= response
    store_conversation(chatrequest.ChatHistory[0].conversationId, query, answer)
    total_tokens=cb.total_tokens
    completion_tokens=cb.completion_tokens
    prompt_tokens=cb.prompt_tokens
    print(total_tokens,completion_tokens,prompt_tokens)
    print(answer,sources)
    return {"answer": answer, "sources":sources, "intent":intent}

def get_chat_history_as_text(history):
    history_text=""
    for history_item in reversed(history):
        history_text=(
            """<|im_start|>user"""+"\n"+"user"+": "+history_item.user+"\n"+"""<|im_end|>"""+"\n"
            """<|im_start|>assistant"""+"\n"+(history_item.assistant+"""<|im_end|>""" if history_item.assistant else "")+"\n"+
            history_text
        )
        if(len(history_text))>1000:
            break
    return history_text

def load_conversation_history():
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_conversation_history(conversation_history):
    with open(json_file_path, 'w') as file:
        json.dump(conversation_history, file, indent=4)

def store_conversation(sessionId, user_query, bot_response):
    conversation_history = load_conversation_history()

    if sessionId not in conversation_history:
        conversation_history[sessionId] = []

    conversation_history[sessionId].append({
        "user_query": user_query,
        "bot_response": bot_response.content
    })

    save_conversation_history(conversation_history)

def get_session_history_chat(sessionId):
    conversation_history = load_conversation_history()
    return conversation_history.get(sessionId, [])

def identify_intent(query):
    propmt="""
    You are a category classifier assistant who help classify the query into given categories.
    STRICTLY return output in JSON format.
    Categories must be from [ 'Product-Specific', 'Customer-Queries', 'Customer-Requests', 'General']
    You strictly use below rules and conditions to identify the category:
    1. Product-Specific:
        This category contains inputs that are requesting static information about a product. 
        Also queries may contain some words from list: [eligibility, benefits, documents, conditions, interest rate, cashback, turnaround time, skywards miles, merchants, World card, Skyward card, what-is, fees]
    2. Customer-Queries:
        This category contains inputs that will elicit a step-by-step process outline that a contact center agent will have to guide a customer through (i.e. the actions will be taken by the customer on the phone, and the contact center agent will be guiding the customer on their own device using the instructions displayed on the screen). This response will have two layers of information – what the contact center agent should tell the customer and what the customer should be seeing on their end when they perform the actions that the contact center agent tells them. 
        Also queries may contain some words from list: [activate, set up, reset, process, new card, statement, liability certificate, renewal, block, digital pathway, PIN, app, balance, claim, how-to]
    3. Customer-Requests:
        This category contains inputs that will elicit a step-by-step process outline that the contact center agent has to undertake by themselves to conduct an action on behalf of the customer. This will include steps that need to be undertaken on their own systems, like Finacle & IBPS, and will be descriptive enough to help them navigate those systems to fulfill the customer’s request. 
        Also queries may contain some words from list:[reversal, process, closure, manual, dispute, credit limit, IBPS, Finacle, service request, cancellation, overlimit fee, late payment fee, reverse charge, how-to]
    4. General:
        This category is choosen if it does not falls into above categories.

    output format:{{"category":<Product-Specific/Customer-Queries/Customer-Requests>}}
    Question:```{query}```
    """
    template=ChatPromptTemplate.from_template(template=propmt)
    
    message=template.format_messages(query=query)
    with get_openai_callback() as cb:
            response = llm(message)
    import json
    data=response.content.replace('json\n','').replace('\n','').replace('```','')
    data1=json.loads(data)
    
    return data1