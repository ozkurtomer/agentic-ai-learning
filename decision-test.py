def validate_decision(decision):
    if decision["status"] != "ready":
        return False, "İşlem henüz hazır değil."

    if decision["operation"] not in ("add", "multiply", "divide"):
        return False, "Bilinmeyen işlem."

    a = decision.get("a")
    b = decision.get("b")

    if type(a) not in (int, float) or type(b) not in (int, float):
        return False, "İki sayısal değer gerekiyor."

    if decision["operation"] == "divide" and b == 0:
        return False, "Bölen sıfır olamaz."

    return True, "İşlem çalıştırılabilir."


decision = {
    "status": "ready",
    "operation": "divide",
    "a": 20,
    "b": 4
}

is_valid, message = validate_decision(decision)

print("Çalıştırılabilir mi?", is_valid)
print("Açıklama:", message)