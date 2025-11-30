import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NeuroScanAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧠 NeuroScanAI")
        self.geometry("900x700")

        # HEADER
        self.label = ctk.CTkLabel(self, text="🧠 NeuroScanAI", font=(
            "Orbitron", 30, "bold"), text_color="#89f0ff")
        self.label.pack(pady=20)

        # PANEL FRAME
        self.panel = ctk.CTkFrame(
            self, corner_radius=20, fg_color="#101624", border_width=2, border_color="#00ffff")
        self.panel.pack(padx=40, pady=10, fill="both", expand=True)

        # CONTENTS
        self.scan_type = ctk.StringVar(value="Select Scan Type")
        self.dropdown = ctk.CTkOptionMenu(self.panel, variable=self.scan_type,
                                          values=["MRI", "fMRI", "PET", "CT"])
        self.dropdown.pack(pady=20)

        self.upload_btn = ctk.CTkButton(
            self.panel, text="📁 Upload Scan", command=self.upload_scan)
        self.upload_btn.pack(pady=10)

        self.analyze_btn = ctk.CTkButton(
            self.panel, text="🔍 Analyze Scan", command=self.start_scan_animation)
        self.analyze_btn.pack(pady=10)

        self.quiz_btn = ctk.CTkButton(
            self.panel, text="🧩 Take Patient Quiz", command=self.open_quiz)
        self.quiz_btn.pack(pady=10)

        # OUTPUT
        self.output_box = ctk.CTkTextbox(
            self.panel, width=600, height=200, fg_color="#0b111d", border_width=0)
        self.output_box.pack(pady=20)

        # ANIMATION BAR
        self.progress = ttk.Progressbar(
            self.panel, length=400, mode='determinate')
        self.progress.pack(pady=10)

    # --- Upload Scan ---
    def upload_scan(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.nii *.dcm")])
        if file_path:
            self.output_box.insert("end", f"🩻 Scan uploaded: {file_path}\n")

    # --- Scan Animation ---
    def start_scan_animation(self):
        if self.scan_type.get() == "Select Scan Type":
            messagebox.showerror("Error", "Please select a scan type first.")
            return
        self.output_box.insert(
            "end", f"🔍 Scanning {self.scan_type.get()} data...\n")
        threading.Thread(target=self.animate_scan).start()

    def animate_scan(self):
        self.progress["value"] = 0
        for i in range(100):
            time.sleep(0.05)
            self.progress["value"] = i + 1
            self.progress.update_idletasks()
        time.sleep(0.5)
        self.output_box.insert(
            "end", "✨ Scan complete! No major neurodegenerative patterns detected.\n")

    # --- Quiz Popup ---
    def open_quiz(self):
        quiz = ctk.CTkToplevel(self)
        quiz.title("Patient Quiz")
        quiz.geometry("400x650")
        quiz.configure(fg_color="#111822")

        ctk.CTkLabel(quiz, text="🧬 Patient Information", font=(
            "Orbitron", 20, "bold"), text_color="#89f0ff").pack(pady=10)

        # Inputs
        name = ctk.CTkEntry(quiz, placeholder_text="Full Name")
        name.pack(pady=5)

        age = ctk.CTkEntry(quiz, placeholder_text="Age")
        age.pack(pady=5)

        gender = ctk.CTkOptionMenu(quiz, values=["Male", "Female", "Other"])
        gender.pack(pady=5)

        ctk.CTkLabel(quiz, text="Is there any family history of disease?", font=(
            "Helvetica", 14, "bold")).pack(pady=10)

        family_history = ctk.StringVar(value="Select")
        family_dropdown = ctk.CTkOptionMenu(quiz, variable=family_history,
                                            values=["Yes", "No", "Not Sure"])
        family_dropdown.pack(pady=5)

        # Hidden entry for disease details (appears if 'Yes' selected)
        disease_entry = ctk.CTkEntry(
            quiz, placeholder_text="Specify disease(s)")
        disease_entry.pack_forget()  # hidden by default

        def show_disease_entry(choice):
            if choice == "Yes":
                disease_entry.pack(pady=5)
            else:
                disease_entry.pack_forget()

        family_history.trace(
            "w", lambda *args: show_disease_entry(family_history.get()))

        # Symptoms
        ctk.CTkLabel(quiz, text="Select any symptoms:",
                     font=("Helvetica", 14, "bold")).pack(pady=10)
        symptoms = ["Memory loss", "Tremors", "Mood swings",
                    "Difficulty walking", "Speech issues", "Confusion"]
        symptom_vars = [ctk.BooleanVar() for _ in symptoms]
        for i, s in enumerate(symptoms):
            ctk.CTkCheckBox(quiz, text=s, variable=symptom_vars[i]).pack(
                anchor="w", padx=40)

        # Submit
        def submit_quiz():
            fam = family_history.get()
            result = {
                "Name": name.get(),
                "Age": age.get(),
                "Gender": gender.get(),
                "Family History": fam,
                "Diseases": disease_entry.get() if fam == "Yes" else "None",
                "Symptoms": [symptoms[i] for i, var in enumerate(symptom_vars) if var.get()]
            }
            summary = f"✅ Quiz Submitted for {result['Name']}\n\n"
            summary += f"Age: {result['Age']}\nGender: {result['Gender']}\n"
            summary += f"Family History: {result['Family History']}\n"
            if fam == "Yes":
                summary += f"Reported Disease(s): {result['Diseases']}\n"
            summary += f"Symptoms: {', '.join(result['Symptoms']) if result['Symptoms'] else 'None'}\n"
            messagebox.showinfo("Quiz Summary", summary)
            quiz.destroy()

        ctk.CTkButton(quiz, text="Submit", command=submit_quiz).pack(pady=20)


# --- RUN APP ---
if __name__ == "__main__":
    app = NeuroScanAI()
    app.mainloop()
