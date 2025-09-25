#!/usr/bin/env python3
"""
AI-Powered Interview Trick Question Trainer

A comprehensive Tkinter-based application for practicing technical interview trick questions
in Java and Python. Features persistent storage, scoring, progress tracking, and question management.

Author: AI Assistant
Date: 2024-09-25
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading


class QuestionDatabase:
    """Manages the trick questions database with JSON persistence."""
    
    def __init__(self, db_path: str = "trick_questions_db.json"):
        self.db_path = db_path
        self.data = self._load_database()
        
    def _load_database(self) -> Dict:
        """Load questions database from JSON file."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_database()
        except Exception as e:
            print(f"Error loading database: {e}")
            return self._create_default_database()
    
    def _create_default_database(self) -> Dict:
        """Create a minimal default database structure."""
        return {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_questions": 0,
                "description": "AI Interview Trick Question Database"
            },
            "questions": [],
            "user_stats": {
                "total_attempts": 0,
                "correct_answers": 0,
                "session_history": [],
                "best_streak": 0,
                "language_stats": {
                    "Python": {"attempted": 0, "correct": 0},
                    "Java": {"attempted": 0, "correct": 0}
                },
                "difficulty_stats": {
                    "Easy": {"attempted": 0, "correct": 0},
                    "Medium": {"attempted": 0, "correct": 0},
                    "Hard": {"attempted": 0, "correct": 0}
                }
            }
        }
    
    def save_database(self):
        """Save database to JSON file."""
        try:
            self.data["metadata"]["last_updated"] = datetime.now().isoformat()
            self.data["metadata"]["total_questions"] = len(self.data["questions"])
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def get_questions(self, language: str = None, difficulty: str = None) -> List[Dict]:
        """Get filtered questions based on criteria."""
        questions = self.data.get("questions", [])
        
        if language:
            questions = [q for q in questions if q.get("language", "").lower() == language.lower()]
        
        if difficulty:
            questions = [q for q in questions if q.get("difficulty", "").lower() == difficulty.lower()]
        
        return questions
    
    def add_question(self, question_data: Dict):
        """Add a new question to the database."""
        # Generate new ID
        existing_ids = [q.get("id", 0) for q in self.data["questions"]]
        new_id = max(existing_ids, default=0) + 1
        question_data["id"] = new_id
        
        self.data["questions"].append(question_data)
        self.save_database()
    
    def update_stats(self, language: str, difficulty: str, correct: bool):
        """Update user statistics after answering a question."""
        stats = self.data["user_stats"]
        
        stats["total_attempts"] += 1
        if correct:
            stats["correct_answers"] += 1
        
        # Update language stats
        if language in stats["language_stats"]:
            stats["language_stats"][language]["attempted"] += 1
            if correct:
                stats["language_stats"][language]["correct"] += 1
        
        # Update difficulty stats
        if difficulty in stats["difficulty_stats"]:
            stats["difficulty_stats"][difficulty]["attempted"] += 1
            if correct:
                stats["difficulty_stats"][difficulty]["correct"] += 1
        
        self.save_database()
    
    def get_stats(self) -> Dict:
        """Get current user statistics."""
        return self.data.get("user_stats", {})


