#!/usr/bin/env python3
"""Gera um vídeo curto de cada guia da biblioteca, para mandar pelo WhatsApp.

Uso:
    python3 ferramentas/gerar_video.py --piper <piper> --voz <modelo .onnx> [id ...]

Para cada guia (ou só os ids pedidos), tira uma foto de cada tela no modo vídeo de
guia.html (capa, um passo por tela, fim) com o Chrome sem janela, junta cada foto com o
áudio do passo (audio/<id>-<n>.mp3, de gerar_audio.py) e grava videos/<id>.mp4.
A capa e o fim ganham uma fala própria, gerada na hora com o Piper.

Precisa do ffmpeg, do ffprobe e do Chrome (google-chrome ou chromium).
"""
import argparse
import functools
import http.server
import json
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GUIAS = RAIZ / "guias"
SAIDA = RAIZ / "videos"
LARGURA, ALTURA, ESCALA = 390, 760, 2
PAUSA = 0.9          # segundos de tela parada depois de cada fala
SO_TELA = 2.5        # duração de uma tela sem fala


def servidor() -> tuple[http.server.ThreadingHTTPServer, int]:
    manipulador = functools.partial(QuietHandler, directory=str(RAIZ))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manipulador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def chrome() -> str:
    for nome in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(nome):
            return nome
    raise SystemExit("não achei o Chrome")


def foto(navegador: str, url: str, destino: Path, perfil: Path) -> None:
    subprocess.run([navegador, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={perfil}", "--no-first-run",
                    f"--window-size={LARGURA},{ALTURA}", f"--force-device-scale-factor={ESCALA}",
                    "--virtual-time-budget=4000", f"--screenshot={destino}", url],
                   check=True, capture_output=True)


def fala(piper: str, voz: str, texto: str, destino: Path) -> None:
    wav = destino.with_suffix(".wav")
    subprocess.run([piper, "-m", voz, "--length-scale", "1.15", "-f", str(wav)],
                   input=texto, text=True, check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-ac", "1", str(destino)],
                   check=True)


def duracao(audio: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(audio)], check=True, capture_output=True, text=True)
    return float(r.stdout.strip())


def trecho(imagem: Path, audio: Path | None, destino: Path) -> None:
    """Uma tela parada com a fala dela (ou silêncio), sempre no mesmo formato para juntar."""
    tempo = duracao(audio) + PAUSA if audio else SO_TELA
    som = ["-i", str(audio)] if audio else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono"]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "25", "-i", str(imagem),
                    *som, "-t", f"{tempo:.2f}",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
                    "-af", "apad,aresample=44100", "-ac", "1",
                    "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-r", "25",
                    "-c:a", "aac", "-b:a", "96k", str(destino)], check=True)


def gera(guia: dict, base: str, navegador: str, piper: str, voz: str, tmp: Path) -> Path:
    gid = guia["id"]
    telas = [("capa", f"Guia: {guia['titulo']}. Assista com calma. Você pode pausar e voltar quando quiser.")]
    telas += [(str(n), RAIZ / p["audio"] if p.get("audio") else None) for n, p in enumerate(guia["passos"], 1)]
    telas += [("fim", "Pronto. Você chegou ao fim do guia. Se ficou alguma dúvida, fale com quem te mandou este vídeo.")]

    perfil = tmp / "perfil"
    trechos = []
    for i, (tela, som) in enumerate(telas):
        png = tmp / f"{gid}-{i:02d}.png"
        foto(navegador, f"{base}guia.html#g={gid}&video={tela}", png, perfil)
        if isinstance(som, str):
            mp3 = tmp / f"{gid}-{tela}.mp3"
            fala(piper, voz, som, mp3)
            som = mp3
        mp4 = tmp / f"{gid}-{i:02d}.mp4"
        trecho(png, som, mp4)
        trechos.append(mp4)

    lista = tmp / f"{gid}.txt"
    lista.write_text("".join(f"file '{t}'\n" for t in trechos))
    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / f"{gid}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c", "copy", "-movflags", "+faststart", str(destino)], check=True)
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--piper", required=True)
    ap.add_argument("--voz", required=True)
    ap.add_argument("ids", nargs="*", help="só estes guias (padrão: todos)")
    a = ap.parse_args()

    navegador = chrome()
    srv, porta = servidor()
    base = f"http://127.0.0.1:{porta}/"
    try:
        with tempfile.TemporaryDirectory() as t:
            for arq in sorted(GUIAS.glob("*.json")):
                if arq.name == "index.json":
                    continue
                guia = json.loads(arq.read_text())
                if a.ids and guia["id"] not in a.ids:
                    continue
                destino = gera(guia, base, navegador, a.piper, a.voz, Path(t))
                print(f"{destino.relative_to(RAIZ)}: {duracao(destino):.0f} s, "
                      f"{destino.stat().st_size / 1e6:.1f} MB")
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
