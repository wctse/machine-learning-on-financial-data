import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model

N = 1000
T = 10
D = 1
X = []
Y = []

series = np.sin(0.1 * np.arange(N)) + np.random.rand(N) # + np.sin(0.13 * np.arange(N))

for t in range(N - T):
    X.append(series[t:t+T])
    Y.append(series[t+T])

X = np.array(X).reshape(-1, T, 1)
Y = np.array(Y)

i = Input(shape=(T, D))
x = LSTM(10)(i)
x = Dense(1)(x)

model = Model(i, x)

model.compile(loss='mse', optimizer=Adam(lr=0.05))

r = model.fit(
    X[:-N//2], Y[:-N//2],
    batch_size=100,
    epochs=200,
    validation_data=(X[-N//2:], Y[-N//2:])
)

plt.plot(r.history['loss'], label='Loss')
plt.plot(r.history['val_loss'], label='val_loss')
plt.legend()

forecast = []
input_ = X[-N//2]
while len(forecast) < len(Y[-N//2:]):
  f = model.predict(input_.reshape(1, T, 1))[0,0]
  forecast.append(f)

  input_ = np.roll(input_, -1)
  input_[-1] = f

plt.plot(Y[-N//2:], label='targets')
plt.plot(forecast, label='forecast')
plt.title("RNN Forecast")
plt.legend()
plt.show()