class ProgressVisualizer:
    """Handles progress visualization using Tkinter Canvas (matplotlib alternative)."""
    
    def __init__(self, parent):
        self.parent = parent
        
    def create_progress_chart(self, stats: Dict) -> tk.Toplevel:
        """Create a progress visualization window using Tkinter Canvas."""
        chart_window = tk.Toplevel(self.parent)
        chart_window.title("Progress Chart")
        chart_window.geometry("600x400")
        
        # Create canvas
        canvas = tk.Canvas(chart_window, width=580, height=350, bg='white')
        canvas.pack(pady=10)
        
        # Get data
        total_attempts = stats.get("total_attempts", 0)
        correct_answers = stats.get("correct_answers", 0)
        
        if total_attempts == 0:
            canvas.create_text(290, 175, text="No data available yet", 
                             font=("Arial", 14), fill="gray")
            return chart_window
        
        # Calculate accuracy
        accuracy = (correct_answers / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Draw accuracy bar chart
        self._draw_accuracy_chart(canvas, stats)
        
        # Draw language breakdown
        self._draw_language_breakdown(canvas, stats)
        
        return chart_window
    
    def _draw_accuracy_chart(self, canvas: tk.Canvas, stats: Dict):
        """Draw accuracy chart on canvas."""
        # Title
        canvas.create_text(145, 30, text="Overall Accuracy", font=("Arial", 12, "bold"))
        
        total_attempts = stats.get("total_attempts", 0)
        correct_answers = stats.get("correct_answers", 0)
        accuracy = (correct_answers / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Draw bar
        bar_width = 200
        bar_height = 30
        x_start = 50
        y_start = 50
        
        # Background bar
        canvas.create_rectangle(x_start, y_start, x_start + bar_width, y_start + bar_height,
                              fill="lightgray", outline="black")
        
        # Accuracy bar
        accuracy_width = (accuracy / 100) * bar_width
        color = "green" if accuracy >= 70 else "orange" if accuracy >= 50 else "red"
        canvas.create_rectangle(x_start, y_start, x_start + accuracy_width, y_start + bar_height,
                              fill=color, outline="black")
        
        # Text
        canvas.create_text(x_start + bar_width/2, y_start + bar_height/2,
                         text=f"{accuracy:.1f}%", font=("Arial", 10, "bold"))
        
        # Stats text
        canvas.create_text(x_start, y_start + bar_height + 20,
                         text=f"Correct: {correct_answers}/{total_attempts}",
                         font=("Arial", 10), anchor="w")
    
    def _draw_language_breakdown(self, canvas: tk.Canvas, stats: Dict):
        """Draw language performance breakdown."""
        canvas.create_text(145, 130, text="Language Performance", font=("Arial", 12, "bold"))
        
        lang_stats = stats.get("language_stats", {})
        y_pos = 160
        
        for lang, data in lang_stats.items():
            attempted = data.get("attempted", 0)
            correct = data.get("correct", 0)
            
            if attempted > 0:
                accuracy = (correct / attempted) * 100
                canvas.create_text(50, y_pos, text=f"{lang}:", font=("Arial", 10, "bold"), anchor="w")
                canvas.create_text(120, y_pos, text=f"{accuracy:.1f}% ({correct}/{attempted})",
                                 font=("Arial", 10), anchor="w")
                y_pos += 25


class AddQuestionDialog:
    """Dialog for adding new questions to the database."""
    
    def __init__(self, parent, database: QuestionDatabase):
        self.parent = parent
        self.database = database
        self.result = None
        self.dialog = None
        
    def show(self) -> Optional[Dict]:
        """Show the add question dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add New Question")
        self.dialog.geometry("600x500")
        self.dialog.grab_set()  # Modal dialog
        
        # Create form
        self._create_form()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_form(self):
        """Create the question input form."""
        # Language selection
        tk.Label(self.dialog, text="Language:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.language_var = tk.StringVar(value="Python")
        lang_frame = tk.Frame(self.dialog)
        lang_frame.pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(lang_frame, text="Python", variable=self.language_var, value="Python").pack(side="left")
        tk.Radiobutton(lang_frame, text="Java", variable=self.language_var, value="Java").pack(side="left")
        
        # Difficulty selection
        tk.Label(self.dialog, text="Difficulty:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.difficulty_var = tk.StringVar(value="Medium")
        diff_frame = tk.Frame(self.dialog)
        diff_frame.pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(diff_frame, text="Easy", variable=self.difficulty_var, value="Easy").pack(side="left")
        tk.Radiobutton(diff_frame, text="Medium", variable=self.difficulty_var, value="Medium").pack(side="left")
        tk.Radiobutton(diff_frame, text="Hard", variable=self.difficulty_var, value="Hard").pack(side="left")
        
        # Category
        tk.Label(self.dialog, text="Category:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.category_entry = tk.Entry(self.dialog, width=50)
        self.category_entry.pack(anchor="w", padx=10, pady=5)
        
        # Question text
        tk.Label(self.dialog, text="Question:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.question_text = scrolledtext.ScrolledText(self.dialog, height=6, width=70)
        self.question_text.pack(padx=10, pady=5)
        
        # Options
        tk.Label(self.dialog, text="Answer Options:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.option_entries = []
        for i in range(4):
            frame = tk.Frame(self.dialog)
            frame.pack(anchor="w", padx=10, pady=2)
            tk.Label(frame, text=f"{i+1}:").pack(side="left")
            entry = tk.Entry(frame, width=60)
            entry.pack(side="left", padx=5)
            self.option_entries.append(entry)
        
        # Correct answer
        tk.Label(self.dialog, text="Correct Answer (1-4):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.correct_var = tk.StringVar(value="1")
        correct_frame = tk.Frame(self.dialog)
        correct_frame.pack(anchor="w", padx=10, pady=5)
        for i in range(4):
            tk.Radiobutton(correct_frame, text=str(i+1), variable=self.correct_var, value=str(i)).pack(side="left")
        
        # Explanation
        tk.Label(self.dialog, text="Explanation:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.explanation_text = scrolledtext.ScrolledText(self.dialog, height=3, width=70)
        self.explanation_text.pack(padx=10, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Question", command=self._add_question, 
                 bg="green", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side="left", padx=5)
    
    def _add_question(self):
        """Add the question to the database."""
        # Validate inputs
        question = self.question_text.get(1.0, tk.END).strip()
        if not question:
            messagebox.showerror("Error", "Please enter a question")
            return
        
        options = [entry.get().strip() for entry in self.option_entries]
        if not all(options):
            messagebox.showerror("Error", "Please fill all answer options")
            return
        
        explanation = self.explanation_text.get(1.0, tk.END).strip()
        if not explanation:
            messagebox.showerror("Error", "Please enter an explanation")
            return
        
        # Create question data
        question_data = {
            "language": self.language_var.get(),
            "difficulty": self.difficulty_var.get(),
            "category": self.category_entry.get().strip() or "General",
            "question": question,
            "options": options,
            "correct_answer": int(self.correct_var.get()),
            "explanation": explanation,
            "tags": ["custom", "user-added"]
        }
        
        # Add to database
        self.database.add_question(question_data)
        self.result = question_data
        
        messagebox.showinfo("Success", "Question added successfully!")
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class InterviewTrainerApp:
    """Main application class for the AI Interview Trick Question Trainer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Interview Trick Question Trainer")
        self.root.geometry("900x700")
        
        # Initialize database
        self.database = QuestionDatabase()
        self.progress_visualizer = ProgressVisualizer(self.root)
        
        # Current session variables
        self.current_question = None
        self.current_session = []
        self.session_start_time = None
        self.question_start_time = None
        self.timer_active = False
        self.time_limit = 300  # 5 minutes default
        
        # Setup UI
        self._setup_ui()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Setup the main user interface."""
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🤖 AI Interview Trick Question Trainer", 
                              font=("Arial", 16, "bold"), fg="blue")
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Master Java & Python Interview Questions", 
                                font=("Arial", 12), fg="gray")
        subtitle_label.pack()
        
        # Control panel
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language selection
        lang_frame = tk.LabelFrame(control_frame, text="Language", font=("Arial", 10, "bold"))
        lang_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.language_var = tk.StringVar(value="All")
        tk.Radiobutton(lang_frame, text="All", variable=self.language_var, value="All").pack(anchor="w")
        tk.Radiobutton(lang_frame, text="Python", variable=self.language_var, value="Python").pack(anchor="w")
        tk.Radiobutton(lang_frame, text="Java", variable=self.language_var, value="Java").pack(anchor="w")
        
        # Difficulty selection
        diff_frame = tk.LabelFrame(control_frame, text="Difficulty", font=("Arial", 10, "bold"))
        diff_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.difficulty_var = tk.StringVar(value="All")
        tk.Radiobutton(diff_frame, text="All", variable=self.difficulty_var, value="All").pack(anchor="w")
        tk.Radiobutton(diff_frame, text="Easy", variable=self.difficulty_var, value="Easy").pack(anchor="w")
        tk.Radiobutton(diff_frame, text="Medium", variable=self.difficulty_var, value="Medium").pack(anchor="w")
        tk.Radiobutton(diff_frame, text="Hard", variable=self.difficulty_var, value="Hard").pack(anchor="w")
        
        # Timer settings
        timer_frame = tk.LabelFrame(control_frame, text="Timer (seconds)", font=("Arial", 10, "bold"))
        timer_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.timer_var = tk.StringVar(value="300")
        timer_options = ["60", "120", "300", "600", "No Limit"]
        self.timer_combo = ttk.Combobox(timer_frame, textvariable=self.timer_var, 
                                       values=timer_options, width=10)
        self.timer_combo.pack(pady=5)
        
        # Action buttons
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="🎯 Start Session", command=self._start_session,
                 bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=2)
        tk.Button(btn_frame, text="📊 View Progress", command=self._show_progress,
                 bg="blue", fg="white", font=("Arial", 10, "bold")).pack(pady=2)
        tk.Button(btn_frame, text="➕ Add Question", command=self._add_question,
                 bg="orange", fg="white", font=("Arial", 10, "bold")).pack(pady=2)
        
        # Question display area
        self.question_frame = tk.LabelFrame(main_frame, text="Current Question", 
                                          font=("Arial", 12, "bold"))
        self.question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Timer display
        self.timer_label = tk.Label(self.question_frame, text="", font=("Arial", 14, "bold"), fg="red")
        self.timer_label.pack(pady=5)
        
        # Question text
        self.question_text = scrolledtext.ScrolledText(self.question_frame, height=8, 
                                                      font=("Courier", 11), state=tk.DISABLED)
        self.question_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Answer options
        self.answer_frame = tk.Frame(self.question_frame)
        self.answer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.answer_var = tk.StringVar()
        self.answer_buttons = []
        
        # Control buttons
        control_btn_frame = tk.Frame(self.question_frame)
        control_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.submit_btn = tk.Button(control_btn_frame, text="Submit Answer", 
                                   command=self._submit_answer, state=tk.DISABLED,
                                   bg="darkgreen", fg="white", font=("Arial", 11, "bold"))
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_btn = tk.Button(control_btn_frame, text="Next Question", 
                                 command=self._next_question, state=tk.DISABLED,
                                 bg="darkblue", fg="white", font=("Arial", 11, "bold"))
        self.next_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.explanation_btn = tk.Button(control_btn_frame, text="Show Explanation", 
                                        command=self._show_explanation, state=tk.DISABLED,
                                        bg="purple", fg="white", font=("Arial", 11, "bold"))
        self.explanation_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Ready to start", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _load_initial_data(self):
        """Load initial data and display statistics."""
        stats = self.database.get_stats()
        total_questions = len(self.database.data.get("questions", []))
        
        status_text = f"Ready | {total_questions} questions available | "
        status_text += f"Your stats: {stats.get('correct_answers', 0)}/{stats.get('total_attempts', 0)} correct"
        
        self.status_bar.config(text=status_text)
        
        # Display welcome message
        welcome_text = """
🎯 Welcome to AI Interview Trick Question Trainer!

Instructions:
• Select your preferred language and difficulty level
• Set a timer for added pressure (pose mode)
• Click 'Start Session' to begin practicing
• Answer questions and learn from explanations
• Track your progress over time

Features:
✓ 20 carefully curated trick questions
✓ Timed practice sessions
✓ Detailed explanations for each question  
✓ Progress tracking and statistics
✓ Add your own custom questions
✓ Language-specific filtering (Java/Python)

Ready to master those tricky interview questions? 🚀
        """
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, welcome_text)
        self.question_text.config(state=tk.DISABLED)
    
    def _start_session(self):
        """Start a new practice session."""
        # Get filtered questions
        language = None if self.language_var.get() == "All" else self.language_var.get()
        difficulty = None if self.difficulty_var.get() == "All" else self.difficulty_var.get()
        
        questions = self.database.get_questions(language, difficulty)
        
        if not questions:
            messagebox.showwarning("No Questions", "No questions available for the selected criteria.")
            return
        
        # Initialize session
        self.current_session = random.sample(questions, min(len(questions), 10))  # Max 10 questions per session
        self.session_start_time = time.time()
        
        # Setup timer
        timer_value = self.timer_var.get()
        if timer_value != "No Limit":
            self.time_limit = int(timer_value)
            self.timer_active = True
        else:
            self.timer_active = False
        
        # Load first question
        self._load_question(0)
        
        self.status_bar.config(text=f"Session started: {len(self.current_session)} questions")
    
    def _load_question(self, index: int):
        """Load a specific question from the current session."""
        if index >= len(self.current_session):
            self._end_session()
            return
        
        self.current_question = self.current_session[index]
        self.question_start_time = time.time()
        
        # Update question display
        question_info = f"Question {index + 1}/{len(self.current_session)}\n"
        question_info += f"Language: {self.current_question['language']} | "
        question_info += f"Difficulty: {self.current_question['difficulty']} | "
        question_info += f"Category: {self.current_question['category']}\n\n"
        question_info += self.current_question['question']
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, question_info)
        self.question_text.config(state=tk.DISABLED)
        
        # Clear previous answer options
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        self.answer_buttons.clear()
        
        # Create answer options
        self.answer_var.set("")
        for i, option in enumerate(self.current_question['options']):
            btn = tk.Radiobutton(self.answer_frame, text=f"{i+1}. {option}", 
                               variable=self.answer_var, value=str(i),
                               font=("Arial", 10), wraplength=600, justify="left")
            btn.pack(anchor="w", pady=2)
            self.answer_buttons.append(btn)
        
        # Enable submit button
        self.submit_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.DISABLED)
        self.explanation_btn.config(state=tk.DISABLED)
        
        # Start timer if active
        if self.timer_active:
            self._update_timer()
    
    def _update_timer(self):
        """Update the countdown timer."""
        if not self.timer_active or not self.question_start_time:
            return
        
        elapsed = time.time() - self.question_start_time
        remaining = max(0, self.time_limit - elapsed)
        
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            self.timer_label.config(text=f"⏰ Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self._update_timer)
        else:
            self.timer_label.config(text="⏰ Time's Up!")
            self._submit_answer()  # Auto-submit when time runs out
    
    def _submit_answer(self):
        """Submit the current answer."""
        if not self.current_question:
            return
        
        selected_answer = self.answer_var.get()
        if not selected_answer and self.timer_active:
            # Time ran out, treat as incorrect
            selected_answer = "-1"
        elif not selected_answer:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return
        
        # Check correctness
        correct_answer = self.current_question['correct_answer']
        is_correct = selected_answer == str(correct_answer)
        
        # Update statistics
        self.database.update_stats(
            self.current_question['language'],
            self.current_question['difficulty'],
            is_correct
        )
        
        # Show result
        if is_correct:
            result_msg = "✅ Correct!"
            self.timer_label.config(text=result_msg, fg="green")
        else:
            correct_text = self.current_question['options'][correct_answer]
            result_msg = f"❌ Incorrect. Correct answer: {correct_answer + 1}. {correct_text}"
            self.timer_label.config(text=result_msg, fg="red")
        
        # Disable submit, enable next and explanation
        self.submit_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.explanation_btn.config(state=tk.NORMAL)
        
        # Stop timer
        self.timer_active = False
    
    def _show_explanation(self):
        """Show the explanation for the current question."""
        if not self.current_question:
            return
        
        explanation_window = tk.Toplevel(self.root)
        explanation_window.title("Explanation")
        explanation_window.geometry("500x300")
        
        # Question info
        info_label = tk.Label(explanation_window, 
                            text=f"Question: {self.current_question['category']} ({self.current_question['difficulty']})",
                            font=("Arial", 12, "bold"))
        info_label.pack(pady=10)
        
        # Explanation text
        explanation_text = scrolledtext.ScrolledText(explanation_window, height=10, 
                                                   font=("Arial", 11), wrap=tk.WORD)
        explanation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        explanation_content = f"Correct Answer: {self.current_question['correct_answer'] + 1}. "
        explanation_content += f"{self.current_question['options'][self.current_question['correct_answer']]}\n\n"
        explanation_content += f"Explanation:\n{self.current_question['explanation']}\n\n"
        
        if 'tags' in self.current_question:
            explanation_content += f"Tags: {', '.join(self.current_question['tags'])}"
        
        explanation_text.insert(1.0, explanation_content)
        explanation_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(explanation_window, text="Close", command=explanation_window.destroy,
                            bg="gray", fg="white", font=("Arial", 10, "bold"))
        close_btn.pack(pady=10)
    
    def _next_question(self):
        """Load the next question in the session."""
        if not self.current_session:
            return
        
        # Find current question index
        current_index = 0
        for i, q in enumerate(self.current_session):
            if q['id'] == self.current_question['id']:
                current_index = i
                break
        
        # Load next question
        self._load_question(current_index + 1)
    
    def _end_session(self):
        """End the current practice session."""
        if not self.current_session:
            return
        
        session_time = time.time() - self.session_start_time if self.session_start_time else 0
        
        # Show session summary
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Session Complete!")
        summary_window.geometry("400x250")
        
        tk.Label(summary_window, text="🎉 Session Complete!", 
                font=("Arial", 16, "bold"), fg="green").pack(pady=10)
        
        # Calculate session stats
        stats = self.database.get_stats()
        
        summary_text = f"Questions Answered: {len(self.current_session)}\n"
        summary_text += f"Session Time: {int(session_time // 60)}:{int(session_time % 60):02d}\n\n"
        summary_text += f"Overall Performance:\n"
        summary_text += f"Total Correct: {stats.get('correct_answers', 0)}\n"
        summary_text += f"Total Attempted: {stats.get('total_attempts', 0)}\n"
        
        if stats.get('total_attempts', 0) > 0:
            accuracy = (stats.get('correct_answers', 0) / stats.get('total_attempts', 0)) * 100
            summary_text += f"Overall Accuracy: {accuracy:.1f}%"
        
        tk.Label(summary_window, text=summary_text, font=("Arial", 11), justify="left").pack(pady=10)
        
        tk.Button(summary_window, text="Close", command=summary_window.destroy,
                 bg="blue", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
        
        # Reset session
        self.current_session = []
        self.current_question = None
        self.timer_active = False
        self.timer_label.config(text="")
        
        # Reload initial screen
        self._load_initial_data()
        
        # Disable buttons
        self.submit_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.explanation_btn.config(state=tk.DISABLED)
    
    def _show_progress(self):
        """Show progress visualization."""
        stats = self.database.get_stats()
        self.progress_visualizer.create_progress_chart(stats)
    
    def _add_question(self):
        """Show add question dialog."""
        dialog = AddQuestionDialog(self.root, self.database)
        result = dialog.show()
        
        if result:
            # Update status bar
            total_questions = len(self.database.data.get("questions", []))
            stats = self.database.get_stats()
            status_text = f"Question added! | {total_questions} questions available | "
            status_text += f"Your stats: {stats.get('correct_answers', 0)}/{stats.get('total_attempts', 0)} correct"
            self.status_bar.config(text=status_text)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create and run the application
    app = InterviewTrainerApp()
    app.run()


if __name__ == "__main__":
    main()