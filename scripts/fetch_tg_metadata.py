import os
import json
import requests
import argparse
from datetime import datetime
from pathlib import Path

def fetch_chat_metadata(bot_token: str, chat_id: str, output_dir: str):
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    metadata = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "chat_id": chat_id,
        "member_count": 0,
        "admins": []
    }

    print(f"Fetching member count for {chat_id}...")
    count_resp = requests.get(f"{base_url}/getChatMemberCount", params={"chat_id": chat_id})
    if count_resp.status_code == 200 and count_resp.json().get("ok"):
        metadata["member_count"] = count_resp.json().get("result", 0)
    else:
        print(f"Failed to fetch member count: {count_resp.text}")

    print(f"Fetching administrators for {chat_id}...")
    admins_resp = requests.get(f"{base_url}/getChatAdministrators", params={"chat_id": chat_id})
    if admins_resp.status_code == 200 and admins_resp.json().get("ok"):
        admins = admins_resp.json().get("result", [])
        for admin in admins:
            user = admin.get("user", {})
            status = admin.get("status") # 'creator' or 'administrator'
            custom_title = admin.get("custom_title", "")
            
            admin_info = {
                "id": user.get("id"),
                "is_bot": user.get("is_bot", False),
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "username": user.get("username", ""),
                "role": status,
                "custom_title": custom_title,
                "permissions": {
                    "can_manage_chat": admin.get("can_manage_chat", False),
                    "can_delete_messages": admin.get("can_delete_messages", False),
                    "can_manage_video_chats": admin.get("can_manage_video_chats", False),
                    "can_restrict_members": admin.get("can_restrict_members", False),
                    "can_promote_members": admin.get("can_promote_members", False),
                    "can_change_info": admin.get("can_change_info", False),
                    "can_invite_users": admin.get("can_invite_users", False),
                    "can_post_messages": admin.get("can_post_messages", False),
                    "can_edit_messages": admin.get("can_edit_messages", False),
                    "can_pin_messages": admin.get("can_pin_messages", False),
                    "can_manage_topics": admin.get("can_manage_topics", False),
                }
            }
            metadata["admins"].append(admin_info)
    else:
        print(f"Failed to fetch administrators: {admins_resp.text}")

    # Ensure output directory exists
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    file_path = out_path / "metadata.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print(f"Metadata saved successfully to {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Telegram Chat Metadata (Admins, Member Count)")
    parser.add_argument("--token", required=True, help="Telegram Bot Token")
    parser.add_argument("--chat", required=True, help="Target Chat ID (e.g., -1001234567890 or @channelname)")
    parser.add_argument("--output", default=".garden/bronze/metadata", help="Output directory")
    
    args = parser.parse_args()
    fetch_chat_metadata(args.token, args.chat, args.output)
