from llama_cpp.llama import Llama, LlamaGrammar
import httpx
from grammar_generator import generate_gbnf_grammar_from_pydantic
import json



def chat_template_format(messages, functions):
    text = ""
    system_prompt_addition = "\n\nYou have access to the following functions:\n"
    for function in functions:
        system_prompt_addition += f"{json.dumps(function.openapi_json, indent=4)}\n"
    system_prompt_addition += "\nRespond in the following syntax:\n"
    system_prompt_addition += "<function_call> ...arguments </function_call>\n"
    for message in messages:
        if message['role'] == 'system':
            message['content'] += system_prompt_addition
            system_prompt_addition = ""
        content = message['content']
        if message.get('function_call'):
            content += f"""\n<function_call> {json.dumps(message['function_call'], indent=4)}</function_call>"""
        text += f"""<|im_start|>{message['role']}
{content}<|im_end|>"""
    return text
    
    

def function_call_completion(llm, messages, functions):
    """
    1. Generate grammer for the functions
    2. Format messages using chat template, add functions to system prompt
    3. generate completion
    """
    # grammar_text = httpx.get("https://raw.githubusercontent.com/ggerganov/llama.cpp/master/grammars/json_arr.gbnf").text
    pydantic_model_list = [f.parameters_openapi for f in functions]
    breakpoint()
    grammar_text = generate_gbnf_grammar_from_pydantic(pydantic_model_list)
    grammar = LlamaGrammar.from_string(grammar_text)
    chat_text = chat_template_format(
        messages=messages,
        functions=functions
    )
    chat_text += "\n\n<|im_start|>assistant\n<function_call> "
    print(chat_text)
    response = llm(
        chat_text,
        grammar=grammar, max_tokens=-1
    )
    return response
    
    
def example():
    # llm = Llama(model_path="/home/niels/text-generation-webui/models/dolphin-2.5-mixtral-8x7b.Q4_K_M.gguf")
    llm = None
    from minichain.tools.bash import Jupyter
    jupyter = Jupyter()
    response = function_call_completion(
        llm=llm,
        messages=[
            {
              "role": "system",
              "content": "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. The assistant calls functions with appropriate input when necessary"
              
            },
            {
              "role": "user",
              "content": "create a pyplot plot of a sine wave please"
            }
        ],
        functions=[
            jupyter
        ]
    )
    breakpoint()
    print(response)


example()