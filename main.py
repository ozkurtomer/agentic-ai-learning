from google import genai

client = genai.Client()
MODEL = "gemini-3.1-flash-lite"

history = []

while True:
    user_message = input("\nSen: ")

    if user_message.strip().lower() == "çık":
        break

    history.append(f"Kullanıcı: {user_message}")

    conversation = "\n".join(history)

    response = client.interactions.create(
        model=MODEL,
        input=conversation
    )

    assistant_message = response.output_text

    print(f"\nAsistan: {assistant_message}")

    history.append(f"Asistan: {assistant_message}")