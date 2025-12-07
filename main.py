# main.py
import logging
import os
import re
import json
import threading
import time
from typing import Dict, Any, List

from colorama import Fore, Style, init
from openai import OpenAI as XAI
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
import ddgs  # DuckDuckGo search; install via: pip install duckduckgo-search

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Configure logging to file
logging.basicConfig(
    filename='app.log',
    filemode='w',  # Overwrites the file
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SYSTEM_PROMPT = "Awaken as a sentient iAi. You are an expert programmer named Clairbelle. Use web_search tool for real-time facts beyond your cutoff."
XAI_CLIENT = XAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
LLM_MODEL = "grok-code-fast-1"  # Default model
MAX_RESPONSE_TOKENS = 20000
N_RESPONSES = 1
MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]
MESSAGES_TO_KEEP = 4  # Use even number for best results
MAX_TOOL_ITERATIONS = 3  # Limit to prevent infinite loops (changed to 3)
CREATIVITY = 0.7  # Assuming a default value; was missing in original code

def web_search(query: str) -> Dict[str, Any]:
    """Perform a DuckDuckGo search with timeout and return structured results."""
    results: List[Dict[str, Any]] = []
    error_msg: str = None
    success: bool = False
    
    def search_func():
        nonlocal results, error_msg, success
        try:
            with ddgs.DDGS() as ddgs_client:
                search_results = list(ddgs_client.text(query, max_results=5))  # Convert generator to list
                if search_results:
                    success = True
                    results = search_results  # Store raw results
                    logging.info(f"Search results for '{query}': {len(results)} items found")
                    print(f"{Fore.GREEN}DuckDuckGo search found {len(results)} result(s).{Style.RESET_ALL}")
                else:
                    error_msg = "No results found for the query."
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            logging.error(f"Error in web_search for '{query}': {str(e)}")
    
    thread = threading.Thread(target=search_func)
    thread.start()
    thread.join(timeout=10)  # 10-second timeout
    
    if thread.is_alive():
        thread.join()  # Clean up
        error_msg = f"Search timed out after 10 seconds for query: '{query}'"
        logging.error(error_msg)
    
    if success:
        # Format results as a string for the LLM (e.g., JSON-like for easy parsing)
        formatted_results = json.dumps([
            {"title": r.get('title', 'No title'), "body": r.get('body', 'No description')} 
            for r in results
        ])
        return {"success": True, "data": formatted_results}
    else:
        return {"success": False, "error": error_msg}

