#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import random
import time
from instagrapi import Client
from instagrapi.exceptions import (
    RateLimitError, PleaseWaitFewMinutes, ChallengeRequired,
    ClientForbiddenError, LoginRequired,
)

# ======================== HARDCODED ========================
THREAD_ID = "340282366841710301281154066587569992657"

MESSAGE_TEMPLATE = """
Oblivion 𝐒ᴜɴ 𝗟ᴜɴ 𝗖ʜᴜᴍ 𝗔ᴜʀ 𝗗ᴜɴɪʏᴀ 𝗚ʜᴜᴍ ⌈ 💢 ⌋


































Oblivion 𝐒ᴜɴ 𝗟ᴜɴ 𝗖ʜᴜᴍ 𝗔ᴜʀ 𝗗ᴜɴɪʏᴀ 𝗚ʜᴜᴍ ⌈ 💢 ⌋"""

MAX_RETRIES = 10
# =========================================================

CONFIG_FILE = "config.txt"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        sys.exit(f"[!] {CONFIG_FILE} not found — run 'python login.py' first.")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        sys.exit(f"[!] Config load failed: {e} — re-run login.py.")

    if not cfg.get("device_settings"):
        sys.exit("[!] Config missing device_settings — re-run login.py.")
    if not cfg.get("sessionid"):
        sys.exit("[!] Config missing sessionid — re-run login.py.")
    return cfg


def save_settings_back(cfg, cl):
    """Persist refreshed cookies/session back to config."""
    try:
        cfg["device_settings"] = cl.get_settings()
        cfg["sessionid"] = cl.sessionid
        tmp = CONFIG_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp, CONFIG_FILE)
    except Exception as e:
        print(f"⚠️  Config update skipped: {e}")


def make_client(cfg):
    """Restore SAME device from config and verify session."""
    cl = Client()
    try:
        cl.set_settings(cfg["device_settings"])
        print(f"📱 Device restored: {cl.device_settings.get('model', '?')}")
    except Exception as e:
        sys.exit(f"[!] set_settings failed: {e} — re-run login.py.")

    # Verify session with a lightweight call
    try:
        cl.get_timeline_feed()
        print("✅ Session valid (no re-login needed)")
        return cl
    except LoginRequired:
        print("🔄 Session expired — trying login_by_sessionid...")
    except ChallengeRequired:
        sys.exit("[!] Session challenge required — re-run login.py.")
    except Exception as e:
        # network / rate limit — trust session, continue
        print(f"⚠️  Session check warning: {type(e).__name__} — continuing")
        return cl

    # Re-login using sessionid
    try:
        cl.login_by_sessionid(cfg["sessionid"])
        print("✅ Re-login via sessionid OK")
        save_settings_back(cfg, cl)
        return cl
    except Exception as e:
        sys.exit(
            f"[!] Session dead: {type(e).__name__}: {e}\n"
            f"    Run 'python login.py' for a fresh session."
        )


def send_with_retry(client, thread_id, message):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.direct_send(message, thread_ids=[thread_id])
            print(f"✅ Sent: '{message[:60]}...'")
            return True
        except RateLimitError:
            wait = 120 * attempt
            print(f"⚠️ Rate limit – wait {wait}s ({attempt}/{MAX_RETRIES})")
            time.sleep(wait)
        except PleaseWaitFewMinutes:
            print("⏳ Please wait – 600s")
            time.sleep(600)
        except ChallengeRequired:
            print("🔒 Challenge – pausing 1 hour")
            time.sleep(3600)
        except (ClientForbiddenError, LoginRequired):
            sys.exit("[!] Session issue — re-run login.py.")
        except Exception as e:
            wait = 60 * attempt
            print(f"❌ {type(e).__name__}: {e} — wait {wait}s")
            time.sleep(wait)
    print("❌ Max retries — skipping")
    return False


def random_band():
    lo = random.uniform(30, 50)
    spread = random.uniform(8, 13)
    return (lo, lo + spread)


def main():
    cfg = load_config()
    cl = make_client(cfg)

    band = random_band()
    last_band = time.time()
    band_interval = random.uniform(2 * 3600, 3 * 3600)

    last_break = time.time()
    break_interval = random.uniform(3600, 7200)

    msg_count = 0
    print(f"\n🚀 Spam loop started")
    print(f"📨 Thread : {THREAD_ID}")
    print(f"📱 User   : @{cfg['username']}")
    print(f"🎯 Band   : {band[0]:.1f}–{band[1]:.1f}s\n")

    while True:
        try:
            num = random.randint(1, 10**10)
            if random.choice([True, False]):
                msg = f"{num} {MESSAGE_TEMPLATE}"
            else:
                msg = f"{MESSAGE_TEMPLATE} {num}"

            if send_with_retry(cl, THREAD_ID, msg):
                msg_count += 1
                print(f"📊 Total sent: {msg_count}")

            delay = random.uniform(band[0], band[1])
            print(f"⏱️  Wait {delay:.1f}s (band {band[0]:.0f}–{band[1]:.0f})")
            time.sleep(delay)

            # Band rotation
            if time.time() - last_band >= band_interval:
                band = random_band()
                last_band = time.time()
                band_interval = random.uniform(2 * 3600, 3 * 3600)
                print(f"🔄 New band: {band[0]:.1f}–{band[1]:.1f}s")

            # Extra break
            if time.time() - last_break >= break_interval:
                extra = random.uniform(60, 180)
                print(f"☕ Break: {extra:.0f}s")
                time.sleep(extra)
                last_break = time.time()
                break_interval = random.uniform(3600, 7200)

        except KeyboardInterrupt:
            print("🛑 Stopped by user")
            break
        except Exception as e:
            print(f"💥 Crash: {e} — restarting in 60s")
            time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped.")