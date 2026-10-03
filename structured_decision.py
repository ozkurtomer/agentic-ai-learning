import json
from typing import Literal, Optional

from google import genai
from pydantic import BaseModel, ConfigDict, ValidationError

from tools import add, multiply, divide, subtract
from state_store import load_state, save_state

class Decision(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    status: Literal["ready", "waiting_for_user", "unsupported"]
    message: str

    operation: Optional[
        Literal["add", "multiply", "divide", "subtract"]
    ]

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
    "divide": divide,
    "subtract": subtract
}

conversation_id = input("Sohbet kimliği: ").strip()
state = load_state(conversation_id)

print("\n[Yüklenen state]")
print(json.dumps(state, ensure_ascii=False, indent=2))

instructions = (
    "Kullanıcının YENİ mesajını değerlendir ve tek bir aritmetik "
    "işlem için yapılandırılmış karar üret. Hesaplama yapma. "

    "Desteklenen işlemler: add (a+b), subtract (a-b), "
    "multiply (a*b), divide (a/b). "

    "Önce yeni mesajın mevcut göreve bilgi sağlayıp sağlamadığını "
    "veya desteklenen yeni bir işlem isteyip istemediğini belirle. "

    "Yeni mesaj yalnızca selamlaşma, teşekkür veya konu dışı "
    "içerikse, bekleyen görev olsa bile status unsupported olsun. "
    "Bu durumda operation, a ve b null olsun. "
    "message alanında kısa ve uygun bir Türkçe yanıt ver. "

    "Örnek: Bekleyen görev subtract, a=30, b=null iken "
    "'merhaba' mesajı gelirse unsupported döndür. "
    "Aynı görevde '12 olsun' mesajı gelirse "
    "ready, operation=subtract, a=30, b=12 döndür. "
    "'Merhaba, 12 olsun' mesajı ise görevle ilgili bilgi içerir; "
    "yalnızca selamlaşma olarak değerlendirme. "

    "Yeni mesaj bekleyen görevi tamamlıyorsa bilinen değerleri koru "
    "ve yalnızca kullanıcının belirttiği değerleri güncelle. "
    "Kullanıcı açıkça desteklenen yeni bir işlem istiyorsa "
    "yeni işlemi esas al. "

    "Eksik sayıları uydurma, null bırak. "
    "Görevle ilgili mesaj belirsizse waiting_for_user ile "
    "açıklama iste. "
    "Sayı eksikse veya bölen sıfırsa waiting_for_user kullan. "
    "Gerekli değerler tam ve geçerliyse ready kullan. "

    "Çıkarma ve bölmede sayı sırasına dikkat et. "
    "'30'dan 12 çıkar' için a=30, b=12 olmalı. "
    "message alanını Türkçe yaz."
)

while True:
    user_message = input("\nSen: ").strip()

    if user_message.lower() == "çık":
        print("Program kapatıldı.")
        break

    if not user_message:
        continue

    if user_message.lower() == "iptal":
        state["status"] = "idle"
        state["pending_task"] = None

        save_state(conversation_id, state)

        print("Bekleyen işlem iptal edildi.")
        print("\n[State]")
        print(json.dumps(state, ensure_ascii=False, indent=2))
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

    if decision.status == "unsupported":
        print("\nAsistan:", decision.message)
        continue

    if decision.operation is None:
        print("\nGeçerli bir işlem seçilmedi. Görev değiştirilmedi.")
        continue

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

        state["status"] = "completed"
        state["pending_task"] = None

    save_state(conversation_id, state)

    print("\n[State]")
    print(json.dumps(state, ensure_ascii=False, indent=2))