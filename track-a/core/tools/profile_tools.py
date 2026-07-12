"""
LangChain tools for User Profile & Settings.

Wraps db user_profile functions into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_user_profile(key: str = "") -> str:
    """Get the user's profile information. Use this when the user wants to see their name, email, or other profile data.

    Args:
        key: Specific profile key to retrieve (e.g., "user_name", "user_email"). Leave empty to get all profile data.
    """
    try:
        from db import get_profile

        if key:
            value = get_profile(key)
            logger.info("Profile lookup: %s = %s", key, value)
            return json.dumps({
                "success": True,
                "key": key,
                "value": value
            })

        keys = ["user_name", "user_email", "daily_focus_goal"]
        profile = {}
        for k in keys:
            v = get_profile(k)
            if v is not None:
                profile[k] = v

        logger.info("Profile retrieved: %d fields", len(profile))
        return json.dumps({"success": True, "profile": profile})
    except Exception as e:
        logger.error("get_user_profile failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_user_profile(key: str, value: str) -> str:
    """Update the user's profile information. Use this when the user wants to change their name, email, or other settings.

    Args:
        key: Profile key to update (e.g., "user_name", "user_email").
        value: New value to set.
    """
    try:
        from db import set_profile

        if not key:
            return json.dumps({"success": False, "error": "Profile key is required."})

        set_profile(key, value)
        logger.info("Profile updated: %s = %s", key, value)

        return json.dumps({
            "success": True,
            "message": f"Profile field '{key}' updated to '{value}'.",
            "key": key,
            "value": value
        })
    except Exception as e:
        logger.error("update_user_profile failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


PROFILE_TOOLS = [get_user_profile, update_user_profile]
