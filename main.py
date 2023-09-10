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
from scipy.io import wavfile
from tkinter import simpledialog


#allows us to play sound
pygame.mixer.init()

class VoiceRecorder:
    def __init__(self):
        self.shifted_samplingRate = 0
        self.ifft_result = []

        #init our window, title, zoom state, and resizeableness
        self.root = tk.Tk()
        self.root.title('Audio Analysis and Autotune Tool')
        self.root.wm_state('zoomed')
        self.root.resizable(False, False)

        #set plot1 characteristic
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Pressure/Wave Amplitude')
        self.ax.set_title('Audio Signal')

        #set plot2 charactersistic
        self.figFFT, self.axFFT = plt.subplots()
        self.axFFT.set_xlabel('Frequency')
        self.axFFT.set_ylabel('Pressure/Wave Amplitude')
        self.axFFT.set_title('Audio Signal FFT Transformed')

        #set plot3 characteristics
        self.figFFT_shifted, self.axFFT_shifted = plt.subplots()
        self.axFFT_shifted.set_xlabel('Frequency')
        self.axFFT_shifted.set_ylabel('Pressure/Wave Amplitude Shifted')
        self.axFFT_shifted.set_title('Audio Signal Shifted')

        #set plot4 characterstics
        self.figFFT_shifted_inverse, self.axFFT_shifted_inverse = plt.subplots()
        self.axFFT_shifted_inverse.set_xlabel('Time')
        self.axFFT_shifted_inverse.set_ylabel('Pressure/Wave Amplitude Shifted Inverse')
        self.axFFT_shifted_inverse.set_title('Audio Signal Shifted Inverse FFT')

        #setup our plots
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvasFFT = FigureCanvasTkAgg(self.figFFT, master=self.root)
        self.canvasFFT_shifted = FigureCanvasTkAgg(self.figFFT_shifted, master = self.root)
        self.canvasFFT_shifted_inverse = FigureCanvasTkAgg(self.figFFT_shifted_inverse, master = self.root)
        #setup our record button
        self.button_record = tk.Button(text="   Record  ", font=("Arial", 30, "bold"),
                                command=self.click_handler)
        self.recording = False
        # setup our select audio button
        self.button_file_select = tk.Button(text="Select File", font=("Arial", 30, "bold"),
                                            command=self.select_file_handler)
        self.file = ""
        #setup our save wav file button
        self.button_save_file = tk.Button(text="Save IFFT File", font = ("Arial", 30, "bold"),
                                          command=self.save_file_handler, state='disabled')
        # setup our tklabel
        self.label = tk.Label(text="00:00:00", font=("Arial", 15, "bold"))
        #setup our play default audio button
        self.button_shift_audio = tk.Button(text="Shift Audio", font = ("Arial", 30, "bold"),
                                             command=self.shift_audio_handler, state='disabled')

        self.root.columnconfigure((0,1,2,3,4,5), weight=1)
        self.root.rowconfigure((0,1), weight=1)
        self.root.rowconfigure(2, weight=3)
        self.root.rowconfigure(3, weight=100)

        #insert our graphs into it
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=2, sticky='nsew', padx=10, pady=10)
        self.canvasFFT.get_tk_widget().grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10, pady=10)
        self.canvasFFT_shifted.get_tk_widget().grid(row=0, column=3, rowspan=2, sticky='nsew', padx=10, pady=10)
        self.canvasFFT_shifted_inverse.get_tk_widget().grid(row = 0, column=4, rowspan=2, sticky='nsew', padx=10, pady=10)

        #insert our graph button into it

        #insert our label
        self.label.grid(row=2, column=0, columnspan=6, sticky='nsew')

        #insert our lower 3 buttons
        self.button_record.grid(row=3, column=0, columnspan=1, sticky='nsew')
        self.button_file_select.grid(row=3, column=1, columnspan=1, sticky='nsew')
        self.button_save_file.grid(row=3, column=4, columnspan=2, sticky='nsew')
        self.button_shift_audio.grid(row = 3, column=3, sticky='nsew')


        #temporary removal
        #self.button_record.pack(side='left', expand=True, fill='both')
        #self.button_file_select.pack(side='right', expand=True, fill='both')
        #self.label.pack(side='top')
        #self.canvas.get_tk_widget().pack(side='top', fill='both')

        self.root.mainloop()


    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button_record.config(fg="black")
        else:
            #redraw our graph
            self.clearGraphs()

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
            self.get_fft_plot(self.file)



        threading.Thread(target = _open_dialog).start()


    def record(self):
        self.file = "recording.wav"
        #starting our audio stream
        audio = pyaudio.PyAudio()
        #rate is how fast se sample our data
        #channels is mono sample
        #fpb is the lenght of our audio buffer
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
        self.get_fft_plot("recording.wav")


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

    #not working below VVV

    def save_file_handler(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])

        if file_path:
            # Save the audio data to the specified WAV file
            wavfile.write(file_path, self.shifted_samplingRate, np.real(self.ifft_result).astype(np.int16))
    def shift_audio_handler(self):
        shift_value = simpledialog.askstring("Input", "Input frequency shift value")

        #were going to calculate ftt then shift then inverse FFT

        sampling_rate, audio_data = wavfile.read(self.file)

        self.shifted_samplingRate = sampling_rate

        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        fft_result = np.fft.fft(audio_data)
        frequencies = np.fft.fftfreq(len(audio_data), d=1 / sampling_rate)
        frequencies = frequencies[:len(frequencies) // 10]

        for i in range(len(fft_result) - 1, int(shift_value) - 1, -1):
            fft_result[i] = fft_result[i - int(shift_value)]

        for i in range(int(shift_value)):
            fft_result[i] = 0

        self.axFFT_shifted.plot(frequencies, (fft_result / 1000)[:len(fft_result)//10])
        self.canvasFFT_shifted.draw()

        #now take ifft

        self.ifft_result = np.fft.ifft(fft_result)

        #finding the time of the audio
        obj = wave.open(self.file, "rb")

        sample_freq = obj.getframerate()
        n_samples = obj.getnframes()
        signal_wave = obj.readframes(-1)

        obj.close()
        t_audio = n_samples / sample_freq
        times = np.linspace(0, t_audio, num=n_samples)


        self.axFFT_shifted_inverse.plot(times, self.ifft_result, 'b-')
        self.canvasFFT_shifted_inverse.draw()

        self.button_save_file.config(state='normal')

    def get_fft_plot(self, recording_name="recording.wav"):
        sampling_rate, audio_data = wavfile.read(recording_name)

        #convert to mono
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        #fft of our recording and shortening the records
        frequency_spectrum = np.fft.fft(audio_data) / 1000
        frequencies = np.fft.fftfreq(len(audio_data), d=1 / sampling_rate)
        frequency_spectrum = frequency_spectrum[:len(frequency_spectrum)//10]
        frequencies = frequencies[:len(frequencies)//10]

        self.axFFT.plot(frequencies, frequency_spectrum)
        self.canvasFFT.draw()
        self.button_shift_audio.config(state='normal')

    def clearGraphs(self):
        self.ax.clear()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Pressure/Wave Amplitude')
        self.ax.set_title('Audio Signal')
        self.canvas.draw()

        self.axFFT.clear()
        self.axFFT.set_xlabel('Frequency')
        self.axFFT.set_ylabel('Pressure/Wave Amplitude')
        self.axFFT.set_title('Audio Signal FFT Transformed')
        self.canvasFFT.draw()

        self.axFFT_shifted.clear()
        self.axFFT_shifted.set_xlabel('Frequency')
        self.axFFT_shifted.set_ylabel('Pressure/Wave Amplitude')
        self.axFFT_shifted.set_title('Audio Signal Shifted')
        self.canvasFFT_shifted.draw()

        self.axFFT_shifted_inverse.clear()
        self.axFFT_shifted_inverse.set_xlabel('Time')
        self.axFFT_shifted_inverse.set_ylabel('Pressure/Wave Amplitude Shifted Inverse')
        self.axFFT_shifted_inverse.set_title('Audio Signal Shifted Inverse FFT')
        self.canvasFFT_shifted_inverse.draw()

    def enable_buttons(self):
        pass
VoiceRecorder()