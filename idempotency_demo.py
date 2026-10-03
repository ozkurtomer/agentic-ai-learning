from uuid import uuid4

completed_actions = {}

def send_email_demo(action_id, recipient, body):
    payload = {
        "recipient": recipient,
        "body": body
    }

    if action_id in completed_actions:
        previous = completed_actions[action_id]

        if previous["payload"] != payload:
            raise ValueError(
                "Aynı işlem kimliği farklı içerikle kullanılamaz."
            )

        print("Tekrarlanan istek: yeniden gönderilmedi.")
        return previous["result"]

    print(f"[SİMÜLASYON] E-posta gönderildi: {recipient}")

    result = {
        "message_id": uuid4().hex,
        "status": "sent"
    }

    completed_actions[action_id] = {
        "payload": payload,
        "result": result
    }

    return result


action_id = uuid4().hex

first_result = send_email_demo(
    action_id,
    "demo@example.com",
    "Toplantı saat 10.00'da."
)

second_result = send_email_demo(
    action_id,
    "demo@example.com",
    "Toplantı saat 10.00'da."
)

print("\nİlk sonuç:", first_result)
print("İkinci sonuç:", second_result)