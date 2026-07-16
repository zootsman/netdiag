import questionary
from .core import run
from .plugin_manager import PluginManager # Import PluginManager

async def show_menu():
    """
    Displays an interactive menu for the user to select which network checks to run.
    """
    # Create a dummy PluginManager to discover plugins for menu display
    dummy_plugin_manager = PluginManager(None, None, None) # Pass None for console, config, report_data
    dummy_plugin_manager.discover_plugins()
    AVAILABLE_CHECKS_INFO = dummy_plugin_manager.get_available_checks_info()

    # Create a mapping from description to the check's key
    desc_to_key = {"Все проверки": "all"}
    desc_to_key.update({info["desc"]: key for key, info in AVAILABLE_CHECKS_INFO.items()})

    # Get the list of descriptions to show the user
    descriptions = list(desc_to_key.keys())
    
    selected_desc = await questionary.select(
        "Выберите проверку для запуска (enter для подтверждения):",
        choices=descriptions
    ).ask_async()

    if not selected_desc:
        print("Не выбрано ни одной проверки. Выход.")
        return

    # Map the selected description back to its key
    selected_key = desc_to_key.get(selected_desc)

    if selected_key == "all":
        await run()
    else:
        await run(checks_to_run=[selected_key])
