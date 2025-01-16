import os, sys
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FileSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor


application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

project_client.telemetry.enable(destination=sys.stdout)

with tracer.start_as_current_span(scenario):
    with project_client:
        try :
            
            # Upload file and create vector store
            # [START upload_file_create_vector_store_and_agent_with_file_search_tool]
            file = project_client.agents.upload_file_and_poll(file_path="product_info.md", purpose="assistants")
            print(f"Uploaded file, file ID: {file.id}")

            vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
            print(f"Created vector store, vector store ID: {vector_store.id}")

            # Create file search tool with resources followed by creating agent
            file_search = FileSearchTool(vector_store_ids=[vector_store.id])

            agent = project_client.agents.create_agent(
                model="gpt-4o-mini",
                name="my-assistant",
                instructions="Hello, you are helpful assistant and can search information from uploaded files",
                tools=file_search.definitions,
                tool_resources=file_search.resources,
            )
            # [END upload_file_create_vector_store_and_agent_with_file_search_tool]

            print(f"Created agent, ID: {agent.id}")

            # Create thread for communication
            thread = project_client.agents.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create message to thread
            message = project_client.agents.create_message(
                thread_id=thread.id, role="user", content="Hello, what Contoso products do you know?"
            )
            print(f"Created message, ID: {message.id}")

            # Create and process assistant run in thread with tools
            run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            # Get messages from the thread
            messages = project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")

            # Get the last message from the sender
            last_msg = messages.get_last_text_message_by_sender("assistant")
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")
            #last_message = messages[-1]
            #print(f"Last message: {last_message.content}")
            # [START teardown]
            # Delete the file when done
            project_client.agents.delete_vector_store(vector_store.id)
            print("Deleted vector store")

            project_client.agents.delete_file(file_id=file.id)
            print("Deleted file")

            # Delete the agent when done
            project_client.agents.delete_agent(agent.id)
            print("Deleted agent")
            # [END teardown]

            # Fetch and log all messages
            messages = project_client.agents.list_messages(thread_id=thread.id)

            # Print citations from the messages
            for citation in messages.file_citation_annotations:
                print(citation)
        except Exception as e :
            print(f"An error occurred: {e}")
            raise
        finally :
            #span.end();
            print("Program completed")
