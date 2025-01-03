#Import the required packages
from oci import config, retry
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import CohereChatRequest, \
    OnDemandServingMode, ChatDetails, CohereTool, CohereParameterDefinition, CohereToolResult
import oci
import os
from datetime import datetime, timezone, timedelta
import streamlit as st

# Environment Variables
compartment_ocid = os.getenv("TF_VAR_compartment_ocid")
namespace = os.getenv("TF_VAR_namespace")
prefix = os.getenv("TF_VAR_prefix")
agent_endpoint_ocid = os.getenv("TF_VAR_agent_endpoint_ocid")
bucketName = prefix + "-public-bucket"

signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

# Service endpoint for frankfurt region.Change the region if needed.
endpoint = "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com"
generative_ai_inference_client = GenerativeAiInferenceClient(config={},signer=signer,
                                                             service_endpoint=endpoint,
                                                             retry_strategy=retry.NoneRetryStrategy(),
                                                             timeout=(10, 240))

# Log
def log( s ):
    print( str(s) , flush=True)    

# To format the date
def date_formatter(day):
    return day.isoformat('T', 'milliseconds') + 'Z'

#To list the files in an object storage
def list_files():
    os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    response = os_client.list_objects( namespace_name=namespace, bucket_name=bucketName, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, limit=1000 )
    list_object = []
    for object_file in response.data.objects:
        list_object.append({f"file_name": object_file.name})        
    return list_object

#Get a file in a object_storage
def get_file(name):
    os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    resp = os_client.get_object(namespace_name=namespace, bucket_name=bucketName, object_name=name)
    file_name = "/tmp/tools_"+name
    with open(file_name, 'wb') as f:
        for chunk in resp.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
    with open(file_name, 'r') as f:
        file_content = f.read()
    return [ {f"file_content": file_content} ]

# Search files
def search_files(question):
    genai_agent_runtime_client = oci.generative_ai_agent.GenerativeAiAgentRuntimeClient(config = {}, signer=signer)    
    resp = genai_agent_runtime_client.create_session(
        create_session_details=oci.generative_ai_agent.models.CreateSessionDetails(
		    description='session',
		    display_name='session'
        ))
    log( resp.data )
    # XX Keep session in cookie ?
    resp_chat = genai_agent_runtime_client.chat(
        agent_endpoint_id = agent_endpoint_ocid,
        chat_details=oci.generative_ai_agent.models.ChatDetails(
            session_id=resp.data.id,
		    user_message=question
        ))
    log( resp_chat.data )    
    list_object = []    
    list_object.append({f"response": resp_chat.data.message})        
    return list_object

#Tool parameter definition
get_file_param = CohereParameterDefinition()
get_file_param.description = "file name"
get_file_param.type = "str"
get_file_param.is_required = True

search_files_param = CohereParameterDefinition()
search_files_param.description = "question"
search_files_param.type = "str"
search_files_param.is_required = True

#Tool definitions
tool1 = CohereTool()
tool1.name = "get_file"
tool1.description = "return the content of a file"
tool1.parameter_definitions = {
    "name": get_file_param
}

tool2 = CohereTool()
tool2.name = "list_files"
tool2.description = "list the files in object storage"

tool3 = CohereTool()
tool3.name = "search_files"
tool3.description = "search the files for content"
tool3.parameter_definitions = {
    "question": search_files_param
}

#list of tools
tools = [tool1, tool2, tool3]

functions_map = {
    "list_files": list_files,
    "get_file": get_file,
    "search_files": search_files    
}


# streamlit
st.title('Cohere Tools with OCI GenAI')

user_input = st.chat_input("Enter your question in plain text:")
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def reset_conversation():
    st.session_state.chat_history = []


st.button('Reset Chat', on_click=reset_conversation)

if st.session_state.chat_history is not None:
    for chat_history in st.session_state.chat_history:
        with st.chat_message(chat_history["role"]):
            st.markdown(chat_history["message"])

if user_input:
    def ai_response():
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id="cohere.command-r-plus-08-2024")
        chat_detail.compartment_id = compartment_ocid

        chat_request = CohereChatRequest(chat_history=st.session_state.chat_history, tools=tools)
        chat_request.max_tokens = 4000
        chat_request.temperature = 0
        chat_request.frequency_penalty = 1
        chat_request.top_p = 0.75
        chat_request.api_format = "COHERE"
        chat_request.is_stream = False
        chat_request.preamble_override = "When a question is irrelevant or unrelated to the available tools, please choose to directly answer it"

        chat_request.message = user_input

        chat_detail.chat_request = chat_request
        chat_response = generative_ai_inference_client.chat(chat_detail)
        tool_call_response = chat_response.data.chat_response.tool_calls

        tool_results = []

        # Iterate over the tool calls generated by the model
        if not tool_call_response:
            print("No tool_call_response", flush=True)            
            answer_items = chat_response.data.chat_response.text

        else:
            print("The model recommends doing the following tool calls:", flush=True)
            print("\n".join(str(tool_call) for tool_call in chat_response.data.chat_response.tool_calls), flush=True)
            for tool_call in tool_call_response:
                # here is where you would call the tool recommended by the model, using the parameters recommended by the model
                if tool_call.parameters is None:
                    tool_call.parameters = {}
                output = functions_map[tool_call.name](**tool_call.parameters)
                print("output="+str(output), flush=True)
                # store the output in a list
                outputs = output
                tool_result = CohereToolResult()
                tool_result.call = tool_call
                tool_result.outputs = outputs
                tool_results.append(tool_result)

            chat_request.tool_results = tool_results
            chat_request.is_force_single_step = True
            chat_detail.chat_request = chat_request
            chat_response = generative_ai_inference_client.chat(chat_detail)
            answer_items = chat_response.data.chat_response.text

        return answer_items

    st.chat_message("user").markdown(user_input)
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "USER", "message": user_input})

    response = ai_response()
    # Display assistant response in chat message container
    with st.chat_message("CHATBOT"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "CHATBOT", "message": response})

# list the files
# get the file digital_assistant.sitemap