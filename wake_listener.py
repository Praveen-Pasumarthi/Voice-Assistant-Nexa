import pvporcupine
import pyaudio
import struct

def wake_word_listener():
    porcupine = pvporcupine.create(keyword_paths=["wake_words/Hey-Barry_en_windows_v3_0_0.ppn"], access_key="BNDW5q5SCK92P1Pf4SgcyqRZ3OLCoMHcUgt3wP9c6rvvo1iYxeg3mQ==")
    pa = pyaudio.PyAudio()

    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("Listening for 'Hey Barry'...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    wake_word_listener()
