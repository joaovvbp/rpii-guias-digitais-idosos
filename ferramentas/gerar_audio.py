#!/usr/bin/env python3
"""Gera o áudio de cada passo dos guias da biblioteca com o Piper (voz neural local).

Uso:
    python3 ferramentas/gerar_audio.py --piper <caminho do executável piper> --voz <modelo .onnx>

Para cada passo de guias/<id>.json (menos o index.json), gera audio/<id>-<n>.mp3 e grava
o campo "audio" no passo. Só refaz o arquivo quando o texto falado mudou (o hash do
texto fica em audio/textos.json). Precisa do ffmpeg para converter para MP3.

O nome de quem ajuda só existe no link, então {contato} é falado como
"a pessoa que te mandou este guia". A frase na tela continua com o nome.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GUIAS = RAIZ / "guias"
AUDIO = RAIZ / "audio"
CONTATO_FALADO = "a pessoa que te mandou este guia"


def texto_falado(passo: dict) -> str:
    return (passo.get("fala") or passo["frase"]).replace("{contato}", CONTATO_FALADO)


def gera(piper: str, voz: str, texto: str, destino: Path, ritmo: float) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "passo.wav"
        subprocess.run([piper, "-m", voz, "--length-scale", str(ritmo),
                        "--sentence-silence", "0.4", "-f", str(wav)],
                       input=texto, text=True, check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav),
                        "-ac", "1", "-b:a", "48k", str(destino)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--piper", required=True)
    ap.add_argument("--voz", required=True, help="modelo .onnx do Piper (com o .onnx.json ao lado)")
    ap.add_argument("--ritmo", type=float, default=1.15, help="maior que 1 fala mais devagar")
    ap.add_argument("--tudo", action="store_true", help="refaz todos os arquivos")
    a = ap.parse_args()

    AUDIO.mkdir(exist_ok=True)
    marcas_path = AUDIO / "textos.json"
    marcas = json.loads(marcas_path.read_text()) if marcas_path.exists() else {}
    chave_voz = f"{Path(a.voz).name}|{a.ritmo}"
    feitos = pulados = 0

    for arq in sorted(GUIAS.glob("*.json")):
        if arq.name == "index.json":
            continue
        guia = json.loads(arq.read_text())
        for n, passo in enumerate(guia["passos"], start=1):
            nome = f"{guia['id']}-{n}.mp3"
            destino = AUDIO / nome
            texto = texto_falado(passo)
            h = hashlib.sha1(f"{chave_voz}|{texto}".encode()).hexdigest()
            if not a.tudo and destino.exists() and marcas.get(nome) == h:
                pulados += 1
            else:
                gera(a.piper, a.voz, texto, destino, a.ritmo)
                marcas[nome] = h
                feitos += 1
            passo["audio"] = f"audio/{nome}"
        arq.write_text(json.dumps(guia, ensure_ascii=False, indent=1) + "\n")

    # tira arquivos de passos que não existem mais
    validos = {f"{json.loads(g.read_text())['id']}-{n}.mp3"
               for g in GUIAS.glob("*.json") if g.name != "index.json"
               for n in range(1, len(json.loads(g.read_text())["passos"]) + 1)}
    for velho in AUDIO.glob("*.mp3"):
        if velho.name not in validos:
            velho.unlink()
            marcas.pop(velho.name, None)

    marcas_path.write_text(json.dumps(marcas, indent=1, sort_keys=True) + "\n")
    print(f"gerados: {feitos}, sem mudança: {pulados}")


if __name__ == "__main__":
    main()
