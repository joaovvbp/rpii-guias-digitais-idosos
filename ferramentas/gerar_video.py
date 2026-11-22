#!/usr/bin/env python3
"""Gera o vídeo de cada guia da biblioteca, para mandar pelo WhatsApp.

Uso:
    python3 ferramentas/gerar_video.py --piper <piper> --voz <modelo .onnx> [--cel android|iphone] [id ...]

O vídeo imita uma gravação da tela do celular: cada passo mostra a tela dentro de um
aparelho, com a legenda do passo em cima, um dedo indo até o ponto do toque, o círculo
do toque e a narração do passo (audio/<id>-<n>.mp3, de gerar_audio.py). A capa e o fim
ganham uma fala própria, gerada na hora com o Piper.

Os quadros vêm de video.html, desenhados por ferramentas/quadros.js no Chrome sem janela
(precisa de `npm install` em ferramentas/). Também precisa do ffmpeg e do ffprobe.
Com --quadros <pasta>, guarda uma imagem de cada tela (para relatórios).
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
QPS = 25
PAUSA = 0.9       # segundos de tela parada depois de cada fala
SO_TELA = 2.5     # duração mínima de uma tela

FALAS = {
    "capa": "Guia: {titulo}. Assista com calma. Você pode pausar e voltar quando quiser.",
    "fim": "Pronto. Pode ver de novo quantas vezes quiser. Se ficou alguma dúvida, responda aqui mesmo nesta conversa.",
}


class Quieto(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def servidor():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quieto, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def fala(piper: str, voz: str, texto: str, destino: Path) -> None:
    wav = destino.with_suffix(".wav")
    subprocess.run([piper, "-m", voz, "--length-scale", "1.15", "-f", str(wav)],
                   input=texto, text=True, check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-ac", "1", str(destino)], check=True)


def duracao(arquivo: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(arquivo)], check=True, capture_output=True, text=True)
    return float(r.stdout.strip())


def trecho(quadros: Path, tela: str, n: int, audio: Path | None, destino: Path) -> None:
    """Uma tela: a animação (n quadros) e depois o último quadro parado até a fala acabar."""
    anim = n / QPS
    total = max(SO_TELA, anim + 0.6, (duracao(audio) + PAUSA) if audio else 0)
    video = ["-framerate", str(QPS), "-start_number", "0", "-i", str(quadros / f"{tela}-%03d.png")]
    som = ["-i", str(audio)] if audio else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono"]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *video, *som, "-t", f"{total:.2f}",
                    "-vf", f"tpad=stop_mode=clone:stop_duration={total:.2f},format=yuv420p",
                    "-af", "apad,aresample=44100", "-ac", "1",
                    "-c:v", "libx264", "-preset", "medium", "-r", str(QPS),
                    "-c:a", "aac", "-b:a", "96k", str(destino)], check=True)


def gera(gid: str, base: str, a, tmp: Path) -> Path:
    guia = json.loads((GUIAS / f"{gid}.json").read_text())
    quadros = tmp / gid
    subprocess.run(["node", str(RAIZ / "ferramentas" / "quadros.js"), base, gid, str(quadros), a.cel], check=True)
    telas = json.loads((quadros / "telas.json").read_text())

    trechos = []
    for i, t in enumerate(telas):
        if t["tela"] in FALAS:
            audio = tmp / f"{gid}-{t['tela']}.mp3"
            fala(a.piper, a.voz, FALAS[t["tela"]].format(titulo=guia["titulo"]), audio)
        else:
            audio = RAIZ / t["audio"] if t.get("audio") else None
        mp4 = tmp / f"{gid}-{i:02d}.mp4"
        trecho(quadros, t["tela"], t["quadros"], audio, mp4)
        trechos.append(mp4)
        if a.quadros:
            Path(a.quadros).mkdir(parents=True, exist_ok=True)
            ultimo = quadros / f"{t['tela']}-{t['quadros'] - 1:03d}.png"
            shutil.copy(ultimo, Path(a.quadros) / f"{gid}-{i:02d}-{t['tela']}.png")
            if t["quadros"] > 1:  # o instante do toque, para mostrar o círculo
                meio = quadros / f"{t['tela']}-{int(t['quadros'] * 0.66):03d}.png"
                shutil.copy(meio, Path(a.quadros) / f"{gid}-{i:02d}-{t['tela']}-toque.png")

    lista = tmp / f"{gid}.txt"
    lista.write_text("".join(f"file '{t}'\n" for t in trechos))
    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / (f"{gid}.mp4" if a.cel == "android" else f"{gid}-{a.cel}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c", "copy", "-movflags", "+faststart", str(destino)], check=True)
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--piper", required=True)
    ap.add_argument("--voz", required=True)
    ap.add_argument("--cel", default="android", choices=["android", "iphone"])
    ap.add_argument("--quadros", help="pasta para guardar uma imagem de cada tela")
    ap.add_argument("ids", nargs="*", help="só estes guias (padrão: todos)")
    a = ap.parse_args()

    ids = a.ids or sorted(p.stem for p in GUIAS.glob("*.json") if p.name != "index.json")
    srv, base = servidor()
    try:
        with tempfile.TemporaryDirectory() as t:
            for gid in ids:
                destino = gera(gid, base, a, Path(t))
                print(f"{destino.relative_to(RAIZ)}: {duracao(destino):.0f} s, {destino.stat().st_size / 1e6:.1f} MB")
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
