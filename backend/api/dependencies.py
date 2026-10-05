from fastapi import Header, HTTPException


def editor(x_workspace_role: str = Header(default='officer')):
    """Local demonstration persona guard; replace with real identity before deployment."""
    if x_workspace_role not in ('officer', 'analyst'):
        raise HTTPException(403, 'Viewer persona is read-only. Choose an editor persona in this local prototype.')
    return x_workspace_role
