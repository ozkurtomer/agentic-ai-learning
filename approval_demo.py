def send_email_demo(to, subject, body):
    print("\n[SİMÜLASYON] Gönderim aracı çalıştı.")
    print("Alıcı:", to)
    print("Konu:", subject)
    print("Mesaj:", body)


state = {
    "status": "waiting_for_approval",
    "revision": 1,
    "approved_revision": None,
    "pending_action": {
        "to": "demo@example.com",
        "subject": "Toplantı",
        "body": "Yarın saat 10.00 uygun mu?"
    }
}

while True:
    action = state["pending_action"]

    print(f"\nTaslak sürümü: {state['revision']}")
    print("Alıcı:", action["to"])
    print("Konu:", action["subject"])
    print("Mesaj:", action["body"])
    print("Durum:", state["status"])

    command = input(
        "\nKomut: onayla / alıcı değiştir / gönder / iptal: "
    ).strip().lower()

    if command == "iptal":
        state["status"] = "cancelled"
        break

    elif command == "alıcı değiştir":
        new_recipient = input("Yeni alıcı: ").strip()

        if not new_recipient:
            print("Alıcı boş olamaz.")
            continue

        action["to"] = new_recipient

        state["revision"] += 1
        state["approved_revision"] = None
        state["status"] = "waiting_for_approval"

    elif command == "onayla":
        state["approved_revision"] = state["revision"]
        state["status"] = "approved"
        print("Gösterilen taslak onaylandı.")

    elif command == "gönder":
        if state["approved_revision"] != state["revision"]:
            print("Bu taslak sürümü onaylı değil. Önce onayla.")
            continue

        send_email_demo(**action)
        state["status"] = "completed"
        break

    else:
        print("Bilinmeyen komut.")