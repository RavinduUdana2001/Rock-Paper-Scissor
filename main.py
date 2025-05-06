# --- main.py ---
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import numpy as np
import pygame
from gesture_recognition import HandGesture
from game_logic import Game, GameState
import time

class RPSLSGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors Lizard Spock")
        self.root.geometry("1280x720")
        self.root.configure(bg="#1e272e")

        pygame.mixer.init()
        self.sounds = {
            "start": pygame.mixer.Sound("sounds/start.wav"),
            "win": pygame.mixer.Sound("sounds/win.wav"),
            "lose": pygame.mixer.Sound("sounds/lose.wav"),
            "tie": pygame.mixer.Sound("sounds/tie.wav")
        }

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.detector = HandGesture()
        self.game = Game()

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#1e272e')
        self.style.configure('TLabel', background='#1e272e', foreground='#ecf0f1')
        self.style.configure('Title.TLabel', font=('Helvetica', 30, 'bold'), foreground='#00cec9')
        self.style.configure('Score.TLabel', font=('Helvetica', 20), foreground='#dff9fb')
        self.style.configure('Result.TLabel', font=('Helvetica', 24, 'bold'), foreground='#ffeaa7')
        self.style.configure('Countdown.TLabel', font=('Helvetica', 72, 'bold'), foreground='#ff7675')
        self.style.configure('TButton', font=('Helvetica', 16, 'bold'), padding=10)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(pady=10)

        self.score_label = ttk.Label(self.top_frame, text="You: 0  |  Computer: 0 | Round: 0/5", style='Score.TLabel')
        self.score_label.pack()

        self.middle_frame = ttk.Frame(self.main_frame)
        self.middle_frame.pack(expand=True, fill=tk.BOTH)

        self.computer_frame = ttk.Frame(self.middle_frame, width=400)
        self.computer_frame.pack(side=tk.LEFT, expand=True, padx=10, pady=10)

        self.computer_title = ttk.Label(self.computer_frame, text="Computer", style='Title.TLabel')
        self.computer_title.pack(pady=10)
        self.computer_gesture_img = tk.Label(self.computer_frame, bg='#1e272e')
        self.computer_gesture_img.pack()

        self.player_frame = ttk.Frame(self.middle_frame, width=400)
        self.player_frame.pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

        self.player_title = ttk.Label(self.player_frame, text="You", style='Title.TLabel')
        self.player_title.pack(pady=10)
        self.video_label = tk.Label(self.player_frame, bg='#1e272e')
        self.video_label.pack()

        self.countdown_label = ttk.Label(self.main_frame, text="", style='Countdown.TLabel')
        self.countdown_label.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

        self.result_label = ttk.Label(self.main_frame, text="Press ▶ Start to begin!", style='Result.TLabel')
        self.result_label.pack(pady=10)

        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(side=tk.BOTTOM, pady=15)

        self.start_button = ttk.Button(self.bottom_frame, text="▶ Start Game", command=self.start_game)
        self.start_button.grid(row=0, column=0, padx=20, pady=10)

        self.play_again_button = ttk.Button(self.bottom_frame, text="↻ Play Again", command=self.play_again, state=tk.DISABLED)
        self.play_again_button.grid(row=0, column=1, padx=20, pady=10)

        self.init_gesture_displays()

    def init_gesture_displays(self):
        blank_img = Image.new('RGB', (400, 300), color='#1e272e')
        draw = ImageDraw.Draw(blank_img)
        try:
            fnt = ImageFont.truetype("arial.ttf", 24)
        except:
            fnt = ImageFont.load_default()
        draw.text((200, 150), "Waiting...", fill="white", font=fnt, anchor="mm")
        img_tk = ImageTk.PhotoImage(blank_img)
        self.computer_gesture_img.config(image=img_tk)
        self.computer_gesture_img.image = img_tk
        self.video_label.config(image=img_tk)
        self.video_label.image = img_tk

    def start_game(self):
        self.sounds['start'].play()
        self.game.start_new_game()
        self.start_button.config(state=tk.DISABLED)
        self.play_again_button.config(state=tk.DISABLED)
        self.update_score_display()
        self.result_label.config(text="Get ready for round 1!")
        self.start_new_round()

    def play_again(self):
        self.start_game()

    def start_new_round(self):
        if self.game.start_new_round():
            self.animate_countdown()
        else:
            self.show_final_result()

    def animate_countdown(self):
        if self.game.state == GameState.COUNTDOWN:
            countdown_text = self.game.update_countdown()
            self.countdown_label.config(text=countdown_text)
            if countdown_text == "Shoot!":
                self.root.after(1000, self.show_gestures)
            else:
                self.root.after(1000, self.animate_countdown)

    def show_gestures(self):
        self.countdown_label.config(text="")
        self.game.state = GameState.SHOW_GESTURES
        self.result_label.config(text="Show your gesture now!")

    def update_score_display(self):
        self.score_label.config(
            text=f"You: {self.game.user_score}  |  Computer: {self.game.computer_score} | Round: {self.game.round}/{self.game.max_rounds}"
        )

    def update_computer_display(self, gesture):
        img = Image.new('RGB', (400, 300), color='#1e272e')
        draw = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype("arial.ttf", 36)
        except:
            fnt = ImageFont.load_default()

        draw.text((200, 50), gesture, fill="white", font=fnt, anchor="mm")

        if gesture == "Rock":
            draw.ellipse([(100, 100), (300, 300)], fill="#95a5a6")
        elif gesture == "Paper":
            draw.rectangle([(100, 100), (300, 300)], fill="#3498db")
        elif gesture == "Scissors":
            draw.polygon([(100, 300), (200, 100), (300, 300)], fill="#e74c3c")
        elif gesture == "Lizard":
            draw.ellipse([(150, 100), (250, 200)], fill="#2ecc71")
            draw.ellipse([(100, 150), (300, 250)], fill="#2ecc71")
        elif gesture == "Spock":
            draw.polygon([(200, 100), (100, 200), (200, 300), (300, 200)], fill="#9b59b6")

        img_tk = ImageTk.PhotoImage(img)
        self.computer_gesture_img.config(image=img_tk)
        self.computer_gesture_img.image = img_tk

    def show_final_result(self):
        if self.game.user_score > self.game.computer_score:
            final_text = "🎉 You Win the Game!"
            self.sounds['win'].play()
        elif self.game.user_score < self.game.computer_score:
            final_text = "💻 Computer Wins!"
            self.sounds['lose'].play()
        else:
            final_text = "🤝 It's a Tie!"
            self.sounds['tie'].play()

        self.result_label.config(text=final_text)
        self.play_again_button.config(state=tk.NORMAL)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)

        if self.game.state in [GameState.WAITING, GameState.COUNTDOWN]:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb).resize((400, 300), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=img_tk)
            self.video_label.image = img_tk

        elif self.game.state == GameState.SHOW_GESTURES:
            processed_frame, user_gesture = self.detector.detect_gesture(frame)
            if self.game.user_choice is None:
                self.game.set_user_choice(user_gesture)
                self.update_computer_display(self.game.computer_choice)
                self.result_label.config(text=self.game.result)
                self.update_score_display()

                rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb).resize((400, 300), Image.LANCZOS)
                draw = ImageDraw.Draw(img)
                try:
                    fnt = ImageFont.truetype("arial.ttf", 18)
                except:
                    fnt = ImageFont.load_default()
                draw.text((200, 30), f"You showed: {user_gesture}", fill="white", font=fnt, anchor="mt")
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_label.config(image=img_tk)
                self.video_label.image = img_tk

                if self.game.is_game_over():
                    self.show_final_result()
                else:
                    self.root.after(3000, self.start_new_round)

        self.root.after(30, self.update_frame)

    def on_closing(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RPSLSGame(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()