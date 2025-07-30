try:
    from aiogram import F
    print("Successfully imported F from aiogram")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")