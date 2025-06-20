import random
import time
import csv
import os
import re
import threading
import sys
import textwrap
import platform
import ast
import glob
import shutil
import select
from datetime import datetime
from fuzzywuzzy import fuzz
from pathlib import Path
from colorama import init, Fore, Style
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def educational_chat_csv():
    file_path = r"F:\Folder of codes\csv\extended_math_questions_answers.csv"
    questions = []
    answers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            next(reader)  
            for row in reader:
                if len(row) >= 2:  
                    questions.append(row[0])
                    answers.append(row[1])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    if not questions or len(questions) != len(answers):
        print("Error: Questions and answers lists are empty or have different lengths.")
        return
    def get_input_with_timeout(prompt, timeout):
        user_input = [None]
        def input_thread():
            try:
                user_input[0] = input(prompt)
            except:
                user_input[0] = ""
        thread = threading.Thread(target=input_thread)
        thread.daemon = True
        thread.start()
        start_time = time.time()
        time_limit = timeout
        while thread.is_alive() and (time.time() - start_time) < time_limit:
            remaining = int(time_limit - (time.time() - start_time))
            sys.stdout.write(f"\rTime left: {remaining} sec [{'=' * (remaining // 2)}{' ' * ((time_limit // 2) - (remaining // 2))}]")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        if thread.is_alive():
            return None
        return user_input[0]

    try:
        n = int(input(f"Number of questions (1-{len(questions)}): "))
        if not 1 <= n <= len(questions):
            print(f"Choose a number between 1 and {len(questions)}")
            return
        score = 0
        indices = random.sample(range(len(questions)), n)
        time_limit = 30

        print("\n🎯 Math Quiz Started! Answer each question within 30 seconds. 🚀")
        print("A countdown timer will show your remaining time. Let's go! 🔥\n")

        for i, idx in enumerate(indices, 1):
            print(f"Question {i}/{n}: {questions[idx]}")
            ans = get_input_with_timeout("Answer: ", time_limit)
            if ans is None:
                print(f"\nTime's up! ⏰ Correct answer: {answers[idx]} ❌")
            elif ans.strip() == answers[idx].strip():  
                print("\nCorrect! ✔")
                score += 1
            else:
                print(f"\nWrong! ❌ Correct answer: {answers[idx]}")
            print() 

        print(f"🏁 Quiz Complete! Your Score: {score}/{n} 🎉")
        percentage = (score / n) * 100
        print(f"Percentage: {percentage:.2f}%")
        if percentage == 100:
            print("Perfect score! You're a math wizard! 🧙‍♂️")
        elif percentage >= 70:
            print("Great job! Keep practicing! 💪")
        else:
            print("Nice try! Review and try again! 📚")

    except ValueError:
        print("Error: Please enter a valid number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
init()

# Define base directory
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

chat_history = []
used_jokes = set()
used_quotes = set()

jokes = [
    "Why did the computer go to art school? It wanted to draw a better 'byte'!",
    "Why don’t coders sleep? Too busy debugging dreams!",
    "Why did Python go to therapy? Too many indentation issues!",
    "Why was the math book sad? It had too many problems!",
    "Why did the scarecrow become a coder? He was outstanding in his field!"
]

quotes = [
    "The future belongs to those who believe in their dreams.",
    "Every line of code you write is a step forward.",
    "Wake up with determination, sleep with satisfaction.",
    "Code is like humor: when you have to explain it, it’s bad.",
    "Success is not a destination, it’s a journey."
]
def normalize(text):
    """Normalize text by converting to lowercase, removing punctuation, and spaces."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text.replace(" ", "")

def detect_sentiment(text):
    """Detect sentiment based on keywords in the input text."""
    positive_words = ["happy", "great", "awesome", "good"]
    negative_words = ["sad", "bored", "tired", "bad"]
    text = text.lower()
    if any(word in text for word in positive_words):
        return "positive"
    elif any(word in text for word in negative_words):
        return "negative"
    return "neutral"

def get_time_based_greeting():
    """Return a time-based greeting based on the current hour."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning! Hope your day's off to a great start! ☀️"
    elif 12 <= hour < 17:
        return "Good Afternoon! What's up? 😎"
    elif 17 <= hour < 22:
        return "Good Evening! Ready to chat? 🌆"
    else:
        return "Good Night! Sweet dreams! 🌙"

def chat_saver(timestamp, user_name, messages):
    filename = "chat_history.csv"  # Use relative path or ensure directory exists
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
        with open(filename, "a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Timestamp", "User", "Speaker", "Message"])
            for line in messages:
                if ": " in line:  # Ensure valid message format
                    speaker, message = line.split(": ", 1)
                    writer.writerow([timestamp, user_name, speaker, message])
                else:
                    print(f"Warning: Skipping malformed message: {line}")
    except PermissionError:
        print(f"Error: No permission to write to {filename}")
    except FileNotFoundError:
        print(f"Error: Directory for {filename} not found")
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_qa_data(file_path):
    """Load question-answer pairs and commands from a CSV file."""
    qa_data = {}
    app_commands = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            next(reader)  
            for row in reader:
                if len(row) >= 2:  
                    question = normalize(row[0].lower())
                    answer = row[1]
                    if answer.endswith('.exe') or answer.startswith('start '):
                        app_commands[question] = [answer]
                    else:
                        if answer == "keyword_responses[\"joke\"]":
                            qa_data[question] = "joke"
                        elif answer == "keyword_responses[\"quote\"]":
                            qa_data[question] = "quote"
                        else:
                            answers = [ans.strip() for ans in answer.split('|') if ans.strip()]
                            qa_data[question] = answers if len(answers) > 1 else answers[0] if answers else answer
        return qa_data, app_commands
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}, {}
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return {}, {}

def find_best_match(question, qa_data, threshold=80):
    """Find the best matching question using fuzzy matching."""
    norm_input = normalize(question)
    best_match = None
    highest_score = 0

    for qa_question in qa_data:
        score = fuzz.ratio(norm_input, qa_question)
        if score > highest_score and score >= threshold:
            highest_score = score
            best_match = qa_question

    return best_match

def get_joke():
    """Return a random joke, ensuring no repeats until all are used."""
    global used_jokes
    available_jokes = [j for j in jokes if j not in used_jokes]
    if not available_jokes:
        used_jokes.clear() 
        available_jokes = jokes
    joke = random.choice(available_jokes)
    used_jokes.add(joke)
    return joke

def get_quote():
    """Return a random quote, ensuring no repeats until all are used."""
    global used_quotes
    available_quotes = [q for q in quotes if q not in used_quotes]
    if not available_quotes:
        used_quotes.clear()  
        available_quotes = quotes
    quote = random.choice(available_quotes)
    used_quotes.add(quote)
    return quote

