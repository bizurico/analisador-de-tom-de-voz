import librosa
import numpy as np
import parselmouth
from parselmouth.praat import call

def analisar_audio(caminho_arquivo):
    """
    Carrega um arquivo de áudio e extrai características vocais,
    incluindo volume, pitch, jitter, shimmer e ritmo.
    """
    try:
        # --- Análise com Librosa (Volume, Pitch, Ritmo) ---
        y, sr = librosa.load(caminho_arquivo, sr=None)
        
        # Volume (Energia RMS Média)
        volume_medio = np.mean(librosa.feature.rms(y=y))
        
        # Pitch (Frequência Fundamental - F0)
        # Usa o algoritmo PYIN para estimar o pitch
        f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        # Filtra apenas os frames onde a voz foi detectada (remove silêncio/NaN)
        f0_voiced = f0[voiced_flag]
        
        # Calcula média e desvio padrão (variação)
        pitch_medio = np.mean(f0_voiced) if len(f0_voiced) > 0 else 0
        variacao_pitch = np.std(f0_voiced) if len(f0_voiced) > 0 else 0

        # Ritmo da Fala (Sílabas por segundo)
        # Detecta "onsets" (inícios de eventos sonoros)
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        duracao_segundos = librosa.get_duration(y=y, sr=sr)
        ritmo_sps = (len(onsets) / duracao_segundos) if duracao_segundos > 0 else 0

        # --- Análise com Parselmouth/Praat (Jitter e Shimmer) ---
        snd = parselmouth.Sound(caminho_arquivo)
        pitch = snd.to_pitch()
        point_process = call(pitch, "To PointProcess")
        
        # Jitter (local) - Instabilidade de frequência
        jitter_local = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
        
        # Shimmer (local) - Instabilidade de amplitude
        shimmer_local = call([snd, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100

        # Tratamento de erros para valores NaN
        if np.isnan(jitter_local): jitter_local = 0
        if np.isnan(shimmer_local): shimmer_local = 0
            
        # --- Estrutura de Retorno ---
        resultado = {
            'nome_arquivo': caminho_arquivo,
            'volume_medio': volume_medio,
            'pitch_medio_hz': pitch_medio,
            'variacao_pitch': variacao_pitch,
            'jitter_percent': jitter_local,
            'shimmer_percent': shimmer_local,
            'ritmo_sps': ritmo_sps
        }
        
        return resultado

    except Exception as e:
        # Print apenas para debug no terminal, não afeta a GUI
        print(f"Erro interno na análise: {e}")
        return None

# --- Bloco de Teste ---
if __name__ == '__main__':
    print("Módulo analise.py carregado com sucesso.")