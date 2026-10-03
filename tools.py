def multiply(a: float, b: float) -> float:
    """İki sayıyı çarpar ve sonucu döndürür."""
    return a * b

def add(a: float, b: float) -> float:
    """İki sayıyı toplar ve sonucu döndürür."""
    return a + b

def divide(a: float, b: float) -> float:
    """İlk sayıyı ikinci sayıya böler."""
    if b == 0:
        raise ValueError("Bölen sıfır olamaz.")

    return a / b

def subtract(a: float, b: float) -> float:
    """İlk sayıdan ikinci sayıyı çıkartır."""
    return a - b