def process_answer(answer):
    """Process the answer, handling special cases like get_time_based_greeting, jokes, and quotes."""
    if answer == "get_time_based_greeting":
        return get_time_based_greeting()
    elif answer == "joke":
        return get_joke()
    elif answer == "quote":
        return get_quote()
    elif isinstance(answer, list):
        processed_answers = [process_answer(a) if a in ["get_time_based_greeting", "joke", "quote"] else a for a in answer]
        return random.choice(processed_answers)
    return answer
def welcome_animation():
    frames = [
        "🌟 Initializing ChatBuddy...",
        "🌟 Loading AI Smarts...   ",
        "🌟 Ready to Chat!         "
    ]
    for frame in frames:
        clear_screen()
        print(f"{Fore.CYAN}{frame.center(50)}{Style.RESET_ALL}")
        time.sleep(0.5)

def display_chat_history():
    if not chat_history:
        return
    print(f"{Fore.CYAN}┌{'─' * 48}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{'Recent Chat History'.center(48)}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}├{'─' * 48}┤{Style.RESET_ALL}")
    for msg in chat_history[-3:]:
        if msg.startswith("You:"):
            print(f"{Fore.GREEN}│ {msg[:46]:<46} │{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}│ {msg[:46]:<46} │{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 48}┘{Style.RESET_ALL}")

def chat_interaction(name="User"):
    qa_data, app_commands = load_qa_data("F:\Folder of codes\csv\qa_data.csv")
    if not qa_data and not app_commands:
        print(f"{Fore.RED}No data loaded. Exiting.{Style.RESET_ALL}")
        return

    welcome_animation()
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'Welcome to ChatBuddy!'.center(50)}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'Type "exit" to quit, "help" for commands, "clear" to reset history.'.center(50)}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Bot: {get_time_based_greeting()}{Style.RESET_ALL}\n")

    global chat_history
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n🕒 {current_time} | 👤 {name}")
        display_chat_history()
        print("-" * 52)
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
        norm_input = normalize(user_input)
        chat_history.append(f"You: {user_input}")
        if len(chat_history) > 20:
            chat_history.pop(0)

        if norm_input == "exit":
            response = "Chat ended. 😺 Come back soon!"
        elif norm_input == "help":
            response = "Commands: 'exit' to quit, 'clear' to reset history, 'joke' for a joke, 'quote' for a quote, 'game' to play a quiz."
        elif norm_input == "clear":
            chat_history.clear()
            response = "Chat history cleared! Start fresh! ✨"
            clear_screen()
        elif norm_input in app_commands:
            for cmd in app_commands[norm_input]:
                try:
                    os.system(cmd)
                except Exception as e:
                    response = f"Error executing command '{cmd}': {e}"
            response = f"✅ Launching: {user_input}"
        elif norm_input in qa_data:
            response = process_answer(qa_data[norm_input])
        else:
            best_match = find_best_match(user_input, qa_data)
            if best_match:
                matched = f"Matched: {best_match}. Response: {process_answer(qa_data[best_match])}"
                response = matched
            else:
                sentiment = detect_sentiment(user_input)
                if sentiment == "positive":
                    response = "Love the positivity! What's up? 😄"
                elif sentiment == "negative":
                    response = "Sorry you're down. Want a joke? 😺"
                else:
                    response = "Didn't get that. Try a joke, quote, or game! 😺"

        chat_history.append(f"Bot: {response}")
        for line in textwrap.wrap(f"{current_time} Bot: {response}", width=70):
            print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
        chat_saver(current_time, name, [f"You: {user_input}", f"Bot: {response}"])

        if norm_input == "exit":
            time.sleep(1)
            break
def history(name, password, v):
    try:
        with open("login_interface.csv", 'a', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            if fh.tell() == 0:  # Write header if file is empty
                writer.writerow(["User", "Password", "Time"])
            writer.writerow([name, password, v])
    except PermissionError:
        print("Error: No permission to write to login_interface.csv")
    except Exception as e:
        print(f"Error writing to login_interface.csv: {e}")
keyword_responses = {
    "joke": ["Why don't programmers prefer dark mode? Because the light attracts bugs.",
             "Why did the computer go to art school? It wanted to draw a better 'byte'!"],
    "quote": ['"The only way to do great work is to love what you do." - Steve Jobs',
              '"Believe you can and you\'re halfway there." - Theodore Roosevelt'],
    "funfact": ["Did you know India has 22 official languages?",
                "The shortest war in history lasted 38 minutes!"],
    "weather": ["Please tell me the city, e.g., 'weather in Delhi'.",
                "Which city's weather do you want to know?"],
    "game": ["Want to play a quiz? What's the capital of India?",
             "Let's play 20 Questions! Think of something, and I'll guess!"]
}
chat_history = []
WEATHER_API_KEY = None
def loading_screen(name):
    print('-' * 20)
    time.sleep(1)
    print(f"Initializing for {name}")
    time.sleep(1)
    print("Updating system...")
    time.sleep(1)
    print("Ready!")
    time.sleep(1)
    print("𝗪𝗲𝗹𝗰𝗼𝗺𝗲")
def calculator_complex():
    print("Enter expressions like: 22/11 + 1 - 3")
    try:
        expr = input("Enter equation: ")
        tree = ast.parse(expr, mode='eval')
        result = eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, {})
        print(f"Result: {expr} = {result}")
    except (SyntaxError, ValueError, ZeroDivisionError) as e:
        print("Invalid expression or error:", e)
def calculator_normal():
    while True:
        print("\nOperations: +, -, *, /, %, E (Exit)")
        op = input("Choose operation: ")
        if op == 'E':
            break
        if op not in ['+', '-', '*', '/', '%']:
            print("Invalid operation")
            continue
        try:
            a = float(input("First number: "))
            b = float(input("Second number: "))
            if op == '+':
                print(f"{a} + {b} = {a + b}")
            elif op == '-':
                print(f"{a} - {b} = {a - b}")
            elif op == '*':
                print(f"{a} * {b} = {a * b}")
            elif op == '/':
                if b == 0:
                    print("Cannot divide by zero!")
                else:
                    print(f"{a} / {b} = {a / b}")
            elif op == '%':
                print(f"{a} % {b} = {a % b}")
        except ValueError:
            print("Enter valid numbers")
def dictionary():
    with open("Facts.txt", 'r', encoding="utf-8") as fh:
        lines = fh.readlines()
        if lines:
            print("📌 Random Fact: ", random.choice(lines).strip())
        else:
            print("No facts available.")
def load_quiz_data(file_path):
    """Load quiz questions and answers from CSV file."""
    questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                questions.append({
                    'question': row['Question'],
                    'answer': row['Answer']
                })
        return questions
    except FileNotFoundError:
        print("Error: Quiz file not found!")
        return []
    except Exception as e:
        print(f"Error loading quiz data: {e}")
        return []
