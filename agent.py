#!/usr/bin/env python3
"""
Code-Editing Agent in Python with OpenAI API
"""

import json
import os
import sys
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from openai import OpenAI


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable[[Dict[str, Any]], str]


class Agent:
    def __init__(self, client: OpenAI, get_user_message: Callable[[], Tuple[str, bool]], tools: List[ToolDefinition]):
        self.client = client
        self.get_user_message = get_user_message
        self.tools = tools
    
    def run(self):
        messages = []
        print("Chat with GPT (use 'ctrl-c' to quit)")
        
        try:
            while True:
                print("\033[94mYou\033[0m: ", end="")
                user_input, ok = self.get_user_message()
                if not ok:
                    break
                
                # Add user message
                messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Get response from OpenAI
                response = self._run_inference(messages)
                
                # Add assistant message
                messages.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                    "tool_calls": response.choices[0].message.tool_calls
                })
                
                # Check if assistant wants to use tools
                if response.choices[0].message.tool_calls:
                    # Execute all requested tools
                    for tool_call in response.choices[0].message.tool_calls:
                        tool_result = self._execute_tool(
                            tool_call.id,
                            tool_call.function.name,
                            json.loads(tool_call.function.arguments)
                        )
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                    
                    # Get final response after tool execution
                    final_response = self._run_inference(messages)
                    messages.append({
                        "role": "assistant",
                        "content": final_response.choices[0].message.content
                    })
                    
                    print(f"\033[93mGPT\033[0m: {final_response.choices[0].message.content}")
                else:
                    # No tools used, just print the response
                    print(f"\033[93mGPT\033[0m: {response.choices[0].message.content}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    def _run_inference(self, messages: List[Dict[str, Any]]):
        # Convert our tools to OpenAI's format
        tools = []
        for tool in self.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or "gpt-3.5-turbo" for lower cost
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto"  # Let the model decide when to use tools
        )
        
        return response
    
    def _execute_tool(self, tool_call_id: str, name: str, arguments: Dict[str, Any]) -> str:
        # Find the tool
        tool_def = None
        for tool in self.tools:
            if tool.name == name:
                tool_def = tool
                break
        
        if not tool_def:
            return "Error: tool not found"
        
        print(f"\033[92mtool\033[0m: {name}({json.dumps(arguments)})")
        
        try:
            response = tool_def.function(arguments)
            return response
        except Exception as e:
            return f"Error: {str(e)}"


# Tool implementations
def read_file(arguments: Dict[str, Any]) -> str:
    """Read the contents of a given relative file path."""
    path = arguments.get("path", "")
    if not path:
        raise ValueError("Path is required")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


def list_files(arguments: Dict[str, Any]) -> str:
    """List files and directories at a given path."""
    path = arguments.get("path", ".")
    
    try:
        files = []
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        if path_obj.is_file():
            return json.dumps([str(path_obj)])
        
        for item in sorted(path_obj.iterdir()):
            if item.is_dir():
                files.append(f"{item.name}/")
            else:
                files.append(item.name)
        
        return json.dumps(files)
    except Exception as e:
        raise Exception(f"Error listing files: {str(e)}")


def edit_file(arguments: Dict[str, Any]) -> str:
    """Make edits to a text file by replacing old_str with new_str."""
    path = arguments.get("path", "")
    old_str = arguments.get("old_str", "")
    new_str = arguments.get("new_str", "")
    
    if not path:
        raise ValueError("Path is required")
    
    if old_str == new_str:
        raise ValueError("old_str and new_str must be different")
    
    try:
        # If file doesn't exist and old_str is empty, create new file
        if not os.path.exists(path) and old_str == "":
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_str)
            return f"Successfully created file {path}"
        
        # Read existing file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace content
        if old_str and old_str not in content:
            raise ValueError("old_str not found in file")
        
        new_content = content.replace(old_str, new_str)
        
        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return "OK"
    
    except Exception as e:
        raise Exception(f"Error editing file: {str(e)}")


# Tool definitions for OpenAI
READ_FILE_DEFINITION = ToolDefinition(
    name="read_file",
    description="Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The relative path of a file in the working directory."
            }
        },
        "required": ["path"]
    },
    function=read_file
)

LIST_FILES_DEFINITION = ToolDefinition(
    name="list_files",
    description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional relative path to list files from. Defaults to current directory if not provided."
            }
        }
    },
    function=list_files
)

EDIT_FILE_DEFINITION = ToolDefinition(
    name="edit_file",
    description="""Make edits to a text file.
Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other.
If the file specified with path doesn't exist, it will be created.""",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file"
            },
            "old_str": {
                "type": "string",
                "description": "Text to search for - must match exactly"
            },
            "new_str": {
                "type": "string",
                "description": "Text to replace old_str with"
            }
        },
        "required": ["path", "old_str", "new_str"]
    },
    function=edit_file
)


def get_user_message() -> Tuple[str, bool]:
    """Get user input from stdin."""
    try:
        line = input()
        return line, True
    except EOFError:
        return "", False


def main():
    # Initialize OpenAI client (requires OPENAI_API_KEY environment variable)
    client = OpenAI()
    
    # Define available tools
    tools = [
        READ_FILE_DEFINITION,
        LIST_FILES_DEFINITION,
        EDIT_FILE_DEFINITION
    ]
    
    # Create and run the agent
    agent = Agent(client, get_user_message, tools)
    agent.run()


if __name__ == "__main__":
    main()