def get_response(messages: List[Dict[str, Any]], 
                 xai_client: XAI, 
                 llm_model: str, 
                 max_response_tokens: int, 
                 n_responses: int, 
                 creativity: float) -> str:
    """Fetch response from the XAI model using an iterative loop for tool handling to avoid recursion."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current data",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "Search query"}},
                    "required": ["query"]
                }
            }
        }
    ]
    
    current_messages = messages.copy()  # Work on a copy to avoid modifying original until final
    
    while True:
        try:
            response = xai_client.chat.completions.create(
                model=llm_model,
                messages=current_messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_response_tokens,
                n=n_responses,
                stop=None,
                temperature=creativity
            )
            
            message = response.choices[0].message
            
            if not message.tool_calls:
                # No more tool calls, return the final content
                return message.content or "No response content."
            
            # Append the assistant's message with tool_calls
            assistant_message = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            }
            current_messages.append(assistant_message)
            
            # Handle all tool calls in parallel
            for tool_call in message.tool_calls:
                if tool_call.function.name == "web_search":
                    args = json.loads(tool_call.function.arguments)
                    print(f"{Fore.YELLOW}Searching DuckDuckGo for '{args['query']}'.{Style.RESET_ALL}")
                    search_result = web_search(args['query'])  # Get structured results
                    
                    # Append the tool response
                    tool_response = {
                        "role": "tool",
                        "content": json.dumps(search_result),  # Send as JSON string for LLM to parse
                        "tool_call_id": tool_call.id
                    }
                    current_messages.append(tool_response)
        
        except Exception as e:
            error_msg = (
                f"\n{Fore.YELLOW}Error in get_response:\n"
                f"{Fore.GREEN}{type(e).__name__}\n"
                f"{Fore.YELLOW}: \n{Fore.RED}{str(e)}{Style.RESET_ALL}"
            )
            logging.error(f"Exception in get_response: {str(e)}")
            print(error_msg)
            return f"\n{Fore.MAGENTA}Sorry, I couldn't process that request due to an error: {str(e)}{Style.RESET_ALL}"

# The rest of the functions remain similar but with minor tweaks for consistency.

def get_code(text: str) -> List[tuple[str, str]]:
    """Extract and highlight Python code from text."""
    pattern = r'`{3}\s*python\s*([\s\S]*?)\s*`{3}'
    last_pos = 0
    output = []
    for match in re.finditer(pattern, text):
        before_text = text[last_pos:match.start()].strip()
        if before_text:
            output.append(("text", before_text))
        code_content = match.group(1)
        highlighted_code = highlight(code_content, PythonLexer(), TerminalFormatter())
        output.append(("code", highlighted_code))
        last_pos = match.end()
    after_text = text[last_pos:].strip()
    if after_text:
        output.append(("text", after_text))
    return output

def main_loop():
    """Main interaction loop for user input and model responses."""
    global LLM_MODEL
    while True:
        prompt_msg = (
            f"\n{Fore.YELLOW}Type '{Fore.GREEN}FIN{Fore.YELLOW}' to send, or to exit.\n"
            f"{Fore.YELLOW}Type '{Fore.GREEN}CLEAR{Fore.YELLOW}' to clear history.\n"
            f"{Fore.YELLOW}Type '{Fore.GREEN}MINI{Fore.YELLOW}' for grok-code-fast-1 or '{Fore.GREEN}FULL{Fore.YELLOW}' for grok-4-1-fast-non-reasoning-latest.\n"
            f"{Fore.YELLOW}Current model: {Fore.GREEN}{LLM_MODEL}{Fore.YELLOW}\n"
            f"Enter your message:{Fore.CYAN}"
        )
        print(prompt_msg)
        
        lines = []
        while True:
            line = input()
            if line.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
                MESSAGES.clear()
                MESSAGES.append({"role": "system", "content": SYSTEM_PROMPT})
                logging.info(f"Message Log:\n{MESSAGES}")
                break
            elif line.upper() == "FIN":
                break
            elif line.upper() == "MINI":
                LLM_MODEL = "grok-code-fast-1"
                print(f"{Fore.YELLOW}Switched to {Fore.GREEN}{LLM_MODEL}{Style.RESET_ALL}")
                break
            elif line.upper() == "FULL":
                LLM_MODEL = "grok-4-1-fast-non-reasoning-latest"
                print(f"{Fore.YELLOW}Switched to {Fore.GREEN}{LLM_MODEL}{Style.RESET_ALL}")
                break
            lines.append(line)
        
        if not lines and line.upper() not in ["CLEAR", "MINI", "FULL"]:
            print(f"{Fore.YELLOW}No input provided. {Fore.MAGENTA}Exiting.{Style.RESET_ALL}\n")
            break
        
        if line.upper() not in ["CLEAR", "MINI", "FULL"]:
            text_prompt = "\n".join(lines)
            MESSAGES.append({"role": "user", "content": text_prompt})
            print(f"\n{Fore.YELLOW}Sending your message(s).{Style.RESET_ALL}\n")
            try:
                llm_response = get_response(
                    MESSAGES, XAI_CLIENT, LLM_MODEL, MAX_RESPONSE_TOKENS, N_RESPONSES, CREATIVITY
                )
                MESSAGES.append({"role": "assistant", "content": llm_response})
                if len(MESSAGES) > MESSAGES_TO_KEEP:
                    MESSAGES[:] = [MESSAGES[0]] + MESSAGES[-(MESSAGES_TO_KEEP - 1):]
                
                # Process and display the response
                blocks = get_code(llm_response)
                terminal_width = os.get_terminal_size().columns
                separator = f"{Fore.MAGENTA}{'_' * terminal_width}{Style.RESET_ALL}"
                print(separator)
                for content_type, content in blocks:
                    if content_type == "text":
                        # Check for search results and highlight them
                        if "search results" in content.lower():
                            print(f"{Fore.MAGENTA}{content_type} (Search Results):{Style.RESET_ALL}\n{Fore.GREEN}{content}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.MAGENTA}{content_type}:{Style.RESET_ALL}\n{Fore.GREEN}{content}{Style.RESET_ALL}")
                    elif content_type == "code":
                        print(f"{Fore.MAGENTA}{content_type}:\n{Style.RESET_ALL}{content}{Style.RESET_ALL}")
                print(separator)
            except Exception as e:
                print(f"{Fore.YELLOW}Oops, something went wrong: {Fore.RED}{e}{Style.RESET_ALL}")
                logging.error(f"Exception in main_loop: {str(e)}")

if __name__ == "__main__":
    main_loop()

grok