import tensorflow as tf
import numpy as np
import pandas as pd
import math

def read_and_process_data(data_dir="/content/drive/MyDrive/CHFJPY=X.csv", source="close", input_length=20, batch_size=32, shuffle=True):
  close = []
  df_chfjpy = pd.read_csv(data_dir)
  if source == "close":
    source_arr = df_chfjpy["Close"]
  elif source == "open":
    source_arr = df_chfjpy["Open"]
  elif source == "high":
    source_arr = df_chfjpy["High"]
  elif source == "Low":
    source_arr = df_chfjpy["Low"]
  
  # remove nan values
  for val in source_arr :
    if not math.isnan(val):
      close.append(val)

  # calculate 5-period moving average as ground truth value 
  sliding_window_input = []
  sliding_window_target = []
  for index, val in enumerate(close):
    if index + input_length + 5 <= len(close) - 1:
      sliding_window_input.append(np.array(close[index:index+input_length]))
      sliding_window_target.append(np.mean(close[index+input_length:index+input_length+5]))
  ds = tf.data.Dataset.from_tensor_slices((sliding_window_input, sliding_window_target)).batch(batch_size)
  if shuffle:
    ds = ds.shuffle(512)
  return ds
