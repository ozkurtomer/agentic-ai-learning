import json

from tools import multiply, add, divide
from google import genai

tool_registry = {
    "multiply": multiply,
    "add": add,
    "divide": divide
}

client = genai.Client()
MODEL = "gemini-3.1-flash-lite"

multiply_tool = {
    "type": "function",
    "name": "multiply",
    "description": "İki sayıyı çarpar.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "Çarpılacak ilk sayı."
            },
            "b": {
                "type": "number",
                "description": "Çarpılacak ikinci sayı."
            }
        },
        "required": ["a", "b"]
    }
}

add_tool = {
    "type": "function",
    "name": "add",
    "description": "İki sayıyı toplar.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
}

divide_tool = {
    "type": "function",
    "name": "divide",
    "description": "a sayısını b sayısına böler. b sıfır olamaz.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
}

response = client.interactions.create(
    model=MODEL,
    input="12 ve 8 sayılarını uygun hesaplama aracını kullanarak çarp",
    tools=[multiply_tool, add_tool]
)

available_tools = [multiply_tool, add_tool, divide_tool]

next_input = (
    "20'yi 0'e divide aracını kullanarak böl"
)

previous_id = None

MAX_MODEL_CALLS = 5

for turn in range(MAX_MODEL_CALLS):
    print(f"\n--- Model çağrısı {turn + 1} ---")

    request = {
        "model": MODEL,
        "input": next_input,
        "tools": available_tools
    }

    if previous_id is not None:
        request["previous_interaction_id"] = previous_id

    response = client.interactions.create(**request)

    previous_id = response.id
    function_results = []

    for step in response.steps:
        if step.type != "function_call":
            continue

        print("İstenen araç:", step.name)
        print("Parametreler:", step.arguments)

        if step.name not in tool_registry:
            raise ValueError(f"Bilinmeyen araç: {step.name}")

        arguments = step.arguments

        if set(arguments) != {"a", "b"}:
            raise ValueError("Araç tam olarak a ve b bekliyor.")

        a = arguments["a"]
        b = arguments["b"]

        if type(a) not in (int, float) or type(b) not in (int, float):
            raise ValueError("a ve b sayısal olmalı.")

        selected_tool = tool_registry[step.name]
        try:
            result = selected_tool(a=a, b=b)

            tool_result = {
                "ok": True,
                "value": result
            }

        except ValueError as error:
            tool_result = {
                "ok": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": str(error),
                    "retryable": False
                }
            }

        print("Araç sonucu:", tool_result)

        function_results.append({
            "type": "function_result",
            "name": step.name,
            "call_id": step.id,
            "result": [
                {
                    "type": "text",
                    "text": json.dumps(tool_result, ensure_ascii=False)
                }
            ]
        })

    if function_results:
        next_input = function_results
    else:
        if response.output_text:
            print("\nSon yanıt:", response.output_text)
        else:
            print("\nMetin veya araç isteği gelmedi; duruldu.")

        break

else:
    print("\nModel çağrısı sınırına ulaşıldı; görev tamamlanmamış olabilir.")