def run_quiz():
    """Run the interactive quiz game."""
    file_path = "F:\Folder of codes\csv\gk_quiz.csv"  
    questions = load_quiz_data(file_path)    
    if not questions:
        print("No questions loaded. Exiting...")
        return
    score = 0
    total_questions = len(questions)   
    random.shuffle(questions)
    print("Welcome to the General Knowledge Quiz!")
    print("Type your answer and press Enter. Type 'quit' to exit.\n")    
    for i, q in enumerate(questions, 1):
        print(f"Question {i}: {q['question']}")
        user_answer = input("Your answer: ").strip()
        if user_answer.lower() == 'quit':
            break     
        normalized_user = normalize(user_answer)
        normalized_correct = normalize(q['answer'])
        
        if normalized_user == normalized_correct:
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The correct answer is: {q['answer']}")
        print()  # Empty line for readability
    
    # Display final score
    print(f"\nQuiz finished! Your score: {score}/{total_questions}")
    percentage = (score / total_questions) * 100
    print(f"Percentage: {percentage:.2f}%")
def quizeer():
    try:
        run_quiz()
    except KeyboardInterrupt:
        print("\nQuiz interrupted by user. Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")
def fun_chat(name, botname):
    print(f"Welcome {name}! Chatting with {botname}")
    attempts = 3
    while attempts > 0:
        print("""
        1. Introduction
        2. Greetings
        3. Purpose
        4. Concept
        5. Exit
        """)
        try:
            ch = int(input("Choose (1-5): "))
            if ch == 1:
                print("I'm a Python chatbot for fun and learning!")
            elif ch == 2:
                print("1. Hey\n2. Kaisa hai\n3. Aur bata\n4. Goodmorning\n5. Hello")
                greet = input("Choose (1-5): ")
                greetings = {
                    "1": "Heyyy! What's up? 😎",
                    "2": "Bindaas bidu! 😁",
                    "3": "Chillin', what's the scene? 🔥",
                    "4": "Good morning! 🌞",
                    "5": "Hellooo! Ready to rock? 🤘"
                }
                print(greetings.get(greet, "Invalid greeting 😅"))
            elif ch == 3:
                print("I assist with info, quizzes, and fun!")
            elif ch == 4:
                pwd = input("Password: ")
                if pwd == '159':
                    print("Secret: I'm built for versatility!")
                else:
                    print("Wrong password!")
                    attempts -= 1
            elif ch == 5:
                break
            else:
                print("Choose 1-5")
        except ValueError:
            print("Enter a number")
    if attempts == 0:
        print("Too many wrong attempts")
def encode_decode():
    code_map = {'a': '!', 'b': '@', 'c': '#', 'd': '$', 'e': '%', 'f': '^', 'g': '&', 'h': '*', 'i': '('}
    rev_map = {v: k for k, v in code_map.items()}
    max_len = max(len(k) for k in rev_map)
    while True:
        print("\n1. Encode\n2. Decode\n3. Exit")
        choice = input("Choose (1/2/3): ")
        if choice == '1':
            msg = input("Message: ")
            encoded = ''.join(code_map.get(ch, ch) for ch in msg)
            print("Encoded:", encoded)
        elif choice == '2':
            code = input("Code: ")
            decoded = ''
            i = 0
            while i < len(code):
                matched = False
                for l in range(max_len, 0, -1):
                    chunk = code[i:i+l]
                    if chunk in rev_map:
                        decoded += rev_map[chunk]
                        i += l
                        matched = True
                        break
                if not matched:
                    decoded += code[i]
                    i += 1
            print("Decoded:", decoded)
        elif choice == '3':
            break
        else:
            print("Choose 1, 2, or 3")
def creation_is():
    try:
        num = int(input("Number for table: "))
        limit = int(input("Up to: "))
        for i in range(limit + 1):
            print(f"{num} × {i} = {num * i}")
    except ValueError:
        print("Enter valid numbers")
def shlokas():
    path = 'F:\Folder of codes\csv\shlokas.csv'
    with open(path, 'r', encoding='utf-8') as fh:
        read = csv.reader(fh)
        next(read)  
        shlokas_list = [row[0] for row in read if row]  
        k = random.choice(shlokas_list) 
        width = 80
        top_border = '~' * width
        mid_border = '=' * width
        bottom_border = '~' * width
        wrapped_shloka = textwrap.wrap(k, width - 10)  
        centered_shloka = [line.center(width) for line in wrapped_shloka]
        title = "Daily Shloka"
        title_line = f"{' ' * ((width - len(title) - 4) // 2)}* {title} *{' ' * ((width - len(title) - 4) // 2)}"
        print(top_border)
        print(title_line)
        print(mid_border)
        print()  
        for line in centered_shloka:
            print(line)
        print()  
        print(bottom_border)
