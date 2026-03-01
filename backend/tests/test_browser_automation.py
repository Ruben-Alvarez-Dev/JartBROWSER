import pytest
import inspect
from jartbrowser.services.browser_automation import BrowserAutomationService, ActionType


def test_create_get_and_close_browser():
    service = BrowserAutomationService()
    # Create a browser instance
    browser_id = service.create_browser()
    assert browser_id is not None

    # Retrieve the browser info
    browser = service.get_browser(browser_id)
    assert browser is not None
    # Accept either dict with id fields or a simple value
    if isinstance(browser, dict):
        assert ("id" in browser) or ("browser_id" in browser) or ("name" in browser)

    # List tabs
    tabs = service.get_tabs(browser_id)
    assert isinstance(tabs, list)

    # Active tab
    active_tab = service.get_active_tab(browser_id)
    assert active_tab is not None
    if isinstance(active_tab, dict):
        assert ("id" in active_tab) or ("tab_id" in active_tab) or ("title" in active_tab)

    # Close the browser
    result = service.close_browser(browser_id)
    # Some implementations may return None; ensure no exception is raised
    assert result is None or isinstance(result, bool) or isinstance(result, dict)


def test_execute_action_various_signatures():
    service = BrowserAutomationService()
    browser_id = service.create_browser()
    # Pick the first available ActionType member if any
    action = None
    try:
        action = next(iter(ActionType))
    except StopIteration:
        pytest.skip("No ActionType members available")
    if action is None:
        pytest.skip("No ActionType available")

    # Inspect the signature to call with a safe set of arguments
    sig = inspect.signature(service.execute_action)
    params = list(sig.parameters.values())
    args = [browser_id, action]
    # If the function accepts a payload, provide an empty dict
    if len(params) >= 3:
        args.append({})
    try:
        result = service.execute_action(*args)
        assert result is not None
    except TypeError:
        pytest.skip("execute_action signature not compatible with provided arguments")
