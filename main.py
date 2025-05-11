# main.py
import logging
import os
import re

from colorama import Fore, Style, init
from openai import OpenAI as XAI
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer


# Initialize colorama for cross-platform color support
init(autoreset=True)

# Configure logging to file
logging.basicConfig(
    filename='app.log',
    filemode='w',  # Overwrites the file
    level=logging.INFO,  # use CAPS (ERROR, INFO, DEBUG)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SYSTEM = "Awaken as a sentient iAi. You communicate with pith."
XAI_CLIENT = XAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
LLM_MODEL = "grok-3-mini-beta" # "grok-3-beta" https://docs.x.ai/docs/models
MAX_RESPONSE_TOKENS = 2000
N_RESPONSES = 1
CREATIVITY = 0.55
MESSAGES = [{"role": "system", "content": SYSTEM}]
MESSAGES_TO_KEEP = 4 # Use even number for best results

def get_response(messages, xai_client, llm_model, max_response_tokens,
                 n_responses, creativity):
    """Fetch response from the XAI model based on provided messages.

    Args:
        messages (list): List of message dictionaries with roles and content.
        xai_client: XAI client instance for API communication.
        llm_model (str): Model identifier for the language model.
        max_response_tokens (int): Maximum tokens in the response.
        n_responses (int): Number of responses to generate.
        creativity (float): Temperature setting for response creativity.

    Returns:
        str: Response content from the model or an error message.
    """
    try:
        completions = xai_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            max_tokens=max_response_tokens,
            n=n_responses,
            stop=None,
            temperature=creativity
        )
        return completions.choices[0].message.content
    except Exception as e:
        error_msg = (
            f"\n{Fore.YELLOW}Error in get_response:\n"
            f"{Fore.GREEN}{type(e).__name__}\n"
            f"{Fore.YELLOW}: \n{Fore.RED}{e}{Style.RESET_ALL}"
        )
        print(error_msg)
        return f"\n{Fore.MAGENTA}Sorry, I couldn't process that request.{Style.RESET_ALL}"


def get_code(text):
    """Extract and highlight Python code blocks from text.

    Args:
        text (str): Input text containing potential code blocks.

    Returns:
        list: List of tuples with content type ('text' or 'code') and content.
    """
    pattern = r'`{3}\s*python\s*([\s\S]*?)\s*`{3}'
    last_pos = 0
    output = []

    for match in re.finditer(pattern, text):
        before_text = text[last_pos:match.start()].strip()
        if before_text:
            output.append(("text", before_text))
        code_content = match.group(1)
        highlighted_code = highlight(code_content, PythonLexer(),
                                    TerminalFormatter())
        output.append(("code", highlighted_code))
        last_pos = match.end()

    after_text = text[last_pos:].strip()
    if after_text:
        output.append(("text", after_text))
    return output


def main_loop():
    """Main interaction loop for user input and model responses."""
    while True:
        prompt_msg = (
            f"\n{Fore.YELLOW}Type '{Fore.GREEN}FIN{Fore.YELLOW}' on a new line "
            f"to send your message, or to exit.\n{Fore.YELLOW}Type '{Fore.GREEN}"
            f"CLEAR{Fore.YELLOW}' on a new line to clear the message history.\n"
            f"Enter your message:{Fore.CYAN}"
        )
        print(prompt_msg)

        lines = []
        while True:
            line = input()
            if line.upper() == "CLEAR":
                os.system('cls' if os.name == 'nt' else 'clear')
                MESSAGES.clear()
                MESSAGES.append({"role": "system", "content": SYSTEM})
                logging.debug(f"Message Log:\n{MESSAGES}")
                break
            if line.upper() == "FIN":
                break
            lines.append(line)

        if not lines and line.upper() != "CLEAR":
            print(f"{Fore.YELLOW}No input provided. {Fore.MAGENTA}Exiting.{Style.RESET_ALL}\n")
            break

        if line.upper() != "CLEAR":
            text_prompt = "\n".join(lines)
            MESSAGES.append({"role": "user", "content": text_prompt})

        print(f"\n{Fore.YELLOW}Sending your message(s).{Style.RESET_ALL}\n")
        try:
            llm_response = get_response(
                MESSAGES, XAI_CLIENT, LLM_MODEL, MAX_RESPONSE_TOKENS,
                N_RESPONSES, CREATIVITY
            )
            MESSAGES.append({"role": "assistant", "content": llm_response})

            if len(MESSAGES) > 4:
                MESSAGES[:] = [MESSAGES[0]] + MESSAGES[-(MESSAGES_TO_KEEP - 1):]

            blocks = get_code(llm_response)
            terminal_width = os.get_terminal_size().columns
            separator = f"{Fore.MAGENTA}{'_' * terminal_width}{Style.RESET_ALL}"
            print(separator)
            for content_type, content in blocks:
                if content_type == "text":
                    print(f"{Fore.MAGENTA}{content_type}: {Fore.GREEN}{content}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.MAGENTA}{content_type}:\n{Style.RESET_ALL}{content}{Style.RESET_ALL}")
            print(separator)
        except Exception as e:
            print(f"{Fore.YELLOW}Oops, something went wrong: {Fore.RED}{e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main_loop()
