#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, subprocess, importlib, getpass, json, os
from datetime import datetime

def ensure(pkg, name=None):
    name = name or pkg
    try:
        importlib.import_module(name)
    except ImportError:
        print(f"📦 Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

ensure("instagrapi")

from instagrapi import Client
from instagrapi.exceptions import (
    TwoFactorRequired, ChallengeRequired, BadPassword,
    UserNotFound, RateLimitError, LoginRequired,
)

CONFIG_FILE = "config.txt"


def challenge_handler(username, choice):
    print(f"\n🔐 Instagram verification for @{username}")
    print(f"   Method: {choice}")
    return input("   Enter code: ").strip()


def save_config(cfg):
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, CONFIG_FILE)


def do_login():
    print("🔐 Instagram Login (Password + 2FA)")
    print("=" * 55)

    username = input("📧 Username: ").strip()
    if not username:
        sys.exit("[!] Username required.")

    password = getpass.getpass("🔑 Password (hidden): ").strip()
    if not password:
        sys.exit("[!] Password required.")

    cl = Client()
    cl.challenge_code_handler = challenge_handler

    print(f"\n[*] Logging in as @{username}...")

    try:
        cl.login(username, password)
        print("✅ LOGIN SUCCESS")

    except TwoFactorRequired:
        print("\n🔐 2FA CODE REQUIRED")
        code = input("Enter 2FA code: ").strip()
        if not code:
            sys.exit("[!] 2FA code required.")
        try:
            cl.login(username, password, verification_code=code)
            print("✅ LOGIN SUCCESS (2FA)")
        except Exception as e:
            sys.exit(f"\n❌ 2FA failed: {type(e).__name__}: {e}")

    except BadPassword:
        sys.exit("\n❌ Wrong password.")

    except UserNotFound:
        sys.exit("\n❌ Username not found.")

    except ChallengeRequired as e:
        sys.exit(f"\n❌ Challenge required — clear it on phone first.\n{e}")

    except RateLimitError:
        sys.exit("\n⏳ Rate limited. Try again later.")

    except Exception as e:
        sys.exit(f"\n❌ Login failed: {type(e).__name__}: {e}")

    return cl


def main():
    cl = do_login()

    settings = cl.get_settings()

    cfg = {
        "username": cl.username,
        "user_id": cl.user_id,
        "sessionid": cl.sessionid,
        "device_settings": settings,
        "saved_at": datetime.now().isoformat(),
    }

    save_config(cfg)
    print(f"\n💾 Saved → {CONFIG_FILE}")
    print(f"   Username : @{cl.username}")
    print(f"   User ID  : {cl.user_id}")
    print(f"   Device   : {settings['device_settings'].get('model', '?')} "
          f"({settings['device_settings'].get('manufacturer', '?')})")
    print(f"   Session  : {cl.sessionid[:50]}...")

    print("\n▶️  Launching single.py...\n")
    try:
        subprocess.run([sys.executable, "single.py"])
    except FileNotFoundError:
        print("❌ single.py not found in current directory.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped.")