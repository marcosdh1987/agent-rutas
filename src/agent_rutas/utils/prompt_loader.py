import importlib
import logging


def load_prompt(chain_name: str, model_core: str, agent_name: str) -> str:
    """
    Load the prompt for a given chain name and model core.

    Args:
        chain_name (str): The name of the chain.
        model_core (str): The core model to use.

    Returns:
        str: The loaded prompt.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the prompt attribute cannot be found in the module.
    """
    # Build the model name from the chain name and the model core
    module_name = f"prompts.{chain_name}.{model_core}"
    try:
        # Dynamically import the module
        module = importlib.import_module(module_name)
        logging.info("Loaded prompt: %s", module_name)
        # Get the prompt attribute from the module
        return getattr(module, f"{chain_name.upper()}_PROMPT")
    except (ModuleNotFoundError, AttributeError) as e:
        logging.info("Error loading prompt: %s", module_name)
        logging.info("Attempting to load default prompt (default)")
        # Get the prompt attribute from the module
        try:
            default_module_name = f"prompts.{chain_name}.default"
            module = importlib.import_module(default_module_name)
            logging.info("Loaded default prompt: %s", default_module_name)
            return getattr(module, f"{chain_name.upper()}_PROMPT")
        except (ModuleNotFoundError, AttributeError) as e:
            logging.critical("Error loading default prompt: %s", e)
            # Fallback: try loading from agent_<suffix>.prompts
            try:
                # use agent name as suffix
                pkg = agent_name.split("_")[1]
                # Load the agent-specific default prompt
                fallback_module = f"agent_{pkg}.prompts.{chain_name}.default"
                module = importlib.import_module(fallback_module)
                logging.info("Loaded agent-specific default prompt: %s", fallback_module)
                return getattr(module, f"{chain_name.upper()}_PROMPT")
            except (ModuleNotFoundError, AttributeError) as e2:
                logging.critical("Error loading agent-specific default prompt: %s", e2)
                raise RuntimeError("Critical error: Unable to load any prompt")
