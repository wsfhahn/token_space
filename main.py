from dotenv import load_dotenv
from os import getenv
from openai import OpenAI

from src import build_token_graph, export_sigma_force_graph_html, save_graph_json


def main() -> None:
    load_dotenv()

    BASE_URL = getenv("BASE_URL")
    API_KEY = getenv("API_KEY")
    MODEL_NAME = getenv("MODEL_NAME")
    DEPTH_STR = getenv("GRAPH_DEPTH")
    COMPLETIONS_PER_NODE_STR = getenv("COMPLETIONS_PER_NODE")
    MAX_RETRIES_STR = getenv("MAX_RETRIES")

    if not BASE_URL:
        raise ValueError("BASE_URL is not set in your env. Please set BASE_URL to your API provider's base URL.")
    if not API_KEY:
        raise ValueError("API_KEY is not set in your env. Please set your API key for your provider in your env.")
    if not MODEL_NAME:
        raise ValueError("MODEL_NAME is not set in your env. Please set the model name.")
    if not DEPTH_STR:
        raise ValueError("GRAPH_DEPTH is not set in your env. Please set your graph depth.")
    if not COMPLETIONS_PER_NODE_STR:
        raise ValueError("COMPLETIONS_PER_NODE is not set in your env. Please set your completions per node.")
    if not MAX_RETRIES_STR:
        raise ValueError("MAX_RETRIES is not set in your env. Please set your max retries.")
    
    try:
        DEPTH = int(DEPTH_STR)
        COMPLETIONS_PER_NODE = int(COMPLETIONS_PER_NODE_STR)
        MAX_RETRIES = int(MAX_RETRIES_STR)
    except Exception as e:
        raise Exception(f"Failed to case env vars to int: {e}") from e
    
    base_node: str = input("Enter base node string (default: \"There once was a\"): ")
    if not base_node:
        base_node = "There once was a"

    save_output_json_str: str = input("Y/n: Save your completions as JSON? ")
    save_output_json = True if save_output_json_str == "Y" else False

    if save_output_json:
        json_output_path: str = input("Please enter the path to save completions: ")
    
    use_wordseg_str = input("Y/n: Use word segmentation? (set N if unsure): ")
    use_wordseg: bool = True if use_wordseg_str == "Y" else False

    html_output_path: str = input("Enter the path to save your visualization (must end in .html): ")

    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    try:
        root = build_token_graph(
            client,
            MODEL_NAME,
            DEPTH,
            COMPLETIONS_PER_NODE,
            MAX_RETRIES,
            base_node,
            use_wordseg
        )
    except Exception as e:
        raise Exception(f"Failed to create graph: {e}") from e
    
    if save_output_json:
        save_graph_json(root, json_output_path)
    
    export_sigma_force_graph_html(root, html_output_path)

    print("Done!")

if __name__ == "__main__":
    main()