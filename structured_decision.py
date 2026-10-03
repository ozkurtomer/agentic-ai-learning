import json
from typing import Literal, Optional

from google import genai
from pydantic import BaseModel, ConfigDict, ValidationError

from tools import add, multiply, divide

from state_store import load_state, save_state

class Decision(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    status: Literal["ready", "waiting_for_user"]
    message: str
    operation: Literal["add", "multiply", "divide"]
    a: Optional[float]
    b: Optional[float]


def validate_decision(decision):
    
    if decision.a is None:
        return False, "İlk sayı kaç olsun?"

    if decision.b is None:
        return False, "İkinci sayı kaç olsun?"

    if decision.operation == "divide" and decision.b == 0:
        return False, "Bölen sıfır olamaz. Hangi böleni kullanayım?"

    if decision.status != "ready":
        return False, decision.message

    return True, "İşlem çalıştırılabilir."


client = genai.Client()
MODEL = "gemini-3.1-flash-lite"

tool_registry = {
    "add": add,
    "multiply": multiply,
    "divide": divide
}

state = load_state()
print("[Yüklenen state]")
print(json.dumps(state, ensure_ascii=False, indent=2))

instructions = (
    "Tek bir aritmetik işlem isteğini yapılandır. Hesaplama yapma. "
    "Sana mevcut görev ve kullanıcının yeni mesajı verilecek. "
    "Yeni mesaj bekleyen görevi tamamlıyorsa mevcut bilgileri koru "
    "ve yalnızca kullanıcının belirttiği değerleri güncelle. "
    "Kullanıcı açıkça yeni işlem istiyorsa yeni işlemi esas al. "
    "Eksik sayıları uydurma, null bırak. "
    "Mesaj belirsizse waiting_for_user durumuyla açıklama iste. "
    "Sayı eksikse veya bölen sıfırsa waiting_for_user kullan. "
    "Değerler tam ve geçerliyse ready kullan. "
    "message alanını Türkçe yaz."
)

while True:
    user_message = input("\nSen: ").strip()

    if user_message.lower() == "çık":
        break

    if not user_message:
        continue

    if user_message.lower() == "iptal":
        state["status"] = "idle"
        state["pending_task"] = None

        save_state(state)

        print("Bekleyen işlem iptal edildi.")
        continue

    context = {
        "current_task": state["pending_task"],
        "user_message": user_message
    }

    response = client.interactions.create(
        model=MODEL,
        input=(
            instructions
            + "\n\n"
            + json.dumps(context, ensure_ascii=False)
        ),
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Decision.model_json_schema()
        }
    )

    try:
        decision = Decision.model_validate_json(
            response.output_text or ""
        )
    except ValidationError:
        print("Modelin yanıtı doğrulanamadı. Görev değiştirilmedi.")
        continue

    print("\n[Modelin kararı]")
    print(decision.model_dump_json(indent=2))

    can_execute, message = validate_decision(decision)

    if not can_execute:
        state["status"] = "waiting_for_user"
        state["pending_task"] = {
            "operation": decision.operation,
            "a": decision.a,
            "b": decision.b,
            "question": message
        }

        print("\nAsistan:", message)

    else:
        selected_tool = tool_registry[decision.operation]

        result = selected_tool(
            a=decision.a,
            b=decision.b
        )

        print("\nPython sonucu:", result)

        save_state(state)

        print("\n[State]")
        print(json.dumps(state, ensure_ascii=False, indent=2))

        state["status"] = "completed"
        state["pending_task"] = None

    print("\n[State]")
    print(json.dumps(state, ensure_ascii=False, indent=2))