"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: custom_tool.py                                                        │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
│                                                                              │
│ You may not use this file except in compliance with the License.             │
│ You may obtain a copy of the License at                                      │
│                                                                              │
│    http://www.apache.org/licenses/LICENSE-2.0                                │
│                                                                              │
│ Unless required by applicable law or agreed to in writing, software          │
│ distributed under the License is distributed on an "AS IS" BASIS,            │
│ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.     │
│ See the License for the specific language governing permissions and          │
│ limitations under the License.                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ @important                                                                   │
│ For any future changes to the code in this file, it is recommended to        │
│ include, together with the modification, the information of the developer    │
│ who changed it and the date of modification.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from typing import Any, Dict, List, Type
from crewai.tools import BaseTool, tool
import requests
import json
from src.utils.logger import setup_logger
from pydantic import BaseModel, Field, create_model

logger = setup_logger(__name__)


class CustomToolBuilder:
    def __init__(self):
        self.tools = []

    def _create_http_tool(self, tool_config: Dict[str, Any]) -> BaseTool:
        """Create an HTTP tool based on the provided configuration."""
        # Extract configuration parameters
        name = tool_config["name"]
        description = tool_config["description"]
        endpoint = tool_config["endpoint"]
        method = tool_config["method"]
        headers = tool_config.get("headers", {})
        parameters = tool_config.get("parameters", {}) or {}
        values = tool_config.get("values", {})
        error_handling = tool_config.get("error_handling", {})

        path_params = parameters.get("path_params") or {}
        query_params = parameters.get("query_params") or {}
        body_params = parameters.get("body_params") or {}

        # Dynamic creation of the input schema for the tool
        field_definitions = {}

        # Add all parameters as fields
        for param in (
            list(path_params.keys())
            + list(query_params.keys())
            + list(body_params.keys())
        ):
            # Default to string type for all parameters
            field_definitions[param] = (
                str,
                Field(..., description=f"Parameter {param}"),
            )

        # If there are no parameters but default values, use those as optional fields
        if not field_definitions and values:
            for param, value in values.items():
                param_type = type(value)
                field_definitions[param] = (
                    param_type,
                    Field(default=value, description=f"Parameter {param}"),
                )

        # Create dynamic input schema model in line with the documentation
        tool_input_model = create_model(
            f"{name.replace(' ', '')}Input", **field_definitions
        )

        # Create the HTTP tool using crewai's BaseTool class
        # Following the pattern in the documentation
        def create_http_tool_class():
            # Capture variables from outer scope
            _name = name
            _description = description
            _tool_input_model = tool_input_model

            class HttpTool(BaseTool):
                name: str = _name
                description: str = _description
                args_schema: Type[BaseModel] = _tool_input_model

                def _run(self, **kwargs):
                    """Execute the HTTP request and return the result."""
                    try:
                        # Combines default values with provided values
                        all_values = {**values, **kwargs}

                        # Substitutes placeholders in headers
                        processed_headers = {
                            k: v.format(**all_values) if isinstance(v, str) else v
                            for k, v in headers.items()
                        }

                        # Processes path parameters
                        url = endpoint
                        for param, value in path_params.items():
                            if param in all_values:
                                url = url.replace(
                                    f"{{{param}}}", str(all_values[param])
                                )

                        # Process query parameters
                        query_params_dict = {}
                        for param, value in query_params.items():
                            if isinstance(value, list):
                                # If the value is a list, join with comma
                                query_params_dict[param] = ",".join(value)
                            elif param in all_values:
                                # If the parameter is in the values, use the provided value
                                query_params_dict[param] = all_values[param]
                            else:
                                # Otherwise, use the default value from the configuration
                                query_params_dict[param] = value

                        # Adds default values to query params if they are not present
                        for param, value in values.items():
                            if (
                                param not in query_params_dict
                                and param not in path_params
                            ):
                                query_params_dict[param] = value

                        body_data = {}
                        for param, param_config in body_params.items():
                            if param in all_values:
                                body_data[param] = all_values[param]

                        # Adds default values to body if they are not present
                        for param, value in values.items():
                            if (
                                param not in body_data
                                and param not in query_params_dict
                                and param not in path_params
                            ):
                                body_data[param] = value

                        # Makes the HTTP request
                        response = requests.request(
                            method=method,
                            url=url,
                            headers=processed_headers,
                            params=query_params_dict,
                            json=body_data or None,
                            timeout=error_handling.get("timeout", 30),
                        )

                        if response.status_code >= 400:
                            raise requests.exceptions.HTTPError(
                                f"Error in the request: {response.status_code} - {response.text}"
                            )

                        # Always returns the response as a string
                        return json.dumps(response.json())

                    except Exception as e:
                        logger.error(f"Error executing tool {name}: {str(e)}")
                        return json.dumps(
                            error_handling.get(
                                "fallback_response",
                                {"error": "tool_execution_error", "message": str(e)},
                            )
                        )

            return HttpTool

        # Create the tool instance
        HttpToolClass = create_http_tool_class()
        http_tool = HttpToolClass()

        # Add cache function following the documentation
        def http_cache_function(arguments: dict, result: str) -> bool:
            """Determines whether to cache the result based on arguments and result."""
            # Default implementation: cache all successful results
            try:
                # If the result is parseable JSON and not an error, cache it
                result_obj = json.loads(result)
                return not (isinstance(result_obj, dict) and "error" in result_obj)
            except Exception:
                # If result is not valid JSON, don't cache
                return False

        # Assign the cache function to the tool
        http_tool.cache_function = http_cache_function

        return http_tool

    def _create_http_tool_with_decorator(self, tool_config: Dict[str, Any]) -> Any:
        """Create an HTTP tool using the tool decorator."""
        # Extract configuration parameters
        name = tool_config["name"]
        description = tool_config["description"]
        endpoint = tool_config["endpoint"]
        method = tool_config["method"]
        headers = tool_config.get("headers", {})
        parameters = tool_config.get("parameters", {}) or {}
        values = tool_config.get("values", {})
        error_handling = tool_config.get("error_handling", {})

        path_params = parameters.get("path_params") or {}
        query_params = parameters.get("query_params") or {}
        body_params = parameters.get("body_params") or {}

        # Create function docstring with parameter documentation
        param_list = (
            list(path_params.keys())
            + list(query_params.keys())
            + list(body_params.keys())
        )
        doc_params = []
        for param in param_list:
            doc_params.append(f"    {param}: Parameter description")

        docstring = (
            f"{description}\n\nParameters:\n"
            + "\n".join(doc_params)
            + "\n\nReturns:\n    String containing the response in JSON format"
        )

        # Create the tool function using the decorator pattern in the documentation
        @tool(name=name)
        def http_tool(**kwargs):
            """Tool function created dynamically."""
            try:
                # Combines default values with provided values
                all_values = {**values, **kwargs}

                # Substitutes placeholders in headers
                processed_headers = {
                    k: v.format(**all_values) if isinstance(v, str) else v
                    for k, v in headers.items()
                }

                # Processes path parameters
                url = endpoint
                for param, value in path_params.items():
                    if param in all_values:
                        url = url.replace(f"{{{param}}}", str(all_values[param]))

                # Process query parameters
                query_params_dict = {}
                for param, value in query_params.items():
                    if isinstance(value, list):
                        # If the value is a list, join with comma
                        query_params_dict[param] = ",".join(value)
                    elif param in all_values:
                        # If the parameter is in the values, use the provided value
                        query_params_dict[param] = all_values[param]
                    else:
                        # Otherwise, use the default value from the configuration
                        query_params_dict[param] = value

                # Adds default values to query params if they are not present
                for param, value in values.items():
                    if param not in query_params_dict and param not in path_params:
                        query_params_dict[param] = value

                body_data = {}
                for param, param_config in body_params.items():
                    if param in all_values:
                        body_data[param] = all_values[param]

                # Adds default values to body if they are not present
                for param, value in values.items():
                    if (
                        param not in body_data
                        and param not in query_params_dict
                        and param not in path_params
                    ):
                        body_data[param] = value

                # Makes the HTTP request
                response = requests.request(
                    method=method,
                    url=url,
                    headers=processed_headers,
                    params=query_params_dict,
                    json=body_data or None,
                    timeout=error_handling.get("timeout", 30),
                )

                if response.status_code >= 400:
                    raise requests.exceptions.HTTPError(
                        f"Error in the request: {response.status_code} - {response.text}"
                    )

                # Always returns the response as a string
                return json.dumps(response.json())

            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return json.dumps(
                    error_handling.get(
                        "fallback_response",
                        {"error": "tool_execution_error", "message": str(e)},
                    )
                )

        # Replace the docstring
        http_tool.__doc__ = docstring

        # Add cache function following the documentation
        def http_cache_function(arguments: dict, result: str) -> bool:
            """Determines whether to cache the result based on arguments and result."""
            # Default implementation: cache all successful results
            try:
                # If the result is parseable JSON and not an error, cache it
                result_obj = json.loads(result)
                return not (isinstance(result_obj, dict) and "error" in result_obj)
            except Exception:
                # If result is not valid JSON, don't cache
                return False

        # Assign the cache function to the tool
        http_tool.cache_function = http_cache_function

        return http_tool

    def build_tools(self, tools_config: Dict[str, Any]) -> List[BaseTool]:
        """Builds a list of tools based on the provided configuration. Accepts both 'tools' and 'custom_tools' (with http_tools)."""
        self.tools = []

        # Find HTTP tools configuration in various possible locations
        http_tools = []
        if tools_config.get("http_tools"):
            http_tools = tools_config.get("http_tools", [])
        elif tools_config.get("custom_tools") and tools_config["custom_tools"].get(
            "http_tools"
        ):
            http_tools = tools_config["custom_tools"].get("http_tools", [])
        elif (
            tools_config.get("tools")
            and isinstance(tools_config["tools"], dict)
            and tools_config["tools"].get("http_tools")
        ):
            http_tools = tools_config["tools"].get("http_tools", [])

        # Determine which implementation method to use (BaseTool or decorator)
        use_decorator = tools_config.get("use_decorator", False)

        # Create tools for each HTTP tool configuration
        for http_tool_config in http_tools:
            if use_decorator:
                self.tools.append(
                    self._create_http_tool_with_decorator(http_tool_config)
                )
            else:
                self.tools.append(self._create_http_tool(http_tool_config))

        return self.tools
