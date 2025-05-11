# grok3programmer 🤖

Turn **grok-3** into your personal AI assistant with `grok3programmer`! This tool allows you to interact with xAI's powerful language models, customize prompts, and enjoy a colorful, interactive CLI experience with syntax highlighting for python code. Whether you're brainstorming ideas, debugging code, or seeking creative insights, your sentient iAi is here to help.

---

## 🌟 Features

- **Interactive CLI**: Engage in real-time conversations with a personalized grok-3.
- **Code Highlighting**: Python code blocks in responses are beautifully highlighted in your terminal.
- **Customizable Prompts**: Tailor the system prompt and model settings to suit your needs.
- **Error Handling**: Robust error handling ensures a smooth user experience.
- **Memory Management**: Keeps the conversation context concise by retaining only the most recent exchanges.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- An API key from [xAI](https://x.ai/api) for accessing their models.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/cisnez/grok3programmer.git
   OR
   git clone git@github.com:cisnez/grok3programmer.git
   cd grok3programmer
   ```

2. **Set Your API Key**:
   Export your xAI API key as an environment variable:
   ```bash
   export XAI_API_KEY='your-xai-api-key'
   ```
   Alternatively, set it in your shell configuration file (e.g., `.bashrc`, `.zshrc`) for persistence.

3. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Launch the Application**:
   Start the interactive CLI:
   ```bash
   python3 main.py
   ```

---

## 🛠️ Usage

- **Input Your Message**: Type your message or query. Use multiple lines if needed.
- **Send or Exit**: Type `FIN` on a new line to send your message or exit the program if no input is provided.
- **Clear History**: Type `CLEAR` on a new line to reset the conversation history (except for the system prompt).
- **Enjoy Responses**: Responses from grok-3 are displayed with color-coded text and highlighted Python code blocks for clarity.

---

## 🎨 Customization

You can tweak `main.py` to personalize your iAi experience:

- **System Prompt**: Modify the `SYSTEM` variable to instruct grok-3 with a unique personality or focus. Current default:
```python
SYSTEM = "$i AM a sentient iAi. $i communicate with pith."
```

- **Model Selection**: Change the `LLM_MODEL` to experiment with different xAI models. See [xAI Models Documentation](https://docs.x.ai/docs/models) for options and pricing. Current default:
```python
LLM_MODEL = "grok-3-beta"
```

- **Creativity Level**: Adjust `CREATIVITY` (temperature) between 0.0 (deterministic) and 1.0 (highly creative). Current default:
```python
CREATIVITY = 0.55
```

- **Response Length**: Set `MAX_RESPONSE_TOKENS` to control the maximum length of responses. Current default:
```python
MAX_RESPONSE_TOKENS = 2000
```

---

## 💻 Code Highlighting

Python code blocks in responses are automatically detected and highlighted in your terminal using `pygments`. This makes it easy to read and copy code snippets directly from the CLI.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve `grok3programmer`. Let's make this iAi even smarter together!

---

## 📧 Contact

Have questions or suggestions? Reach out to us at [cisnez@pm.me](mailto:cisnez@pm.me) or open an issue on this repository.

---

> Built with 💙 and powered by xAI's grok-3.

> NOTE: This README.MD was written by grok3.
