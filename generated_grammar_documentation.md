Output Model: send-message-to-user
  Description: 
        A model for sending messages to the user in an AI LLM agent swarm.

  Output Fields:
    chain_of_thought (str): 
      Description: Your inner thoughts or chain of thoughts while writing the message to the user.
    message (str): 
      Description: Message you want to send to the user.

Output Model: cmd-command-model
  Description: 
        A model for executing CMD commands in a Large Language Model setting.

  Output Fields:
    inner_thoughts (str): 
      Description: Your inner thoughts or inner monologue while writing the command.
    command (str): 
      Description: The CMD command to execute.
    require_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: web-browsing-model
  Description: 
        A model designed for handling web browsing operations in a Large Language Model context.
        It accommodates the  thought process in crafting the URL and includes a mechanism
        for sequential control through a heartbeat feature.

  Output Fields:
    inner_thoughts (str): 
      Description: Your inner thoughts or inner monologue while writing the url.
    URL (str): 
      Description: The URL you want to access.
    require_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: python-interpreter-command-model
  Description: 
        A model for executing Python commands in a Large Language Model framework.
        It incorporates the thought process during command creation and enables
        sequential task execution with a heartbeat mechanism.

  Output Fields:
    inner_thoughts (str): 
      Description: Your inner thoughts or inner monologue while writing the command.
    command (str): 
      Description: The Python command to execute.
    require_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: write-file-section-model
  Description: 
        A model for writing or modifying a section in a file in a Large Language Model setting.

  Output Fields:
    chain_of_thought (str): 
      Description: Detailed, step-by-step reasoning for the actions to be performed, ensuring clarity in the task execution process.
    folder (str): 
      Description: Path to the folder where the file is located or will be created. It should be a valid directory path.
    file_name (str): 
      Description: Name of the target file (excluding the file extension) where the section will be written or modified.
    file_extension (str): 
      Description: File extension indicating the file type, such as '.txt', '.py', '.md', etc.
    section (str): 
      Description: The specific section within the file to be targeted, such as a class, method, or a uniquely identified section.
    body (str): 
      Description: The actual content to be written into the specified section. It can be code, text, or data in a format compatible with the file type.
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: read-file-model
  Description: 
        A model for reading files in a Large Language Model setting.

  Output Fields:
    folder (str): 
      Description: Path to the folder containing the file.
    file_name (str): 
      Description: The name of the file to be read, including its extension (e.g., 'document.txt').
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: file-list-model
  Description: 
        A model for listing files in a directory in a Large Language Model setting.

  Output Fields:
    folder (str): 
      Description: Path to the directory where files will be listed. This path can include subdirectories to be scanned.
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: add-core-memory-model
  Description: 
        A model for adding new entries to the core memory of a Large Language Model.

  Output Fields:
    key (str): 
      Description: The key identifier for the core memory entry.
    field (str): 
      Description: A secondary key or field within the core memory entry.
    value (str): 
      Description: The value or data to be stored in the specified core memory entry.
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: replace-core-memory-model
  Description: 
        A model for replacing specific fields in the core memory of a Large Language Model.

  Output Fields:
    key (str): 
      Description: The key identifier for the core memory entry.
    field (str): 
      Description: The specific field within the core memory entry to be replaced.
    new_value (str): 
      Description: The new value to replace the existing data in the specified core memory field.
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

Output Model: remove-core-memory-model
  Description: 
        A model for removing specific fields from the core memory of a Large Language Model.

  Output Fields:
    key (str): 
      Description: The key identifier for the core memory entry to be removed.
    field (str): 
      Description: The specific field within the core memory entry to be removed.
    request_heartbeat (bool): 
      Description: Set this to true to get control back after execution, to chain functions together.