def data_records(name, password, tareek):
    try:
        with open("User.csv", 'a', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            if fh.tell() == 0:  # Write header if file is empty
                writer.writerow(["Names", "Password", "Date and Time"])
            writer.writerow([name, password, tareek])
    except PermissionError:
        print("Error: No permission to write to User.csv")
    except Exception as e:
        print(f"Error writing to User.csv: {e}")
def greet_user():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"
def chatbot_interface(name, botname,password,t1):
    loading_screen(name)
    clear_screen()
    while True:
        print(f"\nWelcome {name}! I'm {botname} | {greet_user()}")
        print("""
        Menu:
        1. Chat
        2. Simple Calculator
        3. Complex Calculator
        4. Quiz
        5. Fun Chat
        6. Random Fact
        7. Encode/Decode
        8. Multiplication Table
        9. Educational Quiz
        10. Shloka
        11. Exit
        """)
        try:
            ch = input("Choose (1-11): ")
            if ch == '1':
                chat_interaction(name)
                clear_screen()
            elif ch == '2':
                calculator_normal()
            elif ch == '3':
                calculator_complex()
            elif ch == '4':
                quizeer()
            elif ch == '5':
                fun_chat(name, botname)
            elif ch == '6':
                dictionary()
            elif ch == '7':
                encode_decode()
            elif ch == '8':
                creation_is()
            elif ch == '9':
                educational_chat_csv()
            elif ch == '10':
                shlokas()
            elif ch == '11':
                print("Terminating...")
                time.sleep(2)
                clear_screen()
                t2 = datetime.now()
                diff = t2 - t1
                hours, remainder = divmod(diff.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                v = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                history(name,password,v)
                break
            else:
                print("Choose 1-11")
        except ValueError:
            print("Enter a valid number")
#===================================================================================================================================
# ======admin line==================================================================================================================
def admin_panel(name,password):
    print("Loading.....")
    time.sleep(2)
    print("Loading admin panel")
    time.sleep(2)
    print("Redirecting to admin panel")
    time.sleep(2.5)
    t1 = datetime.now()
    clear_screen()
    user(name,password,t1)
        
def creation():
    with open("login_interface.csv", 'r') as fh:
        read = csv.reader(fh)
        print(f"|{'Name':<15}|{'Password':<15}|{'Time spent':<15}|")
        print("-" * 49)
        for i in read:
            print(f"|{i[0]:<15}|{i[1]:<15}|{i[2]:<15}|")
def data():
    with open("chat_history.csv", 'r') as fh:
        read = csv.reader(fh)
        rows = list(read)
        print(f"|{'Time':<10}|{'User':<10}|{'Receiver':<10}|{'Message':<30}|")
        print("-" * 70)
        for i in rows:
            print(f"|{i[0]:<10}|{i[1]:<10}|{i[2]:<10}|{i[3]:<30}|")
def time_search(name):
    with open("chat_history.csv", 'r') as fh:
        read = csv.reader(fh)
        next(read)  # Skip header if present
        found = False
        results = []
        for row in read:
            if name == row[0]:
                results.append(row)
                found = True
        if found:
            print("\n📌 Data found:\n")
            print(f"|{'Time':<10}|{'User':<10}|{'Receiver':<10}|{'Message':<30}|")
            print("-" * 70)
            for i in results:
                print(f"|{i[0]:<10}|{i[1]:<10}|{i[2]:<10}|{i[3]:<30}|")
        else:
            print("❌ Data not found")
def name_search(name):
    with open("chat_history.csv", 'r') as fh:
        read = csv.reader(fh)
        next(read)  # Skip header if present
        found = False
        results = []
        for row in read:
            if name.lower() == row[1].lower():  # Case-insensitive match
                results.append(row)
                found = True
        if found:
            print("\n📌 Data found:\n")
            print(f"|{'Time':<10}|{'User':<10}|{'Receiver':<10}|{'Message':<30}|")
            print("-" * 70)
            for i in results:
                print(f"|{i[0]:<10}|{i[1]:<10}|{i[2]:<10}|{i[3]:<30}|")
        else:
            print("❌ Data not found")
def show_password_status():
    file_path = r"F:\Folder of codes\complete projects\Newdata.csv"
    c = {
        'a': '1', 'b': '2', 'c': '3', 'd': '5', 'e': '6', 'f': '7', 'g': '8', 'h': '9', 'k': '0',
        'l': '`', 'm': '~', 'n': '!', 'o': '@', 'p': '#', 'q': '$', 'r': '%', 's': '^', 't': '&',
        'w': '*', 'x': '(', 'y': ')', 'z': '_', ' ': ' '
    }
    file = {
        '1': '!@#', '2': '#@!', '3': '$%#', '4': '#ef', '5': '@ed', '6': '@&&', '7': '!!#',
        '8': '@#@', '9': '%&%', '0': '$&#', 'a': '@!a', 'b': '#$b', 'c': '%^c', 'd': '&*d',
        'e': '*()e', 'f': '!#f', 'g': '@@g', 'h': '##h', 'i': '$$i', 'j': '^&j', 'k': '&%k',
        'l': '*&l', 'm': '!!m', 'n': '^^n', 'o': '@*o', 'p': '#^p', 'q': '$@q', 'r': '%*r',
        's': '^#s', 't': '&@t', 'u': '(@)u', 'v': '!%v', 'w': '##w', 'x': '&&x', 'y': '@$y',
        'z': '!@z', 'A': '@!A', 'B': '#$B', 'C': '%^C', 'D': '&*D', 'E': '*()E', 'F': '!#F',
        'G': '@@G', 'H': '##H', 'I': '$$I', 'J': '^&J', 'K': '&%K', 'L': '*&L', 'M': '!!M',
        'N': '^^N', 'O': '@*O', 'P': '#^P', 'Q': '$@Q', 'R': '%*R', 'S': '^#S', 'T': '&@T',
        'U': '(@)U', 'V': '!%V', 'W': '##W', 'X': '&&X', 'Y': '@$Y', 'Z': '!@Z', '!': '***',
        '@': '###', '#': '$$$', '$': '%%%', '%': '^^^', '^': '&&&', '&': '(((', '*': ')))',
        '(': '!!!', ')': '@@@', '-': '---', '_': '___', '+': '+++', '=': '===', '{': '{{{',
        '}': '}}}', '[': '[[]', ']': ']]]', ':': ':::', '"': '"""', "'": "'''", '<': '<<<',
        '>': '>>>', ',': ',,,', '.': '...', '/': '///', '?': '???'
    }
    c_reverse = {v: k for k, v in c.items()}  # Reverse mapping for decoding username and password
    code = {v: k for k, v in file.items()}  # Reverse mapping for decoding (kept for potential future use)

    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            next(reader, None)  # Skip header
            users = []
            for row in reader:
                if len(row) >= 2:
                    username_enc = row[0]
                    password_enc = row[1]
                    # Decode username using c/c_reverse
                    try:
                        username = ''
                        i = 0
                        while i < len(username_enc):
                            chunk = username_enc[i:i+1]  # c dictionary uses single-char mappings
                            if chunk in c_reverse:
                                username += c_reverse[chunk]
                                i += 1
                            else:
                                username += '?'
                                i += 1
                    except:
                        username = "Error decoding"
                    # Decode password using c/c_reverse
                    try:
                        password = ''
                        i = 0
                        while i < len(password_enc):
                            found = False
                            for length in range(4, 0, -1):  # Try longest possible matches
                                chunk = password_enc[i:i+length]
                                if chunk in code:
                                    password += code[chunk]
                                    i += length
                                    found = True
                                    break
                            if not found:
                                password += '?'
                                i += 1
                    except:
                        password = "Error decoding"
                    # Determine status
                    status = "Active"
                    if username == "Error decoding" or password == "Error decoding" or '?' in username or '?' in password:
                        status = "Invalid"
                    elif len(password) < 3:
                        status = "Weak"
                    users.append((username_enc, username, password, status))
            
            # Display enhanced interface
            width = 80
            print("\n" + "=" * width)
            print(f"{' Password Status Dashboard '.center(width)}")
            print("=" * width)
            print(f"| {'Encoded Username':<20} | {'Decoded Username':<20} | {'Decoded Password':<20} | {'Status':<12} |")
            print("-" * width)
            for user in users:
                encoded, decoded, pwd, status = user
                print(f"| {encoded:<20} | {decoded:<20} | {pwd:<20} | {status:<12} |")
            print("-" * width)
            print(f"Total Users: {len(users)}")
            print(f"Active: {sum(1 for u in users if u[3] == 'Active')}")
            print(f"Weak: {sum(1 for u in users if u[3] == 'Weak')}")
            print(f"Invalid: {sum(1 for u in users if u[3] == 'Invalid')}")
            print("=" * width)
            
    except FileNotFoundError:
        print("\n" + "=" * width)
        print(f"{' ERROR: File not found at {file_path} '.center(width)}")
        print("=" * width)
    except Exception as e:
        print("\n" + "=" * width)
        print(f"{' ERROR: {str(e)} '.center(width)}")
        print("=" * width)
def search():
    while True: 
        print("Welcome to search panel ")
        print("Press keys to select to  search through")
        print("\n 1.TIME" \
              "\n2.NAME" \
              "\n3.Exit")
        ch = int(input("Admin :-"))
        if ch == 1:
           print("Search Method by Time")
           print("Enter the time to search")
           print("HH:MM:SS")
           name = input("Admin :-")
           time_search(name)
        elif ch == 2:
           print("Search Method by Name")
           print("Enter the Name to search")
           name = input("Admin :-")
           name_search(name)   
        elif ch == 3:
            print("Terminating...")
            time.sleep(2)
            print("Redirecting to back panel")
            time.sleep(1)
            print("Loading.......")
            break
        else:
           print("Try again")
def concept_hell():
    print("\n1.TO see flowq chart" \
          "\n2.To see detail structure")
    ch = input("Admin :-")
    if ch == '1':
        print('  '*30)
        print('__'*30,"Flowchart For Your Chatbot✔❗❗😂",'__'*30)
        with open("flowchart.txt",'r',encoding="utf-8")as fh:
            re = fh.read()
            print(re)    
    elif ch =='2':
        print('  '*30)
        print('__'*30,"Description For Your Chatbot❗❗🙌",'__'*30)
        with open("concept_map.txt",'r',encoding="utf-8")as fh:
            re = fh.read()
            print(re)
    else:
        print("Invalid Input")
def add_fact():
    with open("Facts.txt", 'r', encoding="utf-8") as fh:
        lines = fh.readlines()
    with open("Facts.txt", 'w', encoding="utf-8") as fh:
        fact = input("Enter New Fact: ").strip()
        if not fact.startswith('\n'):
            fact = '\n' + fact
        lines.append(fact + '\n')
        fh.writelines(lines)
        print("✅ New fact added successfully.")
def show_all_facts():
    with open("Facts.txt", 'r', encoding="utf-8") as fh:
        lines = fh.readlines()
        if not lines:
            print("No facts to show.")
        else:
            print("📚 All Facts:")
            for i, line in enumerate(lines, start=1):
                print(f"{i}. {line.strip()}")    
def delete_fact():
    with open("Facts.txt", 'r', encoding="utf-8") as fh:
        lines = fh.readlines()
    if not lines:
        print("❌ No facts to delete.")
        return
    print("📚 All Facts:")
    for i, line in enumerate(lines, start=1):
        print(f"{i}. {line.strip()}")
    try:
        choice = int(input("Enter the number of the fact to delete: "))
        if 1 <= choice <= len(lines):
            deleted = lines.pop(choice - 1)
            with open("Facts.txt", 'w', encoding="utf-8") as fh:
                fh.writelines(lines)
            print(f"✅ Deleted: {deleted.strip()}")
        else:
            print("❌ Invalid number.")
    except ValueError:
        print("❌ Please enter a valid number.")
#======================================================================================================================================
#======================================================================================================================================
# Mechanism for editing creating for you
# creation of editing View ,data,delete
def get_file_path():
    """Returns the path to the CSV file."""
    return r"F:\Folder of codes\csv\qa_data.csv"
def manage_backups(file_path, max_backups=5):
    """Manages backup files by keeping only the most recent ones."""
    backups = sorted(glob.glob(file_path + ".backup_*"))
    if len(backups) > max_backups:
        for old_backup in backups[:-max_backups]:
            try:
                os.remove(old_backup)
                print(f"ℹ️ Removed old backup: {old_backup}")
            except Exception as e:
                print(f"❌ Error removing backup {old_backup}: {str(e)}")
def view():
    """Displays chatbot data in a formatted table."""
    print("\n=== Chatbot Data ===")
    file_path = get_file_path()
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as fh:
            read = csv.reader(fh)
            headers = next(read)  
            data = [row for row in read]  
            if not data:
                print("ℹ️ No data available in the file.")
                return
            col1_width = 30
            col2_width = 50
            print(f"\n┌{'─' * (col1_width + 2)}┬{'─' * (col2_width + 2)}┐")
            print(f"│ {headers[0]:<{col1_width}} │ {headers[1]:<{col2_width}} │")
            print(f"├{'─' * (col1_width + 2)}┼{'─' * (col2_width + 2)}┤")
            for row in data:
                question = row[0][:col1_width-3] + "..." if len(row[0]) > col1_width-3 else row[0]
                answer = row[1][:col2_width-3] + "..." if len(row[1]) > col2_width-3 else row[1]
                print(f"│ {question:<{col1_width}} │ {answer:<{col2_width}} │")
            print(f"└{'─' * (col1_width + 2)}┴{'─' * (col2_width + 2)}┘")
            print(f"ℹ️ Displayed {len(data)} rows.")            
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}. Please check the path.")
    except PermissionError:
        print(f"❌ Error: Permission denied for {file_path}. Check file access.")
    except Exception as e:
        print(f"❌ Error: Unable to read file - {str(e)}")
def add_data():
    """Adds a new question-answer pair to the CSV file after checking for duplicates."""
    file_path = get_file_path() 
    if not os.path.exists(file_path):
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Question', 'Answer'])
            print(f"ℹ️ Created new CSV file at {file_path}")
        except Exception as e:
            print(f"❌ Error: Unable to create file - {str(e)}")
            return
    question = input("Enter question (or type 'cancel' to abort): ").strip()
    if question.lower() == 'cancel':
        print("ℹ️ Operation cancelled.")
        return
    if not question:
        print("❌ Error: Question cannot be empty.")
        return
    if ',' in question:
        print("❌ Error: Commas are not allowed in questions to maintain CSV format.")
        return
    try:
        rows = []
        existing_questions = []
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            rows.append(headers)
            for row in reader:
                rows.append(row)
                existing_questions.append(row[0].lower())        
        if question.lower() in existing_questions:
            for row in rows[1:]:
                if row[0].lower() == question.lower():
                    print(f"Existing question: {row[0]}")
                    print(f"Current answer: {row[1]}")
                    break
            overwrite = input("Do you want to overwrite the existing answer? (y/n): ").lower()
            if overwrite != 'y':
                print("ℹ️ Operation cancelled.")
                return
            answer = input("Enter new answer (or type 'cancel' to abort): ").strip()
            if answer.lower() == 'cancel':
                print("ℹ️ Operation cancelled.")
                return
            if not answer:
                print("❌ Error: Answer cannot be empty.")
                return
            if ',' in answer:
                print("❌ Error: Commas are not allowed in answers to maintain CSV format.")
                return
            rows = [headers] + [([row[0], answer] if row[0].lower() == question.lower() else row) for row in rows[1:]]
            try:
                backup_path = file_path + f".backup_{int(time.time())}"
                shutil.copy(file_path, backup_path)
                print(f"ℹ️ Backup created at {backup_path}")
                manage_backups(file_path)
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
                print("✅ Answer updated successfully.")
                return
            except PermissionError:
                print(f"❌ Error: Permission denied for {file_path}. Check file access.")
                return
            except Exception as e:
                print(f"❌ Error: Unable to write to file - {str(e)}")
                return
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}. Please check the path.")
        return
    except PermissionError:
        print(f"❌ Error: Permission denied for {file_path}. Check file access.")
        return
    except Exception as e:
        print(f"❌ Error: Unable to read file - {str(e)}")
        return
    answer = input("Enter answer (or type 'cancel' to abort): ").strip()
    if answer.lower() == 'cancel':
        print("ℹ️ Operation cancelled.")
        return
    if not answer:
        print("❌ Error: Answer cannot be empty.")
        return
    if ',' in answer:
        print("❌ Error: Commas are not allowed in answers to maintain CSV format.")
        return
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([question, answer])
        print("✅ Data added successfully.")
    except PermissionError:
        print(f"❌ Error: Permission denied for {file_path}. Check file access.")
    except Exception as e:
        print(f"❌ Error: Unable to write to file - {str(e)}")
