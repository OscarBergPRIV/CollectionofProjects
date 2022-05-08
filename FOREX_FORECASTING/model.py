import tensorflow as tf

def create_model (input_length=20, features=1, arch="CNN_GRU", lstm_unit1=3, lstm_unit2=3, dense_units=3, dropout_rate=0.5, gru_unit1=3, kernel_size=4, cov1d_filter1=3, cov1d_filter2=3):
  input_shape = (input_length, features)
  inputs = tf.keras.layers.Input(shape=input_shape)
  x = tf.keras.layers.Normalization()(inputs)
  if arch == "LSTM":
    x = tf.keras.layers.LSTM(units=lstm_unit2, return_sequences=False)(x)
    x = tf.keras.layers.Dropout(dropout_rate)(x)
    x = tf.keras.layers.Dense(dense_units, activation="tanh")(x)
    outputs = tf.keras.layers.Dense(1, activation="linear")(x)
    return tf.keras.Model(inputs, outputs)
  elif arch == "CNN_GRU":
    x = tf.keras.layers.Conv1D(cov1d_filter1, kernel_size=kernel_size, activation='relu')(x)
    x = tf.keras.layers.MaxPool1D()(x)
    x = tf.keras.layers.Conv1D(cov1d_filter2, kernel_size=kernel_size, activation='relu')(x)
    x = tf.keras.layers.MaxPool1D()(x)
    print(x.shape)
    #x = tf.keras.layers.Flatten()(x)
    #x = tf.expand_dims(x, axis=-1)
    #x = tf.keras.layers.GRU(units=gru_unit1, return_sequences=True)(x)
    x = tf.keras.layers.GRU(units=gru_unit1)(x)
    print(x.shape)
    x = tf.keras.layers.Dropout(rate=dropout_rate)(x)
    outputs = tf.keras.layers.Dense(1, activation="linear")(x)
    return tf.keras.Model(inputs, outputs)
  
