import numpy as np

def get_fft(x, y):
    N = y.shape[1]
    h = x[0,1] - x[0,0]
    # yf = np.fft.fft(y).real[:,:N/2]
    ft = np.fft.fft(y)
    fft = ft[:, :int(N/2)]
    fft = np.fft.fft(y)[:, :int(N/2)]
    yf = np.absolute(fft)
    yp = np.arctan2(fft.imag,fft.real)
    xf0 = np.fft.fftfreq(N,h)
    xf = xf0[:int(N/2)]
    xf = np.tile(xf,y.shape[0])
    xf0 = np.tile(xf0,y.shape[0])
    xf = xf.reshape(yf.shape[0],yf.shape[1])
    xf0 = xf0.reshape(ft.shape[0],ft.shape[1])
    # array to store fft + frequences
    fft = np.array((xf0,ft))
    # array to store fft amplitude + frequences
    fft_amp = np.array((xf,yf))
    # array to store fft phase + frequences
    fft_phase = np.array((xf,yp))
    return fft, fft_amp, fft_phase