def delete_data():
    """Deletes rows from the CSV file based on a keyword in the question."""
    file_path = get_file_path()
    keyword = input("Enter keyword to delete row (in question, or 'cancel' to abort): ").strip()
    if keyword.lower() == 'cancel':
        print("ℹ️ Operation cancelled.")
        return
    if not keyword:
        print("❌ Error: Keyword cannot be empty.")
        return    
    rows = []
    deleted_count = 0
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader) 
            rows.append(headers)
            for row in reader:
                if keyword.lower() not in row[0].lower():
                    rows.append(row)
                else:
                    deleted_count += 1            
        if deleted_count == 0:
            print("❌ No matching data found.")
            return
        confirm = input(f"ℹ️ Found {deleted_count} row(s) to delete. Confirm? (y/n): ").lower()
        if confirm != 'y':
            print("ℹ️ Deletion cancelled.")
            return
        backup_path = file_path + f".backup_{int(time.time())}"
        shutil.copy(file_path, backup_path)
        print(f"ℹ️ Backup created at {backup_path}")
        manage_backups(file_path)
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        print(f"✅ Deleted {deleted_count} row(s) successfully.")        
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}. Please check the path.")
    except PermissionError:
        print(f"❌ Error: Permission denied for {file_path}. Check file access.")
    except Exception as e:
        print(f"❌ Error: Unable to process file - {str(e)}")

