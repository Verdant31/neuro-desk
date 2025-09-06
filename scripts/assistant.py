import speech_recognition as sr
from typing import Optional
from helpers import get_logger, get_root_path
from utils import normalize_text
import subprocess
import time
import difflib

logger = get_logger(__name__)


class Assistant:
    def __init__(self, wake_phrase: str, language: str = "pt-BR"):
        self.language = language
        self.maximize_microphone_volume()
        self._wake_phrase_norm: str = normalize_text(wake_phrase or "")
        self._wake_window_seconds: float = 2.5
        self._wake_cooldown_seconds: float = 1.5
        self._wake_buffer: str = ""
        self._wake_last_update: float = 0.0
        self._wake_last_trigger: float = 0.0

    def check_wake(self, chunk: Optional[str]) -> bool:
        """
        Verifica se a wake phrase foi dita, mesmo que dividida em múltiplos reconhecimentos.
        """
        if not chunk:
            return False

        now = time.time()
        chunk_norm = normalize_text(chunk)

        # Evita re-disparo em sequência
        if now - self._wake_last_trigger < self._wake_cooldown_seconds:
            return False

        # Reinicia buffer se o último update foi há muito tempo
        if now - self._wake_last_update > self._wake_window_seconds:
            self._wake_buffer = chunk_norm
        else:
            self._wake_buffer = (self._wake_buffer + " " + chunk_norm).strip()
            if len(self._wake_buffer) > 120:
                self._wake_buffer = self._wake_buffer[-120:]

        self._wake_last_update = now

        # 1) Checagem exata no buffer agregado
        if self._wake_phrase_norm in self._wake_buffer:
            self._wake_last_trigger = now
            # Limpa buffer após detecção para evitar duplicação imediata
            self._wake_buffer = ""
            self._wake_last_update = 0.0
            return True

        # 2) Checagem fuzzy de similaridade (tolerância a pequenos erros de ASR)
        phrase = self._wake_phrase_norm
        phrase_len = len(phrase)
        tokens_phrase = phrase.split()
        token_count = len(tokens_phrase)
        threshold = 0.84  # ajuste fino se necessário

        def ratio(a: str, b: str) -> float:
            return difflib.SequenceMatcher(None, a, b).ratio()

        # Candidatos por tokens: últimas janelas com mesmo nº de tokens (±1)
        buf_tokens = self._wake_buffer.split()
        candidates = []
        if buf_tokens:
            if len(buf_tokens) >= token_count:
                candidates.append(" ".join(buf_tokens[-token_count:]))
            if len(buf_tokens) >= token_count + 1:
                candidates.append(" ".join(buf_tokens[-(token_count + 1):]))

        # Candidatos por caracteres: sufixo recente com folga
        suffix = self._wake_buffer[-(phrase_len + 8):]
        if suffix:
            # janela deslizante simples ao tamanho da frase
            if len(suffix) >= phrase_len:
                for i in range(0, len(suffix) - phrase_len + 1):
                    candidates.append(suffix[i:i + phrase_len])
            else:
                candidates.append(suffix)

        for cand in candidates:
            if ratio(phrase, cand) >= threshold:
                self._wake_last_trigger = now
                self._wake_buffer = ""
                self._wake_last_update = 0.0
                logger.debug(
                    f"Wake phrase detectada por similaridade: cand='{cand}' ratio>={threshold}")
                return True

        return False

    def listen(self) -> Optional[str]:
        """
        Listen for speech input and convert to text.

        Returns:
            str or None: Recognized text or None if failed
        """
        r = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                r.energy_threshold = 100
                r.adjust_for_ambient_noise(source, duration=1)
                logger.debug("Escutando entrada de voz...")
                audio = r.listen(source, timeout=3)

                try:
                    text = r.recognize_google(  # type: ignore
                        audio, language=self.language)
                    normalized_text = text.lower()
                    logger.info(f"Fala reconhecida: '{text}'")
                    return normalized_text
                except sr.UnknownValueError:
                    logger.debug(
                        "Fala capturada mas não pôde ser compreendida")
                    return None
                except sr.RequestError as e:
                    logger.exception(
                        f"Erro do serviço Google Speech Recognition: {e}")
                    return None
        except sr.WaitTimeoutError:
            logger.debug("Nenhuma fala detectada, continuando a escutar...")
        except Exception as e:
            logger.exception(f"Erro durante reconhecimento de voz: {e}")
            return None

    def listen_with_timeout(self, timeout_seconds: int = 10) -> Optional[str]:
        """
        Listen for speech input for up to timeout_seconds seconds and convert to text.
        Returns recognized text or None if nothing is said within the window.
        """
        r = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                r.energy_threshold = 100
                r.adjust_for_ambient_noise(source, duration=1)
                logger.debug(
                    f"Escutando entrada de voz (até {timeout_seconds} segundos)...")
                audio = r.listen(source, phrase_time_limit=timeout_seconds)
                try:
                    text = r.recognize_google(  # type: ignore
                        audio, language=self.language)
                    normalized_text = text.lower()
                    logger.info(f"Fala reconhecida: '{text}'")
                    return normalized_text
                except sr.UnknownValueError:
                    logger.debug(
                        "Fala capturada mas não pôde ser compreendida")
                    return None
                except sr.RequestError as e:
                    logger.exception(
                        f"Erro do serviço Google Speech Recognition: {e}")
                    return None
        except Exception as e:
            logger.exception(f"Erro durante reconhecimento de voz: {e}")
            return None

    def maximize_microphone_volume(self):
        """
        Set the system microphone input volume (Windows only).
        """
        volume_percent = 100
        try:
            sound_volume_exe = get_root_path() + "assets/SoundVolumeView.exe"
            subprocess.run([sound_volume_exe, '/SetVolume', 'DefaultCaptureDevice',
                           str(volume_percent)], check=True)
            logger.info(
                f"Volume do dispositivo de captura padrão do usuário definido para {volume_percent}%")
        except Exception as e:
            logger.exception(f"Falha ao definir volume do microfone: {e}")
