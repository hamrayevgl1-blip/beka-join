"""Beka MLBB — kanalga kirish so'rovlarini avtomatik qabul qilish (GitHub Actions uchun).

Har ishga tushganda ~50 soniya so'rovlarni kutadi: kelganlarini qabul qiladi va
qabul qilingan odamga xush kelibsiz xabari yuboradi.
"""
import json
import os
import time

import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
API = f"https://api.telegram.org/bot{TOKEN}/"
WELCOME = os.environ.get("WELCOME_MESSAGE") or (
    "Salom! 👋 <b>Beka MLBB</b> kanaliga xush kelibsiz 🎮\n\n"
    "Har kuni 20:00 da yangi predmet darsi, har 3 kunda meta tahlili 🔥\n\n"
    "💎 Olmosni arzon olish: <a href=\"https://t.me/Bekdonatbot\">@Bekdonatbot</a>")


def call(method, **data):
    r = requests.post(API + method, data=data, timeout=60)
    return r.json()


def main():
    offset, approved, end = None, 0, time.time() + 50
    while time.time() < end:
        params = {"timeout": 20, "allowed_updates": json.dumps(["chat_join_request"])}
        if offset:
            params["offset"] = offset
        res = call("getUpdates", **params)
        if not res.get("ok"):
            print("getUpdates xato:", res.get("description"))
            time.sleep(5)
            continue
        for u in res["result"]:
            offset = u["update_id"] + 1
            req = u.get("chat_join_request")
            if not req or str(req["chat"]["id"]) != str(CHANNEL_ID):
                continue
            user = req["from"]
            r = call("approveChatJoinRequest", chat_id=CHANNEL_ID, user_id=user["id"])
            if r.get("ok"):
                approved += 1
                print("Qabul qilindi:", user.get("first_name", ""), user["id"])
                call("sendMessage", chat_id=req.get("user_chat_id", user["id"]), text=WELCOME,
                     parse_mode="HTML", disable_web_page_preview="true")
            else:
                print("Qabul qilinmadi:", user["id"], r.get("description"))
    if offset:
        call("getUpdates", offset=offset, timeout=0)  # ko'rilganlarni tasdiqlash
    print(f"Jami qabul qilindi: {approved}")


if __name__ == "__main__":
    main()