def edit_menu():
    """Displays a menu to manage chatbot data."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  
        print("\n=== Chatbot Data Management Menu ===")
        print("1. View Data")
        print("2. Add Data")
        print("3. Delete Data")
        print("4. Exit")
        choice = input("\nChoose option (1-4): ").strip()        
        if choice == '1':
            view()
        elif choice == '2':
            add_data()
        elif choice == '3':
            delete_data()
        elif choice == '4':
            confirm = input("ℹ️ Are you sure you want to exit? (y/n): ").lower()
            if confirm == 'y':
                print("👋 Exiting program. Goodbye!")
                break
            else:
                print("ℹ️ Exit cancelled.")
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        input("\nPress Enter to continue...") 
#=======================================================================================================================================
#=======================================================================================================================================
def admin_mov(name, password, v):
    try:
        with open("admin_confi.csv", 'a', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            if fh.tell() == 0:
                writer.writerow(["Name", "Password", "Time"])
            writer.writerow([name, password, v])
    except PermissionError:
        print("Error: No permission to write to admin_confi.csv")
    except Exception as e:
        print(f"Error writing to admin_confi.csv: {e}")
        
def user(name,password,t1):
    while True:
        try:
            print("\nWelcome to Admin Panel")
            print("1. View User Login")
            print("2. View Chat Data")
            print("3. Search the Data")
            print("4. Extra Features (Coming Soon)")
            print("5. To know about bot")
            print("6. Chatbot Data")
            print("7. TO see The password status")
            print("8.Exit")
            ch = input("Admin :- ")
            

            if ch == '1':
                creation()
            elif ch == '2':
                data()
            elif ch == '3':
                search()
            elif ch == '4':
                print("TO see data")
                print("1.To see data")
                print("2.Add data")
                k = int(input("Admin :-"))
                if k == 1:
                    show_all_facts()
                elif k == 2:
                    add_fact()
                elif k == 3:
                    delete_fact()
                else:
                    print("Invalid type inputs!!!")                   
            elif ch == '5':
                 pas = input("Enter Password :-")
                 if pas == '159753':
                     print("Acess Granted✔✔......")
                     time.sleep(2)
                     concept_hell()
                 else:
                     print("Access Denied")
            elif ch == '6':
                print("Redirecting to chatbot data control panel")
                print("Loading.....")
                time.sleep(1.5)
                edit_menu()
            elif ch == '7':
                show_password_status()
            elif ch == '8':
                print("Exiting the admin panel")
                time.sleep(1)
                clear_screen()
                break
            else:
                print("Invalid choice. Try again.")
                t2 = datetime.now()
                diff = t2 - t1
                hours, remainder = divmod(diff.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                v = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                admin_mov(name,password,v)
        except ValueError as err:
            print("Error:", err)
#==========================================================================================================================
#=========================================================================================================================================
#==========================================================================================================================================

#=============================================================================================================================
#=============================================================================================================================
#=============================================================================================================================


LOCK_TIME = 300  # 5 minutes default lock time
RATE_LIMIT_LOCK = 30  # 30 seconds lockout after 3 failed attempts
INPUT_TIMEOUT = 60  # 60 seconds timeout for user input
WARNING_TIME = 10  # Warning displayed 10 seconds before timeout
SIGNUP_PASSWORD = "mySecret123"  # Password required to access signup interface

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def timer_animation(duration=20):
    """Display a 20-second animation between sessions."""
    spinner = "|/-\\"
    count = duration
    for i in range(count, 0, -1):
        progress = "█" * (count - i) + " " * i
        spinner_char = spinner[(count - i) % 4]
        clear_screen()
        print("\n" * 3)
        print("┌" + "─" * 40 + "┐")
        print(f"│{'Preparing for next session...'.center(40)}│")
        print(f"│{f'{i} seconds remaining {spinner_char}'.center(40)}│")
        print(f"│{f'[ {progress} ] {(count - i) * 100 // count}%'.center(40)}│")
        print("└" + "─" * 40 + "┘")
        time.sleep(1)
    clear_screen()

def rate_limit_animation():
    """Display a 30-second animation for rate limit lockout."""
    spinner = "|/-\\"
    count = RATE_LIMIT_LOCK
    for i in range(count, 0, -1):
        progress = "█" * (count - i) + " " * i
        spinner_char = spinner[(count - i) % 4]
        clear_screen()
        print("\n" * 3)
        print("┌" + "─" * 40 + "┐")
        print(f"│{'Rate limit lockout active'.center(40)}│")
        print(f"│{f'{i} seconds remaining {spinner_char}'.center(40)}│")
        print(f"│{f'[ {progress} ] {(count - i) * 100 // count}%'.center(40)}│")
        print("└" + "─" * 40 + "┘")
        time.sleep(1)
    clear_screen()

def rate_limit_lockout():
    """Handle rate limit lockout with animation."""
    print(f"Too many attempts. System locked for {RATE_LIMIT_LOCK} seconds.")
    rate_limit_animation()
    print("Lockout period ended. You can try again.")

def lock_system(lock_duration):
    """Handle final system lockout and terminate."""
    print(f"Maximum attempts reached. System locking for {lock_duration} seconds.")
    time.sleep(lock_duration)
    print("Program terminated due to multiple failed sessions.")
    sys.exit(1)

def input_with_timeout(prompt, timeout=INPUT_TIMEOUT, warning_time=WARNING_TIME):
    """Get input with a timeout, showing a warning near the end."""
    if platform.system() == 'Windows':
        def get_input(result):
            try:
                result.append(input(prompt))
            except (EOFError, KeyboardInterrupt):
                result.append("")
        result = []
        thread = threading.Thread(target=get_input, args=(result,))
        thread.daemon = True
        thread.start()
        start_time = time.time()
        warning_shown = False
        while thread.is_alive():
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            if remaining <= warning_time and not warning_shown:
                print(f"\nWARNING: {int(remaining)} seconds left before termination!")
                print(prompt, end="", flush=True)
                warning_shown = True
            if elapsed >= timeout:
                print("\nNo input received. Terminating program.")
                sys.exit(1)
            time.sleep(0.1)
        if warning_shown:
            print("\r" + " " * 50 + "\r", end="")  # Clear warning line
        return result[0] if result else ""
    else:
        print(prompt, end="", flush=True)
        start_time = time.time()
        warning_shown = False
        while True:
            remaining = timeout - (time.time() - start_time)
            if remaining <= warning_time and not warning_shown:
                print(f"\nWARNING: {int(remaining)} seconds left before termination!")
                print(prompt, end="", flush=True)
                warning_shown = True
            if remaining <= 0:
                print("\nNo input received. Terminating program.")
                sys.exit(1)
            rlist, _, _ = select.select([sys.stdin], [], [], max(0, remaining))
            if rlist:
                if warning_shown:
                    print("\r" + " " * 50 + "\r", end="")  # Clear warning line
                return sys.stdin.readline().strip()
            else:
                continue

def login_interface(session_attempts=0, total_attempts=0):
    botname = "ChatBuddy"
    attempts = 3
    tareek = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c = {
        'a': '1', 'b': '2', 'c': '3', 'd': '5', 'e': '6', 'f': '7', 'g': '8', 'h': '9', 'k': '0',
        'l': '`', 'm': '~', 'n': '!', 'o': '@', 'p': '#', 'q': '$', 'r': '%', 's': '^', 't': '&',
        'w': '*', 'x': '(', 'y': ')', 'z': '_', ' ': ' '
    }

    file = {
        '1': '!@#', '2': '#@!', '3': '$%#', '4': '#ef', '5': '@ed', '6': '@&&', '7': '!!#',
        '8': '@#@', '9': '%&%', '0': '$&#', 'a': '@!a', 'b': '#$b', 'c': '%^c', 'd': '&*d',
        'e': '*()e', 'f': '!#f', 'g': '@@g', 'h': '##h', 'i': '$$i', 'j': '^&j', 'k': '&%k',
        'l': '*&l', 'm': '!!m', 'n': '^^n', 'o': '@*o', 'p': '#^p', 'q': '$@q', 'r': '%*r',
        's': '^#s', 't': '&@t', 'u': '(@)u', 'v': '!%v', 'w': '##w', 'x': '&&x', 'y': '@$y',
        'z': '!@z', 'A': '@!A', 'B': '#$B', 'C': '%^C', 'D': '&*D', 'E': '*()E', 'F': '!#F',
        'G': '@@G', 'H': '##H', 'I': '$$I', 'J': '^&J', 'K': '&%K', 'L': '*&L', 'M': '!!M',
        'N': '^^N', 'O': '@*O', 'P': '#^P', 'Q': '$@Q', 'R': '%*R', 'S': '^#S', 'T': '&@T',
        'U': '(@)U', 'V': '!%V', 'W': '##W', 'X': '&&X', 'Y': '@$Y', 'Z': '!@Z', '!': '***',
        '@': '###', '#': '$$$', '$': '%%%', '%': '^^^', '^': '&&&', '&': '(((', '*': ')))',
        '(': '!!!', ')': '@@@', '-': '---', '_': '___', '+': '+++', '=': '===', '{': '{{{',
        '}': '}}}', '[': '[[]', ']': ']]]', ':': ':::', '"': '"""', "'": "'''", '<': '<<<',
        '>': '>>>', ',': ',,,', '.': '...', '/': '///', '?': '???'
    }

    code = {v: k for k, v in file.items()}

    file_path = r"F:\Folder of codes\complete projects\Newdata.csv"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    while attempts > 0 and total_attempts < 6:
        clear_screen()
        print("\n" * 2)
        print("╔" + "═" * 30 + "╗")
        print(f"║{'ChatBuddy Interface'.center(30)}║")
        print("╠" + "═" * 30 + "╣")
        print(f"║{'1. Login'.ljust(30)}║")
        print(f"║{'2. Signup or Register'.ljust(30)}║")
        print(f"║{'3. Exit'.ljust(30)}║")
        print("╚" + "═" * 30 + "╝")
        print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")

        try:
            ch = input_with_timeout("Please Enter your choice: ")

            if ch == '1':
                clear_screen()
                print("Redirecting to login interface...")
                time.sleep(1)
                print("Loading...\nPlease wait...")
                time.sleep(1)

                while attempts > 0 and total_attempts < 6:
                    clear_screen()
                    print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                    name = input_with_timeout("Username: ")
                    password = input_with_timeout("Password: ")
                    data_records(name, password, tareek)  # Log login attempt

                    if name.lower() in ['admin', 'controller', 'editor'] and password in ['12345', '456852', '159153', '159753', '007']:
                        print("Loading...")
                        time.sleep(2)
                        clear_screen()
                        print("Access granted! Admin mode.")
                        admin_panel(name, password)
                        return True

                    if not name or not password:
                        print("Error: Username and password cannot be empty.")
                        attempts -= 1
                        total_attempts += 1
                        print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                        if attempts == 0:
                            rate_limit_lockout()
                            attempts = 3
                        time.sleep(2)
                        continue

                    if len(password) < 3:  # Allow existing users with ≥3 char passwords
                        print("Error: Password must be at least 3 characters long.")
                        attempts -= 1
                        total_attempts += 1
                        print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                        if attempts == 0:
                            rate_limit_lockout()
                            attempts = 3
                        time.sleep(2)
                        continue

                    for char in name.lower():
                        if char not in c:
                            print(f"Error: Username contains invalid character '{char}'.")
                            attempts -= 1
                            total_attempts += 1
                            print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                            if attempts == 0:
                                rate_limit_lockout()
                                attempts = 3
                            time.sleep(2)
                            break
                    else:
                        for char in password:
                            if char not in file:
                                print(f"Error: Password contains invalid character '{char}'.")
                                attempts -= 1
                                total_attempts += 1
                                print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                                if attempts == 0:
                                    rate_limit_lockout()
                                    attempts = 3
                                time.sleep(2)
                                break
                        else:
                            st = ''.join(c.get(i, '?') for i in name.lower())
                            found = False
                            try:
                                with open(file_path, 'r', newline='', encoding='utf-8') as fh:
                                    reader = csv.reader(fh)
                                    next(reader, None)  # Skip header
                                    for row in reader:
                                        if len(row) < 2:
                                            continue
                                        if st == row[0]:
                                            encoded = row[1]
                                            decoded = ''
                                            for i in range(0, len(encoded), 3):
                                                part = encoded[i:i + 3]
                                                decoded += code.get(part, '?')
                                            if password == decoded:
                                                found = True
                                            break
                            except (FileNotFoundError, PermissionError, csv.Error) as e:
                                print(f"Error reading file: {e}")
                                attempts -= 1
                                total_attempts += 1
                                print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                                if attempts == 0:
                                    rate_limit_lockout()
                                    attempts = 3
                                time.sleep(2)
                                continue
                            except Exception as e:
                                print(f"Unexpected error reading file: {e}")
                                attempts -= 1
                                total_attempts += 1
                                print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                                if attempts == 0:
                                    rate_limit_lockout()
                                    attempts = 3
                                time.sleep(2)
                                continue

                            if found:
                                print("Loading...")
                                time.sleep(2)
                                clear_screen()
                                print("Access granted!")
                                t1 = datetime.now()
                                chatbot_interface(name, botname, password, t1)
                                t2 = datetime.now()
                                diff = t2 - t1
                                hours, remainder = divmod(diff.total_seconds(), 3600)
                                minutes, seconds = divmod(remainder, 60)
                                v = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                                history(name, password, v)
                                return True
                            else:
                                print("Access Denied")
                                attempts -= 1
                                total_attempts += 1
                                print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                                if attempts == 0:
                                    rate_limit_lockout()
                                    attempts = 3
                                time.sleep(2)

            elif ch == '2':
                clear_screen()
                print("Redirecting to Signup interface...")
                time.sleep(1)
                print("Loading...\nPlease wait...")
                time.sleep(2)
                signup_pass = input_with_timeout("Enter signup password: ")
                if signup_pass != SIGNUP_PASSWORD:
                    print("Error: Incorrect signup password.")
                    attempts -= 1
                    total_attempts += 1
                    print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                    if attempts == 0:
                        rate_limit_lockout()
                        attempts = 3
                    time.sleep(2)
                    continue
                else:
                    clear_screen()
                    print("Signup password accepted. Proceed to registration.")
                    time.sleep(1)
                    while True:
                        clear_screen()
                        username = input_with_timeout("Enter username: ")
                        password = input_with_timeout("Enter password: ")

                        if not username or not password:
                            print("Error: Username and password cannot be empty.")
                            time.sleep(2)
                            continue
                        if len(password) < 6:  # Stricter requirement for new signups
                            print("Error: Password must be at least 6 characters long.")
                            time.sleep(2)
                            continue
                        for char in username.lower():
                            if char not in c:
                                print(f"Error: Username contains invalid character '{char}'.")
                                time.sleep(2)
                                break
                        else:
                            for char in password:
                                if char not in file:
                                    print(f"Error: Password contains invalid character '{char}'.")
                                    time.sleep(2)
                                    break
                            else:
                                t = username.lower()
                                lo = ''.join(c.get(i, '?') for i in t)
                                st = ''.join(file.get(i, '???') for i in password)
                                cons = False
                                try:
                                    with open(file_path, 'r', newline='', encoding='utf-8') as fh:
                                        reader = csv.reader(fh)
                                        next(reader, None)  # Skip header if exists
                                        for row in reader:
                                            if len(row) > 0 and lo == row[0]:
                                                cons = True
                                                break
                                except FileNotFoundError:
                                    pass
                                except PermissionError:
                                    print(f"Error: No permission to read {file_path}.")
                                    time.sleep(2)
                                    continue
                                except csv.Error:
                                    print("Error: Invalid CSV format.")
                                    time.sleep(2)
                                    continue
                                except Exception as e:
                                    print(f"Error reading file: {e}")
                                    time.sleep(2)
                                    continue

                                if cons:
                                    print(f"This username '{username}' is already in use.")
                                    time.sleep(2)
                                else:
                                    try:
                                        file_exists = os.path.exists(file_path)
                                        with open(file_path, 'a', newline='', encoding='utf-8') as fh:
                                            writer = csv.writer(fh)
                                            if not file_exists:
                                                writer.writerow(["Username", "Password"])
                                            writer.writerow([lo, st])
                                        print("User registered successfully.")
                                        time.sleep(2)
                                    except PermissionError:
                                        print(f"Error: No permission to write to {file_path}.")
                                        time.sleep(2)
                                        continue
                                    except Exception as e:
                                        print(f"Error writing to file: {e}")
                                        time.sleep(2)
                                        continue
                                    choice = input_with_timeout("Press Enter to register another user or any key to return to menu: ")
                                    if choice:
                                        break

            elif ch == '3':
                clear_screen()
                print("Exiting...")
                time.sleep(1)
                return False
            else:
                print("Invalid choice. Try again.")
                attempts -= 1
                total_attempts += 1
                print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
                if attempts == 0:
                    rate_limit_lockout()
                    attempts = 3
                time.sleep(2)

        except EOFError:
            print("Input interrupted. Try again.")
            attempts -= 1
            total_attempts += 1
            print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
            if attempts == 0:
                rate_limit_lockout()
                attempts = 3
            time.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {e}")
            attempts -= 1
            total_attempts += 1
            print(f"Attempts remaining: {attempts}/3 (Total: {6 - total_attempts}/6)")
            if attempts == 0:
                rate_limit_lockout()
                attempts = 3
            time.sleep(2)

        if total_attempts >= 6:
            lock_system(LOCK_TIME)
            return False

    if session_attempts < 1 and total_attempts < 6:
        print("Too many failed attempts in this session. Initiating cooldown...")
        timer_animation()
        return login_interface(session_attempts + 1, total_attempts)
    else:
        lock_system(LOCK_TIME)
        return False
if __name__ == "__main__":
    try:
        success = login_interface()
        if not success:
            clear_screen()
            print("Closing program...")
    except KeyboardInterrupt:
        clear_screen()
        print("\nProgram interrupted")
    finally:
        clear_screen()
        print("Closing program...")