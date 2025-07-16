"""
UI System for Daydreamer Project

This package contains the user interface components for the Daydreamer simulation system,
including web dashboard and CLI interfaces.
"""

# Use lazy imports to avoid FastAPI dependency when only CLI is needed
def get_web_dashboard():
    """Lazy import for WebDashboard"""
    from .web_dashboard import WebDashboard
    return WebDashboard

def get_cli_interface():
    """Lazy import for CLIInterface"""
    from .cli_interface import CLIInterface
    return CLIInterface

# For backward compatibility, provide direct access
# but with a warning about potential import issues
def _import_with_warning(module_name):
    """Import with warning about potential dependency issues"""
    import warnings
    warnings.warn(
        f"Direct import of {module_name} may cause dependency issues. "
        "Use get_web_dashboard() or get_cli_interface() for lazy loading.",
        ImportWarning,
        stacklevel=2
    )
    
    if module_name == "WebDashboard":
        return get_web_dashboard()
    elif module_name == "CLIInterface":
        return get_cli_interface()

# Provide access to classes with lazy loading
class WebDashboard:
    """Lazy-loaded WebDashboard class"""
    def __new__(cls, *args, **kwargs):
        return get_web_dashboard()(*args, **kwargs)

class CLIInterface:
    """Lazy-loaded CLIInterface class"""
    def __new__(cls, *args, **kwargs):
        return get_cli_interface()(*args, **kwargs)

__all__ = ['WebDashboard', 'CLIInterface', 'get_web_dashboard', 'get_cli_interface']