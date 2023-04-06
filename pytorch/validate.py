# import tensorflow as tf
# from tensorflow import keras
from torch import from_numpy, jit
import numpy as np
from preprocessingivara import create_spectogram, split_file
import os

score = 0
total = 0

def load_models():
    # load json and create model
    # loaded_models = {'cel': None, 'cla': None, 'flu': None, 'gac': None, 'gel': None, 
    #                'org': None, 'pia': None, 'sax': None, 'tru': None, 'vio': None, 'voi': None}
    # models_path = './model/models/'

    # for root, _, files in os.walk(models_path):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         if file[-4:] == 'json':
    #             json_file = open(file_path, 'r')
    #             loaded_model_json = json_file.read()
    #             json_file.close()
    #             loaded_model = tf.keras.models.model_from_json(loaded_model_json)
    #             # load weights into new model
    #             loaded_model.load_weights(models_path + file[:-5] + '.h5')
    #             loaded_models[file[6:9]] = loaded_model

    # # load json and create model
    # json_file = open('./model/modelBIG.json', 'r')
    # loaded_model_json = json_file.read()
    # json_file.close()
    # loaded_model = tf.keras.models.model_from_json(loaded_model_json)
    # # load weights into new model
    # loaded_model.load_weights("./model/modelBIG.h5")
    
    loaded_model = jit.load('modelzubara.pt')
    return loaded_model

def predict(model, data):
    global instruments, instrument_list
    global precission, recall, accuracy, total, exacts, TP, FP, TN, FN
    # Predict
    total += 1
    pred_max = [0,0,0,0,0,0,0,0,0,0,0]    
    for signal in data:
        signal = np.resize(signal, (1, 128, 44))
        prediction = model(from_numpy(np.expand_dims(signal, 0)))
        prediction = prediction.detach().numpy()
        for i in range(len(prediction[0])):
            if prediction[0][i] > pred_max[i]:
                pred_max[i] = prediction[0][i]
                if prediction[0][i] > 0.8:
                    pred_max[i] = 1
                    continue


     
    print("pred_max: ", pred_max)    

    for i in range(len(pred_max)):
        if pred_max[i] > 0.8:
            pred_max[i] = 1
            if instruments[i] == 1:
                TP += 1
            elif instruments[i] == 0:
                FP += 1
        else:
            pred_max[i] = 0
            if instruments[i] == 1:
                FN += 1
            elif instruments[i] == 0:
                TN += 1
            
    if pred_max == instruments:
        exacts += 1
    
    recall = TP / (TP + FN)
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    if TP + FP == 0:
        precission = 0
    else:
        precission = TP / (TP + FP)
    if precission + recall == 0:
        f1 = 0
    else:
        f1 = 2 * (precission * recall) / (precission + recall)

    print("Predciton: ", pred_max)
    print("Instruments: ", instruments)
    print("RECALL: ", recall) 
    print("ACCURACY: ", accuracy)
    print("PRECISION: ", precission) 
    print("F1: ", f1)         
    print("EXACT MATCHES: ", exacts/total)
    
            
    


if __name__ == "__main__":
    # Load model
    model = load_models()
    
    # Load data
    path = '../../DataLumenDS/Dataset/IRMAS_Validation_Data/'
    accuracy, recall, precission, total, exacts, TP, FP, TN, FN = 0, 0, 0, 0, 0, 0, 0, 0, 0
    instrument_list = ["cel", "cla", "flu", "gac", "gel", "org", "pia", "sax", "tru", "vio", "voi"]
    
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path[-3:] == "txt":
                instruments = [0,0,0,0,0,0,0,0,0,0,0]
                with open(file_path, "r") as f:
                    data = f.readlines()
                    for instrument in data:
                        if instrument.strip() in instrument_list:
                            instruments[instrument_list.index(instrument.strip())] = 1
                
              
                file_path = file_path[:-4] + ".wav"                
                # Split data
                split_signals = split_file(file_path)
                
                # Create spectrograms
                spectrograms = []
                for signal in split_signals.T:
                    spectrogram = create_spectogram(signal)
                    spectrograms.append(np.expand_dims(spectrogram, 2))
                
                
                # Predict
                predict(model, np.array(spectrograms))
                
            
 


    
    