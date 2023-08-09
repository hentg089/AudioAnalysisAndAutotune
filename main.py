import os
import pyaudio
import wave
import time
import threading
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import os
import pygame
from tkinter import PhotoImage

#allows us to play sound
pygame.mixer.init()

class VoiceRecorder:
    def __init__(self):
        #init our window and our thing
        self.root = tk.Tk()
        self.fig, self.ax = plt.subplots()

        #set plot characteristic
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Signal Wave')
        self.ax.set_title('Audio Signal')

        #some window features: dimensions and resizable
        self.root.state("zoomed")
        self.root.resizable(False, False)

        #draw our plot on the window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill='both')

        #draw our tklabel
        self.label = tk.Label(text="00:00:00", font=("Arial", 15, "bold"))
        self.label.pack()

        #draw our record button
        self.button_record = tk.Button(text="   Record  ", font=("Arial", 30, "bold"),
                                command=self.click_handler)
        self.button_record.pack(side='left', expand=True, fill='both')


        #draw our select audio button
        self.button_file_select = tk.Button(text="Select File", font=("Arial",30,"bold"),
                                command=self.select_file_handler)
        self.button_file_select.pack(side='left', expand=True, fill='both')
        self.file = ""



        self.recording = False
        self.root.mainloop()

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button_record.config(fg="black")
        else:
            #redraw our graph
            self.ax.clear()
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Signal Wave')
            self.ax.set_title('Audio Signal')
            self.canvas.draw()

            #update our recording state and change button color
            self.recording = True
            self.button_record.config(fg="red")

            #start a seperate threaf for recording in the record method
            threading.Thread(target=self.record).start()

    def select_file_handler(self):
        def _open_dialog():
            self.file = filedialog.askopenfilename(
                title='Select a file',
                filetypes=[(".wav", '*.wav')]
            )
            self.get_plot(self.file)

        threading.Thread(target = _open_dialog).start();


    def record(self):
        #starting our audio stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        frames = []

        start = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)

            passed = time.time() - start
            secs = passed % 60
            mins = passed // 60
            hours = mins // 60
            self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")

        stream.stop_stream()
        stream.close()
        audio.terminate()


        sound_file = wave.open(f"recording.wav", "wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b"".join(frames))
        sound_file.close()

        #all the overall code does is record and then save the recording the the recording wav
        self.get_plot()


    def get_plot(self, recording_name = "recording.wav"):
        obj = wave.open(recording_name, "rb")

        sample_freq = obj.getframerate()
        n_samples = obj.getnframes()
        signal_wave = obj.readframes(-1)

        obj.close()

        #audio length
        t_audio = n_samples / sample_freq

        #np array
        signal_array = np.frombuffer(signal_wave, dtype=np.int16)
        times = np.linspace(0, t_audio, num=n_samples)

        self.ax.plot(times, signal_array, 'b-')
        self.canvas.draw()


VoiceRecorder()