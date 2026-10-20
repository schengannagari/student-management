def __init__():
    print("This is a test module.")

def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    name = input("Enter your name: ")
    print(greet(name))