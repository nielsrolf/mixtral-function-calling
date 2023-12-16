from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from grammar_generator import generate_and_save_gbnf_grammar_and_documentation

class Department(Enum):
    """Enum for department names."""
    HR = 'Human Resources'
    IT = 'Information Technology'
    SALES = 'Sales'
    MARKETING = 'Marketing'


class SkillSet:
    """Skillset of the employee."""
    primary_skill: str = Field(..., description="Primary skill of the employee.")
    secondary_skills: List[str] = Field(..., description="List of secondary skills.")


class ComplexEmployeeModel:
    employee_id: int
    name: str = Field(..., description="Name of the employee.")
    department: Department = Field(..., description="Department of the employee.")
    skill_set: SkillSet = Field(..., description="Skillset of the employee.")
    experience_years: float = Field(..., description="Years of experience.")
    is_full_time: bool = Field(True, description="Is the employee full-time.")


# Cmd Command Model
class CmdCommandModel(BaseModel):
    """
    A model for executing CMD commands in a Large Language Model setting.
    """
    inner_thoughts: str = Field(..., description="Your inner thoughts or inner monologue while writing the command.")
    command: str = Field(..., description="The CMD command to execute.")
    require_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Web Browsing Model
class WebBrowsingModel(BaseModel):
    """
    A model designed for handling web browsing operations in a Large Language Model context.
    It accommodates the  thought process in crafting the URL and includes a mechanism
    for sequential control through a heartbeat feature.
    """

    inner_thoughts: str = Field(..., description="Your inner thoughts or inner monologue while writing the url.")
    URL: str = Field(..., description="The URL you want to access.")
    require_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Web Download Model
class WebDownloadModel(BaseModel):
    """
    A model for managing web content downloads in a Large Language Model setting.
    It captures the considerations in selecting the URL and download path,
    and supports chained execution via a heartbeat mechanism.
    """
    inner_thoughts: str = Field(..., description="Your inner thoughts or inner monologue while writing the url.")
    URL: str = Field(..., description="The URL you want to download.")
    Path: str = Field(..., description="The Path you want to download the file to.")
    require_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Python Interpreter Command Model
class PythonInterpreterCommandModel(BaseModel):
    """
    A model for executing Python commands in a Large Language Model framework.
    It incorporates the thought process during command creation and enables
    sequential task execution with a heartbeat mechanism.
    """
    inner_thoughts: str = Field(..., description="Your inner thoughts or inner monologue while writing the command.")
    command: str = Field(..., description="The Python command to execute.")
    require_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Write File Section Model
class WriteFileSectionModel(BaseModel):
    """
    A model for writing or modifying a section in a file in a Large Language Model setting.
    """
    chain_of_thought: str = Field(...,
                                  description="Detailed, step-by-step reasoning for the actions to be performed, ensuring clarity in the task execution process.")
    folder: str = Field(...,
                        description="Path to the folder where the file is located or will be created. It should be a valid directory path.")
    file_name: str = Field(...,
                           description="Name of the target file (excluding the file extension) where the section will be written or modified.")
    file_extension: str = Field(...,
                                description="File extension indicating the file type, such as '.txt', '.py', '.md', etc.")
    section: str = Field(...,
                         description="The specific section within the file to be targeted, such as a class, method, or a uniquely identified section.")
    body: str = Field(...,
                      description="The actual content to be written into the specified section. It can be code, text, or data in a format compatible with the file type.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Read File Model
class ReadFileModel(BaseModel):
    """
    A model for reading files in a Large Language Model setting.
    """
    folder: str = Field(None, description="Path to the folder containing the file.")
    file_name: str = Field(...,
                           description="The name of the file to be read, including its extension (e.g., 'document.txt').")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# File List Model
class FileListModel(BaseModel):
    """
    A model for listing files in a directory in a Large Language Model setting.
    """
    folder: str = Field(...,
                        description="Path to the directory where files will be listed. This path can include subdirectories to be scanned.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


class AddCoreMemoryModel(BaseModel):
    """
    A model for adding new entries to the core memory of a Large Language Model.
    """
    key: str = Field(..., description="The key identifier for the core memory entry.")
    field: str = Field(..., description="A secondary key or field within the core memory entry.")
    value: str = Field(..., description="The value or data to be stored in the specified core memory entry.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Replace Core Memory Model
class ReplaceCoreMemoryModel(BaseModel):
    """
    A model for replacing specific fields in the core memory of a Large Language Model.
    """
    key: str = Field(..., description="The key identifier for the core memory entry.")
    field: str = Field(..., description="The specific field within the core memory entry to be replaced.")
    new_value: str = Field(...,
                           description="The new value to replace the existing data in the specified core memory field.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Remove Core Memory Model
class RemoveCoreMemoryModel(BaseModel):
    """
    A model for removing specific fields from the core memory of a Large Language Model.
    """
    key: str = Field(..., description="The key identifier for the core memory entry to be removed.")
    field: str = Field(..., description="The specific field within the core memory entry to be removed.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Defining the RolesEnum
class RolesEnum(str, Enum):
    EVENT_MEMORY_SEARCH = "Event-Memory-Search"
    KNOWLEDGE_MEMORY_SEARCH = "Knowledge-Memory-Search"
    MESSAGE_FROM_SWARM = "Message-From-Swarm"
    MESSAGE_FROM_USER = "Message-From-User"
    SYSTEM_MESSAGE = "System-Message"


# Search Event Memory Model
class SearchEventMemoryModel(BaseModel):
    """
    A model for searching event memories in a Large Language Model.
    """
    event_types: List[RolesEnum] = Field(..., description="Array of event types to filter the search.")
    start_date: str = Field(..., description="The starting date for the event search range.")
    end_date: str = Field(..., description="The ending date for the event search range.")
    content_keywords: List[str] = Field(..., description="Array of keywords to search within the event content.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Search Knowledge Model
class SearchKnowledgeModel(BaseModel):
    """
    A model for searching knowledge memories in a Large Language Model.
    """
    query: str = Field(..., description="The query string to search within the 'Knowledge-Memory'.")
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Connect Knowledge Memories Model
class ConnectKnowledgeMemoriesModel(BaseModel):
    """
    A model for connecting knowledge memories in a Large Language Model.
    """
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


# Self Reflect Model
class SelfReflectModel(BaseModel):
    """
    A model for enabling self-reflection in a Large Language Model.
    """
    request_heartbeat: bool = Field(...,
                                    description="Set this to true to get control back after execution, to chain functions together.")


class SendMessageToUser(BaseModel):
    """
    A model for sending messages to the user in an AI LLM agent swarm.
    """

    chain_of_thought: str = Field(...,
                                  description="Your inner thoughts or chain of thoughts while writing the message to the user.")
    message: str = Field(..., description="Message you want to send to the user.")


generate_and_save_gbnf_grammar_and_documentation(
    [SendMessageToUser, CmdCommandModel, WebBrowsingModel, PythonInterpreterCommandModel, WriteFileSectionModel,
     ReadFileModel,
     FileListModel, AddCoreMemoryModel, ReplaceCoreMemoryModel, RemoveCoreMemoryModel], root_rule_class="function",
    root_rule_content="function-parameters")