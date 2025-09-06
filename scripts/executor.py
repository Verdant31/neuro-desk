from typing import Dict
from langchain_core.messages import AIMessage
from utils import get_custom_apps_paths, get_execution_plans_str
from helpers import get_settings, validate_agent_output, get_root_path
from tools import (
    launch_app,
    move_window,
    monitor_control,
    update_app_volume,
    close_app,
    split_screen,
    launch_chrome,
    shutdown,
    min_app,
    max_app,
    install_requirements,
    set_audio_input_device
)
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor

tools = [
    launch_app,
    move_window,
    monitor_control,
    update_app_volume,
    close_app,
    split_screen,
    launch_chrome,
    shutdown,
    min_app,
    max_app,
    install_requirements,
    set_audio_input_device
]

root_path = get_root_path()
settings = get_settings()
app_paths_str = get_custom_apps_paths(settings)
execution_plans_str = get_execution_plans_str(settings)

with open(root_path + "prompts/agent_executor.md", encoding="utf-8") as f:
    system_prompt = f.read().format(app_paths_str=app_paths_str,
                                    execution_plans_str=execution_plans_str)


class Executor():
    def __init__(self, mode: str = "auto"):

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        provider = (settings or {}).get("llm_provider", "ollama").lower()
        model = (settings or {}).get("llm_model")

        if provider == "openai":
            model = model or "gpt-4o-mini"
            llm = ChatOpenAI(
                model=model,
                temperature=0.0,
                api_key=(settings or {}).get("openai_api_key"),
                base_url=(settings or {}).get("openai_base_url"),
            )
        else:
            model = model or "llama3.1:8b"
            llm = ChatOllama(
                model=model,
                temperature=0.0,
            )

        if (mode == "auto"):
            agent = create_tool_calling_agent(llm, tools, prompt)
            executor = AgentExecutor(
                agent=agent, tools=tools, verbose=True, max_iterations=3,
                return_intermediate_steps=True,
                handle_parsing_errors=True,
                early_stopping_method="generate")
        else:
            executor = prompt | llm.bind_tools(tools)

        self.executor = executor
        self.mode = mode

    def run(self, data: Dict[str, str]):
        response = self.executor.invoke(data)
        if (self.mode == "auto"):
            if (isinstance(response, dict)):
                validate_agent_output(response)
        else:
            if isinstance(response, AIMessage) and response.tool_calls:
                tools_calls = response.tool_calls
                tools_by_name = {tool.name: tool for tool in tools}
                results = []
                for call in tools_calls:
                    tool_fn = tools_by_name[call["name"]]
                    result = tool_fn.invoke(call["args"])
                    results.append(
                        {"tool_call_id": call["id"], "output": result})
                print(results)
