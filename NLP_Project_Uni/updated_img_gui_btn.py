import tkinter as tk
from tkinter import Text, Frame, Canvas, Scrollbar
from PIL import Image, ImageTk
import threading
import random
import h5py
from fuzzywuzzy import fuzz
import speech_recognition as sr
import pyttsx3

# ---------------------------
# Mapping function using a dictionary for all commands
# ---------------------------
def map_query_to_image(query_text: str) -> str:
    command_to_image = {
        "chairman basic sciences office": "chairman_basic_sciences_office.jpg",
        "assistant office bsi": "assistant_office_bsi.jpg",
        "phd classroom": "phd_classroom.jpg",
        "applied physics lab": "applied_physics_lab.jpg",
        "ms classroom": "ms_classroom.jpg",
        "electronic engineering lab": "electronic_engineering_lab.jpg",
        "Postgraduate Lab": "postgraduate_lab.jpg",
        "Digital Signal Processing": "digital_signal_processing.jpg",
        "cr 6": "cr6.jpg",
        "cr-6": "cr6.jpg",
        "cr 5": "cr5.jpg",
        "cr-5": "cr5.jpg",
        "cr 3": "cr3.jpg",
        "cr-3": "cr3.jpg",
        "cr 4": "cr4.jpg",
        "cr-4": "cr4.jpg",
        "cr 2": "cr2.jpg",
        "cr-2": "cr2.jpg",
        "Female Facilitation Center": "female_facilitation_center.jpg",
        "Professor Doctor Hasin Ullah Jan Office": "prof_dr_haseen_ullah_jan_office.jpg",
        "Professor Doctor Haseen Ullah Jan Office": "prof_dr_haseen_ullah_jan_office.jpg",
        "professor Doctor Sadiq Jan Office": "prof_dr_sadeeq_jan_office.jpg",
        "professor Doctor Sadeeq Jan Office": "prof_dr_sadeeq_jan_office.jpg",
        "boardroom": "boardroom.jpg",
        "Girls Common Room": "girls_common_room.jpg",
        "Lab 2": "lab2.jpg",
        "Microprocessor Lab": "microprocessor_lab.jpg",
        "Doctor Muhammad Abir Irfan Office": "dr_muhammad_abeer_irfan_office.jpg",
        "Doctor Muhammad Abeer Irfan Office": "dr_muhammad_abeer_irfan_office.jpg",
        "Doctor Amaad Khalil Office": "dr_amaad_khalil_office.jpg",
        "Doctor Amad Khalil Office": "dr_amaad_khalil_office.jpg",
        "Engineer Abdullah Hamid Office": "engr_abdullah_hamid_office.jpg",
        "Engineer Abdullah Hameed Office": "engr_abdullah_hamid_office.jpg",
        "Doctor Samad Basir Khan Office": "dr_samad_baseer_khan_office.jpg",
        "Doctor Samad Baseer Khan Office": "dr_samad_baseer_khan_office.jpg",
        "prof. dr. zahid wadud mufti office": "prof_dr_zahid_wadud_mufti_office.jpg",
        "professor Doctor Zahid Wadud Mufti Office": "prof_dr_zahid_wadud_mufti_office.jpg"
    }
    lower_text = query_text.lower()
    for command, image in command_to_image.items():
        if command in lower_text:
            return image
    return None


# ---------------------------
# GUI helper: Load and update background image
# ---------------------------
def load_background_image(image_path, canvas, width, height):
    try:
        img = Image.open(image_path)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo  # keep a reference to avoid garbage collection
        print(f"Background updated with image: {image_path}")
    except Exception as e:
        print("Error loading background image:", e)

# ---------------------------
# Function: Record and Process Voice Input on Demand
# ---------------------------
def record_and_process():
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices and len(voices) > 1:
        engine.setProperty('voice', voices[1].id)  # choose a female voice, for example
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Recording... Speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            return

    try:
        recognized_text = recognizer.recognize_google(audio)
        print("Recognized text:", recognized_text)

        max_similarity = 0
        best_matches = []  # List of tuples: (stored_question, stored_response)
        for row in chat_data:
            stored_question = row[0].decode()
            stored_response = row[1].decode()
            similarity_score = fuzz.ratio(recognized_text.lower(), stored_question.lower())
            if similarity_score >= max_similarity:
                if similarity_score > max_similarity:
                    max_similarity = similarity_score
                    best_matches = [(stored_question, stored_response)]
                else:
                    best_matches.append((stored_question, stored_response))

        if best_matches:
            selected_question, selected_response = random.choice(best_matches)
            # First, update the image if there is one
            image_file = map_query_to_image(selected_question)
            if image_file:
                root.after(0, lambda: load_background_image(image_file, canvas, 800, 400))
            else:
                print("No mapping found for query to update background image.")

            # Update the text area to show only the chatbot's response
            root.after(0, lambda: text_area.delete("1.0", tk.END))
            root.after(0, lambda: text_area.insert("end", selected_response + "\n"))

            # Finally, speak the chatbot's response
            engine.say(selected_response)
            engine.runAndWait()
        else:
            print("No match found in chat data.")

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service: {e}")
    except Exception as e:
        print("Error in voice recording process:", e)

# ---------------------------
# Trigger Recording on Demand (Button or Shift Key)
# ---------------------------
def trigger_recording(event=None):
    # Run voice recording in a separate thread to avoid blocking the UI
    threading.Thread(target=record_and_process, daemon=True).start()

# ---------------------------
# MAIN CODE
# ---------------------------
# Load the HDF5 file with chat data.
hdf5_file_path = 'chatbot.h5'
with h5py.File(hdf5_file_path, 'r') as hf:
    chat_data = hf['chat_data'][:]

# Create the main Tkinter window
root = tk.Tk()
root.title("Chat Response GUI")
root.geometry("800x600")
root.configure(bg="#34495e")  # Dark blue-gray background

# ----------------------------
# Top Frame: Full-Frame Background Image Area
# ----------------------------



top_frame = Frame(root, width=800, height=400, bg="black")
top_frame.pack_propagate(False)
top_frame.pack(side="top", fill="both")

canvas = Canvas(top_frame, width=800, height=400, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Load the initial view image directly (without calling load_background_image)
initial_image_path = "Initial View.jpg"  # Replace with your image path
try:
    img = Image.open(initial_image_path)
    img = img.resize((800, 400), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # Keep a reference to avoid garbage collection
    print("Initial view loaded with image:", initial_image_path)
except Exception as e:
    print("Error loading initial view image:", e)

# ----------------------------
# Bottom Frame: Styled Text Area for Chatbot Response
# ----------------------------
bottom_frame = Frame(root, width=800, height=200, bg="#2c3e50")
bottom_frame.pack_propagate(False)
bottom_frame.pack(side="bottom", fill="x")

text_area = Text(bottom_frame, wrap="word", font=("Helvetica", 16),
                 bg="#ecf0f1", fg="#2c3e50", bd=0, highlightthickness=0)
text_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

scrollbar = Scrollbar(bottom_frame, command=text_area.yview)
scrollbar.pack(side="right", fill="y")
text_area.config(yscrollcommand=scrollbar.set)

# ----------------------------
# Control: Button to Trigger Voice Recording
# ----------------------------
record_button = tk.Button(bottom_frame, text="Start Recording", font=("Helvetica", 14),
                          command=trigger_recording, bg="#2980b9", fg="white", bd=0, relief="raised", padx=10, pady=5)
record_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

# Bind the space key (both left and right) to trigger recording
root.bind("<space>", trigger_recording)


# Run the Tkinter event loop
root.mainloop()
