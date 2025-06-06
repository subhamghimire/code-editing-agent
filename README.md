# Code-Editing AI Agent

> Building a fully functional code-editing AI agent in less than 300 lines of Python

A simple yet powerful AI agent that can read, list, and edit files through natural conversation. Inspired by [Thorsten Ball's blog post](https://ampcode.com/how-to-build-an-agent) but implemented in Python for accessibility.

## What This Does

This agent can:

- **Read files** - "What's in my config.py?"
- **List directories** - "Show me all Python files in this project"
- **Edit code** - "Add error handling to my function"
- **Combine actions** - Intelligently chains tools to complete complex tasks

## Quick Start

### Prerequisites

- Python 3.7+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Setup (2 minutes)

1. **Clone and setup**

```bash
git clone https://github.com/subhamghimire/code-editing-agent
cd code-editing-agent
pip install openai
```

2. **Set your API key**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. **Run it!**

```bash
python agent.py
```

## Try These Examples

### File Reading

```
You: What's in my agent.py file?
GPT: I'll read that file for you...
```

### Directory Exploration

```
You: What files are in this project?
GPT: Let me list the files in your directory...
```

### Code Creation

```
You: Create a FizzBuzz program in JavaScript
GPT: I'll create a fizzbuzz.js file with a working FizzBuzz implementation...
```

### Code Editing

```
You: Add comments to my Python code and fix any bugs
GPT: I'll read your code, analyze it, and make improvements...
```

### Complex Tasks

```
You: Create a ROT13 decoder that processes this string: 'Uryyb Jbeyq!'
GPT: I'll create a script that decodes ROT13 and processes your string...
```

## How It Works

The "magic" is surprisingly simple:

```
1. You type a message
2. Agent sends it to GPT + available tools
3. GPT decides which tools to use
4. Agent executes tools and sends results back
5. GPT gives you the final answer
6. Repeat!
```

### Available Tools

| Tool         | Description                       | Example Use                    |
| ------------ | --------------------------------- | ------------------------------ |
| `read_file`  | Read any file's contents          | "Show me my config file"       |
| `list_files` | List directory contents           | "What Python files do I have?" |
| `edit_file`  | Edit files via string replacement | "Fix the bug in line 42"       |

## What Makes This Special

- **Simple but Powerful** - Less than 300 lines, but handles complex tasks
- **Intelligent Tool Use** - GPT knows when and how to combine tools
- **Natural Conversation** - No special commands, just talk naturally
- **Extensible** - Easy to add new tools and capabilities
- **Python Native** - Uses familiar Python patterns and libraries

## Architecture

```python
# The core loop is surprisingly simple:
while True:
    user_input = get_user_message()
    response = gpt.chat(user_input, tools=available_tools)

    if response.wants_to_use_tool:
        result = execute_tool(response.tool_request)
        final_response = gpt.chat(result)

    print(final_response)
```

## Extending the Agent

Want to add more capabilities? Here are some ideas:

### System Tools

```python
# Run shell commands
def run_command(input_data):
    return subprocess.run(input_data['command'], capture_output=True, text=True)

# Search across files
def search_files(input_data):
    return grep_like_search(input_data['pattern'], input_data['directory'])
```

### Web Tools

```python
# Fetch web content
def fetch_url(input_data):
    return requests.get(input_data['url']).text

# Search the web
def web_search(input_data):
    return search_api(input_data['query'])
```

### Data Tools

```python
# Analyze CSV files
def analyze_csv(input_data):
    return pandas.read_csv(input_data['file']).describe()

# Generate plots
def create_plot(input_data):
    return matplotlib_plot(input_data['data'])
```

## Learning Resources

- **Original Blog Post**: [How to Build an Agent](https://ampcode.com/how-to-build-an-agent) by Thorsten Ball
- **OpenAI Function Calling**: [Documentation](https://platform.openai.com/docs/guides/function-calling)
- **OpenAI API**: [API Reference](https://platform.openai.com/docs/api-reference)

## Contributing

Found a bug? Want to add a feature? PRs welcome!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a PR

## Acknowledgments

- **Thorsten Ball** for the original [blog post](https://ampcode.com/how-to-build-an-agent) and Go implementation
- **OpenAI** for GPT and excellent function calling capabilities
- **The AI community** for showing us that the future is simpler than we thought

## The Big Picture

This project demonstrates a profound truth: **the most impressive AI capabilities often have surprisingly simple implementations**.

We're not just building a code editor - we're showing that:

- **Intelligence can be emergent** from simple patterns
- **Tools amplify AI capabilities** exponentially
- **The future is accessible** to anyone willing to try
- **"Magic" is often just** good engineering

## A Final Thought

As I've been learning and building this project, I've realized that the core of a code-editing agent isn't as complex as I initially thought. With just 300 lines of Python and three simple tools, you can create something powerful. While there's always room for more features—like editor integration, a better UI, or multi-agent support—I believe starting with these fundamentals has helped me understand the magic behind it all.

I'm hopeful that by sharing this journey, others can learn and build upon these basics too. The barrier to entry is lower than you might think, and I'm excited to see where this can take us.

---

_"It's an LLM, a loop, and enough tokens. The rest is elbow grease."_ - Thorsten Ball
