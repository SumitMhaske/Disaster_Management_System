import numpy as np
import joblib
import tensorflow as tf

def load_model_and_preprocessors(model_path=r"D:\Downloads\ML1\DisasterAlert (8)\DisasterAlert (8)\models\lstm_earthquake_model.keras",
                                 scaler_path=r"D:\Downloads\ML1\DisasterAlert (8)\DisasterAlert (8)\models\scaler (1).save",
                                 encoder_path=r"D:\Downloads\ML1\DisasterAlert (8)\DisasterAlert (8)\models\label_encoder.save"):
    model = tf.keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    le = joblib.load(encoder_path)
    return model, scaler, le

def predict_next_earthquake(df, model, scaler, le, window_size=10):
    df = df.sort_values('datetime').dropna(subset=['magnitude', 'latitude', 'longitude', 'state'])
    
    features = df[['magnitude', 'latitude', 'longitude']]
    features_scaled = scaler.transform(features)
    last_seq = features_scaled[-window_size:].reshape(1, window_size, 3)
    
    pred_mag_scaled, pred_state_prob = model.predict(last_seq)
    
    pred_mag = scaler.inverse_transform([[pred_mag_scaled[0][0], 0, 0]])[0][0]
    pred_state = le.inverse_transform([np.argmax(pred_state_prob)])[0]
    
    return round(pred_mag, 2), pred_state