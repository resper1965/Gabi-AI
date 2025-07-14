"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: mcp_server_seeder.py                                                  │
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

"""
Script to create default MCP servers:
- Brave Search
- Github
- Sequential Thinking
- Gitlab
- Airbnb
- Serper
- Firecrawl
Each with specific configurations
"""

import os
import sys
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from src.models.models import MCPServer
import uuid

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_mcp_servers():
    """Create default MCP servers in the system"""
    try:
        # Load environment variables
        load_dotenv()

        # Get database settings
        db_url = os.getenv("POSTGRES_CONNECTION_STRING")
        if not db_url:
            logger.error("Environment variable POSTGRES_CONNECTION_STRING not defined")
            return False

        # Connect to the database
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Check if there are already MCP servers
            existing_servers = session.query(MCPServer).all()
            if existing_servers:
                logger.info(
                    f"There are already {len(existing_servers)} MCP servers registered"
                )
                return True

            # MCP servers definitions
            mcp_servers = [
                {
                    "id": "b73dc2e8-9d91-4167-a8f1-1102c42af3d2",
                    "name": "Brave Search",
                    "description": "Brave Search allows you to seamlessly integrate Brave Search functionality into AI assistants like Claude. By implementing a Model Context Protocol (MCP) server, it enables the AI to leverage Brave Search's web search and local business search capabilities. It provides tools for both general web searches and specific local searches, enhancing the AI assistant's ability to provide relevant and up-to-date information.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                        "env": {"BRAVE_API_KEY": "env@@BRAVE_API_KEY"},
                    },
                    "environments": {"BRAVE_API_KEY": "env@@BRAVE_API_KEY"},
                    "tools": [
                        {
                            "id": "brave_web_search",
                            "name": "Web Search",
                            "description": "Perform web searches using Brave Search",
                            "tags": ["search", "web"],
                            "examples": [
                                "Search for Python documentation",
                                "Find information about AI",
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["application/json"],
                        },
                        {
                            "id": "brave_local_search",
                            "name": "Local Search",
                            "description": "Search for local businesses and places",
                            "tags": ["search", "local"],
                            "examples": [
                                "Find restaurants near me",
                                "Search for hotels in New York",
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["application/json"],
                        },
                    ],
                    "type": "official",
                },
                {
                    "id": "49c7b182-b341-4cc4-864c-7ae623ba41a7",
                    "name": "Github",
                    "description": "The GitHub MCP Server is a Model Context Protocol (MCP) server that provides seamless integration with GitHub APIs, enabling advanced automation and interaction capabilities for developers and tools.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "docker",
                        "args": [
                            "run",
                            "-i",
                            "--rm",
                            "-e",
                            "GITHUB_PERSONAL_ACCESS_TOKEN",
                            "ghcr.io/github/github-mcp-server",
                        ],
                        "env": {
                            "GITHUB_PERSONAL_ACCESS_TOKEN": "env@@GITHUB_PERSONAL_ACCESS_TOKEN"
                        },
                    },
                    "environments": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "env@@GITHUB_PERSONAL_ACCESS_TOKEN"
                    },
                    "tools": [
                        {
                            "id": "get_me",
                            "name": "get_me",
                            "description": "Get details of the authenticated user",
                            "tags": ["users,authentication,github"],
                            "examples": ["get me"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_issue",
                            "name": "get_issue",
                            "description": "Gets the contents of an issue within a repository",
                            "tags": ["issues,repository,read,github"],
                            "examples": ["get issue"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_issue_comments",
                            "name": "get_issue_comments",
                            "description": "Get comments for a GitHub issue",
                            "tags": ["issues,comments,read,github"],
                            "examples": ["get issue comments"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_issue",
                            "name": "create_issue",
                            "description": "Create a new issue in a GitHub repository",
                            "tags": ["issues,create,github"],
                            "examples": ["create issue"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "add_issue_comment",
                            "name": "add_issue_comment",
                            "description": "Add a comment to an issue",
                            "tags": ["issues,comments,create,github"],
                            "examples": ["add issue comment"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_issues",
                            "name": "list_issues",
                            "description": "List and filter repository issues",
                            "tags": ["issues,list,filter,github"],
                            "examples": ["list issues"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "update_issue",
                            "name": "update_issue",
                            "description": "Update an existing issue in a GitHub repository",
                            "tags": ["issues,update,github"],
                            "examples": ["update issue"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "search_issues",
                            "name": "search_issues",
                            "description": "Search for issues and pull requests",
                            "tags": ["issues,search,github"],
                            "examples": ["search issues"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_pull_request",
                            "name": "get_pull_request",
                            "description": "Get details of a specific pull request",
                            "tags": ["pull_requests,read"],
                            "examples": ["get pull request"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_pull_requests",
                            "name": "list_pull_requests",
                            "description": "List and filter repository pull requests",
                            "tags": ["pull_requests,list,filter,github"],
                            "examples": ["list pull requests"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "merge_pull_request",
                            "name": "merge_pull_request",
                            "description": "Merge a pull request",
                            "tags": ["pull_requests,merge,github"],
                            "examples": ["merge pull request"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_pull_request_files",
                            "name": "get_pull_request_files",
                            "description": "Get the list of files changed in a pull request",
                            "tags": ["pull_requests,files,read,github"],
                            "examples": ["get pull request files"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_pull_request_status",
                            "name": "get_pull_request_status",
                            "description": "Get the combined status of all status checks for a pull request",
                            "tags": ["pull_requests,status,read,github"],
                            "examples": ["get pull request status"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "update_pull_request_branch",
                            "name": "update_pull_request_branch",
                            "description": "Update a pull request branch with the latest changes from the base branch",
                            "tags": ["pull_requests,branch,update,github"],
                            "examples": ["update pull request branch"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_pull_request_comments",
                            "name": "get_pull_request_comments",
                            "description": "Get the review comments on a pull request",
                            "tags": ["pull_requests,comments,read,github"],
                            "examples": ["get pull request comments"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_pull_request_reviews",
                            "name": "get_pull_request_reviews",
                            "description": "Get the reviews on a pull request",
                            "tags": ["pull_requests,reviews,read,github"],
                            "examples": ["get pull request reviews"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_pull_request_review",
                            "name": "create_pull_request_review",
                            "description": "Create a review on a pull request review",
                            "tags": ["pull_requests,reviews,create,github"],
                            "examples": ["create pull request review"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_pull_request",
                            "name": "create_pull_request",
                            "description": "Create a new pull request",
                            "tags": ["pull_requests,create,github"],
                            "examples": ["create pull request"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "add_pull_request_review_comment",
                            "name": "add_pull_request_review_comment",
                            "description": "Add a review comment to a pull request or reply to an existing comment",
                            "tags": ["pull_requests,reviews,comments,create,github"],
                            "examples": ["add pull request review comment"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "update_pull_request",
                            "name": "update_pull_request",
                            "description": "Update an existing pull request in a GitHub repository",
                            "tags": ["pull_requests,update,github"],
                            "examples": ["update pull request"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_or_update_file",
                            "name": "create_or_update_file",
                            "description": "Create or update a single file in a repository",
                            "tags": ["repos,file,create,update,github"],
                            "examples": ["create or update file"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_branches",
                            "name": "list_branches",
                            "description": "List branches in a GitHub repository",
                            "tags": ["repos,branches,list,github"],
                            "examples": ["list branches"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "push_files",
                            "name": "push_files",
                            "description": "Push multiple files in a single commit",
                            "tags": ["repos,files,push,github"],
                            "examples": ["push files"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "search_repositories",
                            "name": "search_repositories",
                            "description": "Search for GitHub repositories",
                            "tags": ["repos,search,github"],
                            "examples": ["search repositories"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_repository",
                            "name": "create_repository",
                            "description": "Create a new GitHub repository",
                            "tags": ["repos,create,github"],
                            "examples": ["create repository"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_file_contents",
                            "name": "get_file_contents",
                            "description": "Get contents of a file or directory",
                            "tags": ["repos,file,read,github"],
                            "examples": ["get file contents"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "fork_repository",
                            "name": "fork_repository",
                            "description": "Fork a repository",
                            "tags": ["repos,fork,github"],
                            "examples": ["fork repository"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_branch",
                            "name": "create_branch",
                            "description": "Create a new branch",
                            "tags": ["repos,branch,create,github"],
                            "examples": ["create branch"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_commits",
                            "name": "list_commits",
                            "description": "Get a list of commits of a branch in a repository",
                            "tags": ["repos,commits,list,github"],
                            "examples": ["list commits"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_commit",
                            "name": "get_commit",
                            "description": "Get details for a commit from a repository",
                            "tags": ["repos,commit,read,github"],
                            "examples": ["get commit"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "search_code",
                            "name": "search_code",
                            "description": "Search for code across GitHub repositories",
                            "tags": ["repos,code,search,github"],
                            "examples": ["search code"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "search_users",
                            "name": "search_users",
                            "description": "Search for GitHub users",
                            "tags": ["users,search,github"],
                            "examples": ["search users"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_code_scanning_alert",
                            "name": "get_code_scanning_alert",
                            "description": "Get a code scanning alert",
                            "tags": ["code_security,alert,github"],
                            "examples": ["get code scanning alert"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_code_scanning_alerts",
                            "name": "list_code_scanning_alerts",
                            "description": "List code scanning alerts for a repository",
                            "tags": ["code_security,alerts,github"],
                            "examples": ["list code scanning alerts"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "get_secret_scanning_alert",
                            "name": "get_secret_scanning_alert",
                            "description": "Get a secret scanning alert",
                            "tags": ["code_security,alert,secret,github"],
                            "examples": ["get secret scanning alert"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "list_secret_scanning_alerts",
                            "name": "list_secret_scanning_alerts",
                            "description": "List secret scanning alerts for a repository",
                            "tags": ["code_security,alerts,secret,github"],
                            "examples": ["list secret scanning alerts"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                    ],
                    "type": "official",
                },
                {
                    "id": "6e878520-4a49-45f8-b42c-621bffcf70bf",
                    "name": "Sequential Thinking",
                    "description": "Sequential Thinking helps users organize their thoughts and break down complex problems through a structured workflow. By guiding users through defined cognitive stages like Problem Definition, Research, Analysis, Synthesis, and Conclusion, it provides a framework for progressive thinking. The server tracks the progression of your thinking process, identifies connections between similar thoughts, monitors progress, and generates summaries, making it easier to approach challenges methodically and reach well-reasoned conclusions.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": [
                            "-y",
                            "@modelcontextprotocol/server-sequential-thinking",
                        ],
                        "env": {},
                    },
                    "environments": {},
                    "tools": [
                        {
                            "id": "sequentialthinking",
                            "name": "Sequential Thinking",
                            "description": "Helps organize thoughts and break down complex problems through a structured workflow",
                            "tags": ["thinking", "analysis", "problem-solving"],
                            "examples": [
                                "Help me analyze this problem",
                                "Guide me through this decision making process",
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        }
                    ],
                    "type": "official",
                },
                {
                    "id": "b626b528-13ac-4d63-aa74-c4acecde9e29",
                    "name": "Gitlab",
                    "description": "MCP Server for the GitLab API, enabling project management, file operations, and more.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-gitlab"],
                        "env": {
                            "GITLAB_PERSONAL_ACCESS_TOKEN": "env@@GITLAB_PERSONAL_ACCESS_TOKEN",
                            "GITLAB_API_URL": "env@@GITLAB_API_URL",
                        },
                    },
                    "environments": {
                        "GITLAB_PERSONAL_ACCESS_TOKEN": "env@@GITLAB_PERSONAL_ACCESS_TOKEN",
                        "GITLAB_API_URL": "env@@GITLAB_API_URL",
                    },
                    "tools": [
                        {
                            "id": "create_or_update_file",
                            "name": "create_or_update_file",
                            "description": "Create or update a single file in a project",
                            "tags": ["repos", "files", "create", "update", "gitlab"],
                            "examples": ["create or update file"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "push_files",
                            "name": "push_files",
                            "description": "Push multiple files in a single commit",
                            "tags": ["repos", "files", "push", "gitlab"],
                            "examples": ["push files"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "search_repositories",
                            "name": "search_repositories",
                            "description": "Search for GitLab projects",
                            "tags": ["repos", "search", "gitlab"],
                            "examples": ["search repositories"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_repository",
                            "name": "create_repository",
                            "description": "Create a new GitLab project",
                            "tags": ["repos", "create", "gitlab"],
                            "examples": ["create repository"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_issue",
                            "name": "create_issue",
                            "description": "Create a new issue",
                            "tags": ["issues", "create", "gitlab"],
                            "examples": ["create issue"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_merge_request",
                            "name": "create_merge_request",
                            "description": "Create a new merge request",
                            "tags": ["merge_requests", "create", "gitlab"],
                            "examples": ["create merge request"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "fork_repository",
                            "name": "fork_repository",
                            "description": "Fork a project",
                            "tags": ["repos", "fork", "gitlab"],
                            "examples": ["fork repository"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "create_branch",
                            "name": "create_branch",
                            "description": "Create a new branch",
                            "tags": ["branches", "create", "gitlab"],
                            "examples": ["create branch"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                    ],
                    "type": "official",
                },
                {
                    "id": "7bb73ef1-22da-4c05-a05d-d31db4243560",
                    "name": "Airbnb",
                    "description": "MCP Server for searching Airbnb and get listing details.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": ["-y", "@openbnb/mcp-server-airbnb"],
                        "env": {},
                    },
                    "environments": {},
                    "tools": [
                        {
                            "id": "airbnb_search",
                            "name": "airbnb_search",
                            "description": "Search for Airbnb listings.",
                            "tags": ["airbnb", "search", "listings", "travel"],
                            "examples": ["search airbnb listings"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "airbnb_listing_details",
                            "name": "airbnb_listing_details",
                            "description": "Get detailed information about a specific Airbnb listing.",
                            "tags": ["airbnb", "listings", "details", "travel"],
                            "examples": ["get airbnb listing details"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                    ],
                    "type": "official",
                },
                {
                    "id": "ae214cb1-92f0-473c-93a3-e2075884bf4d",
                    "name": "Serper",
                    "description": "A TypeScript-based MCP server that provides web search and webpage scraping capabilities using the Serper API. This server integrates with Claude Desktop to enable powerful web search and content extraction features.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": ["-y", "serper-search-scrape-mcp-server"],
                        "env": {"SERPER_API_KEY": "env@@SERPER_API_KEY"},
                    },
                    "environments": {"SERPER_API_KEY": "env@@SERPER_API_KEY"},
                    "tools": [
                        {
                            "id": "google_search",
                            "name": "google_search",
                            "description": 'Perform web searches via the Serper API, returning rich results such as organic hits, knowledge graph data, "people also ask", related searches, and supporting region/language targeting, pagination, autocorrection and advanced search operators.',
                            "tags": [
                                "search",
                                "web",
                                "information_retrieval",
                                "serper_api",
                            ],
                            "examples": ["search web for Rust programming tutorials"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "scrape",
                            "name": "scrape",
                            "description": "Extract content from web pages, returning plain text or optional markdown, including JSON-LD and head metadata, while preserving document structure.",
                            "tags": [
                                "web_scraping",
                                "content_extraction",
                                "text_processing",
                                "api",
                            ],
                            "examples": ["scrape https://example.com/article"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                    ],
                    "type": "official",
                },
                {
                    "id": "01bcc7ef-a6a5-4264-9e47-9f565499eaaa",
                    "name": "Firecrawl",
                    "description": "A Model Context Protocol (MCP) server implementation that integrates with Firecrawl for web scraping capabilities.",
                    "config_type": "studio",
                    "config_json": {
                        "command": "npx",
                        "args": ["-y", "firecrawl-mcp"],
                        "env": {"FIRECRAWL_API_KEY": "env@@FIRECRAWL_API_KEY"},
                    },
                    "environments": {"FIRECRAWL_API_KEY": "env@@FIRECRAWL_API_KEY"},
                    "tools": [
                        {
                            "id": "firecrawl_scrape",
                            "name": "firecrawl_scrape",
                            "description": "Scrape content from a single URL with advanced options (formats, main-content only, JS rendering, etc.).",
                            "tags": [
                                "scraping",
                                "web",
                                "content_extraction",
                                "firecrawl",
                            ],
                            "examples": ["firecrawl_scrape https://example.com"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_batch_scrape",
                            "name": "firecrawl_batch_scrape",
                            "description": "Scrape multiple URLs efficiently using built-in rate limiting and parallel processing. ",
                            "tags": ["scraping", "batch_processing", "parallel"],
                            "examples": [
                                "firecrawl_batch_scrape https://site1.com",
                                "https://site2.com",
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_check_batch_status",
                            "name": "firecrawl_check_batch_status",
                            "description": "Check the status of a previously queued batch scrape operation.",
                            "tags": ["scraping", "batch_processing", "monitoring"],
                            "examples": ["firecrawl_check_batch_status batch_1"],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_search",
                            "name": "firecrawl_search",
                            "description": "Perform a web search and optionally scrape content from the top results.",
                            "tags": ["search", "web", "scraping"],
                            "examples": [
                                "firecrawl_search how does carbon capture technology work"
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_crawl",
                            "name": "firecrawl_crawl",
                            "description": "Start an asynchronous crawl from a seed URL with options for depth, link limits, deduplication, etc.",
                            "tags": ["crawling", "web", "link_discovery"],
                            "examples": [
                                "firecrawl_crawl https://example.com --maxDepth 2 --limit 100"
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_extract",
                            "name": "firecrawl_extract",
                            "description": "Extract structured data from one or more pages using LLM-guided prompts and a JSON schema.",
                            "tags": ["extraction", "llm", "structured_data"],
                            "examples": [
                                "firecrawl_extract https://site.com/page1",
                                "https://site.com/page2",
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_deep_research",
                            "name": "firecrawl_deep_research",
                            "description": "Conduct deep web research on a topic by combining crawling, search, and LLM analysis into a single workflow.",
                            "tags": ["research", "web", "llm_analysis"],
                            "examples": [
                                "firecrawl_deep_research impact of renewable energy subsidies"
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                        {
                            "id": "firecrawl_generate_llmstxt",
                            "name": "firecrawl_generate_llmstxt",
                            "description": "Generate a standardized llms.txt (and optionally llms-full.txt) file for a domain, guiding how LLMs should interact with that site.",
                            "tags": ["site_policy", "metadata", "llms"],
                            "examples": [
                                "firecrawl_generate_llmstxt https://example.com"
                            ],
                            "inputModes": ["text"],
                            "outputModes": ["text"],
                        },
                    ],
                    "type": "official",
                },
            ]

            # Create the MCP servers
            for server_data in mcp_servers:
                server = MCPServer(
                    id=uuid.UUID(server_data["id"]),
                    name=server_data["name"],
                    description=server_data["description"],
                    config_type=server_data["config_type"],
                    config_json=server_data["config_json"],
                    environments=server_data["environments"],
                    tools=server_data["tools"],
                    type=server_data["type"],
                )

                session.add(server)
                logger.info(f"MCP server '{server_data['name']}' created successfully")

            session.commit()
            logger.info("All MCP servers were created successfully")
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error when creating MCP servers: {str(e)}")
            return False
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error when creating MCP servers: {str(e)}")
        return False


if __name__ == "__main__":
    success = create_mcp_servers()
    sys.exit(0 if success else 1)
