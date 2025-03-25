import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.fft import fft, ifft
import scipy.fftpack as fftpk
from scipy.io import wavfile

def volume(signal,volume):
    new_signal = np.clip(signal * volume, -32768, 32767).astype(np.int16)
    return new_signal

def fade_in(signal,rate,duration):
    signal = np.array(signal).astype(np.float32)
    fade_in_samples = int(duration * rate)
    fade_in_mask = np.linspace(0, 1, fade_in_samples)
    signal[:fade_in_samples] *= fade_in_mask[:, np.newaxis] if signal.ndim > 1 else fade_in_mask

    return signal
    
def fade_out(signal,rate,duration):
    signal = np.array(signal).astype(np.float32)
    fade_out_samples = int(duration * rate)
    fade_out_mask = np.linspace(1, 0, fade_out_samples)
    signal[-fade_out_samples:] *= fade_out_mask[:, np.newaxis] if signal.ndim > 1 else fade_out_mask

    return signal

def normalize_audio(audio, target_rms):
    """
    Normalize the audio to a target RMS level.
    """
    current_rms = np.sqrt(np.mean(audio**2))
    if current_rms == 0:
        return audio
    scaling_factor = target_rms / current_rms
    return audio * scaling_factor

def FFT_graph(signal,sample,s_rate):
    signal = signal.astype(np.float32)
    song_dur = len(signal)/sample   

    FFT = abs(fft(signal))
    freqs = fftpk.fftfreq(len(FFT), (1.0/s_rate))   


    plt.plot(freqs[range(len(FFT)//2)], FFT[range(len(FFT)//2)])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.show(block = False)



#s_rate, signal = wavfile.read("Test.wav") 
#                                                        
#FFT_graph(signal,s_rate)
#
#new_signal = normalize_audio(signal,30)
#new_signal = fade_in(new_signal,s_rate,3)
#new_signal = fade_out(new_signal,s_rate,3)
#new_signal = volume(new_signal,1)
#
#wavfile.write("output.wav", s_rate, new_signal)
#
#FFT_graph(new_signal,s_rate)