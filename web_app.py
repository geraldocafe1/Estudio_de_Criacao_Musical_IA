"""
Servidor Web Local do Estúdio de Criação Musical Multi-Motor
Suporta: Suno (AIMusicAPI), Google Lyria 3 / 3.5 (Gemini API), MiniMax Music (Fal.ai) e ACE-Step 1.5 (Fal.ai).
Inclui Biblioteca de Músicas Geradas + Prompts Utilizados.
"""

import os
import ssl
import time
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from compositor import TEMPLATES_LETRAS

PORT = 8080
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def carregar_env():
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    chave, valor = linha.split("=", 1)
                    chave = chave.strip()
                    valor = valor.strip().strip('"').strip("'")
                    if chave not in os.environ:
                        os.environ[chave] = valor


carregar_env()


def criar_contexto_ssl():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def obter_biblioteca_musicas():
    """Retorna as músicas já geradas em outputs/ com seus prompts reais e os exemplos prontos."""
    musicas_geradas = []

    # Lê metadados reais salvos em resultado_musica.json (se existir)
    resultado_json = OUTPUT_DIR / "resultado_musica.json"
    dados_suno = []
    if resultado_json.exists():
        try:
            with open(resultado_json, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
                dados_suno = conteudo.get("data", [])
        except Exception:
            pass

    # Mapeia os MP3s e WAVs locais da pasta outputs/
    arquivos_audio = sorted(list(OUTPUT_DIR.glob("*.mp3")) + list(OUTPUT_DIR.glob("*.wav")), key=lambda p: p.stat().st_mtime, reverse=True)
    for idx, audio_arq in enumerate(arquivos_audio):
        nome_base = audio_arq.stem
        capa_local = OUTPUT_DIR / f"{nome_base}_Capa.jpeg"
        if not capa_local.exists():
            capa_local = None

        meta_json = OUTPUT_DIR / f"{nome_base}.json"
        if meta_json.exists():
            try:
                with open(meta_json, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
            except Exception:
                meta = {}
        else:
            # Tenta vincular ao resultado_musica.json (Suno)
            meta = next((d for d in dados_suno if d.get("title", "").lower() in nome_base.lower() or nome_base.endswith("_1") and dados_suno.index(d) == 0 or nome_base.endswith("_2") and dados_suno.index(d) == 1), {})

        musicas_geradas.append({
            "id": meta.get("clip_id", nome_base),
            "titulo": meta.get("title", nome_base.replace("_", " ")),
            "arquivo": f"/outputs/{audio_arq.name}",
            "capa": f"/outputs/{capa_local.name}" if capa_local else meta.get("image_url"),
            "tags": meta.get("tags", "brazilian pop rock, electric guitar, passionate male vocals, 125 bpm"),
            "letra": meta.get("lyrics", ""),
            "motor": meta.get("motor") or (f"Suno ({meta.get('mv', 'chirp-v3-5')})" if meta.get("mv") else "Local Audio"),
            "duracao": meta.get("duration", ""),
        })

    exemplos = []
    for chave, tpl in TEMPLATES_LETRAS.items():
        exemplos.append({
            "id": chave,
            "titulo": tpl["titulo"],
            "tags": tpl["tags"],
            "letra": tpl["letra"],
        })

    return {"musicas_geradas": musicas_geradas, "exemplos": exemplos}


class MusicHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def _responder_json(self, dados, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(dados, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("web/index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        elif self.path == "/api/status":
            api_key = os.getenv("AI_MUSIC_API_KEY", "").strip()
            tem_chave = bool(api_key and api_key != "sua_chave_aqui")
            self._responder_json({"has_api_key": tem_chave})
            return

        elif self.path == "/api/biblioteca":
            self._responder_json(obter_biblioteca_musicas())
            return

        elif self.path.startswith("/api/status-task"):
            query = parse_qs(urlparse(self.path).query)
            task_id = query.get("taskId", [""])[0] or query.get("id", [""])[0]
            motor = query.get("motor", ["aimusicapi"])[0]
            token_ui = query.get("token", [""])[0].strip()
            status_url = query.get("statusUrl", [""])[0].strip()
            response_url = query.get("responseUrl", [""])[0].strip()

            ssl_ctx = criar_contexto_ssl()

            # Polling para Fal.ai (MiniMax / ACE-Step)
            if motor in ("fal_minimax", "fal_acestep") and status_url:
                headers_fal = {
                    "Authorization": f"Key {token_ui}",
                    "User-Agent": "Mozilla/5.0",
                }
                try:
                    req = urllib.request.Request(status_url, headers=headers_fal, method="GET")
                    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
                        st_data = json.loads(resp.read().decode("utf-8"))

                    if st_data.get("status") == "COMPLETED" and response_url:
                        req_res = urllib.request.Request(response_url, headers=headers_fal, method="GET")
                        with urllib.request.urlopen(req_res, timeout=20, context=ssl_ctx) as resp_r:
                            res_data = json.loads(resp_r.read().decode("utf-8"))
                        audio_url = (res_data.get("audio") or {}).get("url") or (res_data.get("audio_file") or {}).get("url")
                        self._responder_json({"status": "COMPLETED", "audio_url": audio_url, "raw": res_data})
                        return

                    self._responder_json(st_data)
                    return
                except Exception as e:
                    self._responder_json({"status": "processing", "erro": str(e)})
                    return

            # Polling padrão AIMusicAPI (Suno)
            api_key = token_ui or os.getenv("AI_MUSIC_API_KEY", "").strip()
            headers_api = {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            rotas_check = [
                f"https://api.aimusicapi.ai/api/v1/sonic/task/{task_id}",
                f"https://api.aimusicapi.ai/api/v1/producer/task/{task_id}",
            ]

            for r in rotas_check:
                try:
                    req = urllib.request.Request(r, headers=headers_api, method="GET")
                    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
                        resultado_task = json.loads(resp.read().decode("utf-8"))
                        self._responder_json(resultado_task)
                        return
                except Exception:
                    pass

            self._responder_json({"status": "processing"})
            return

        elif self.path.startswith("/api/download"):
            query = parse_qs(urlparse(self.path).query)
            url_audio = query.get("url", [""])[0].strip()
            nome = query.get("nome", ["musica.mp3"])[0].strip()

            if not url_audio:
                self.send_response(400)
                self.end_headers()
                return

            # Se for link de stream do aimusicapi, converte para o MP3 definitivo em stems/
            if "api.aimusicapi.ai/api/v1/stream/" in url_audio:
                clip_id = url_audio.rstrip("/").split("/")[-1]
                url_audio = f"https://files.aimusicapi.ai/stems/{clip_id}.mp3"

            # Se já for um arquivo local em /outputs/
            if url_audio.startswith("/outputs/"):
                arq_local = OUTPUT_DIR / Path(url_audio).name
                if arq_local.exists():
                    with open(arq_local, "rb") as f:
                        conteudo = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "audio/mpeg")
                    self.send_header("Content-Disposition", f'attachment; filename="{nome}"')
                    self.send_header("Content-Length", str(len(conteudo)))
                    self.end_headers()
                    self.wfile.write(conteudo)
                    return

            # Baixa da nuvem via proxy do backend e salva em outputs/
            try:
                ssl_ctx = criar_contexto_ssl()
                req = urllib.request.Request(url_audio, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                    conteudo = resp.read()
                with open(OUTPUT_DIR / nome, "wb") as f_out:
                    f_out.write(conteudo)

                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Disposition", f'attachment; filename="{nome}"')
                self.send_header("Content-Length", str(len(conteudo)))
                self.end_headers()
                self.wfile.write(conteudo)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/gerar":
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tamanho).decode("utf-8")
            dados = json.loads(corpo)

            titulo = dados.get("titulo", "Minha Música")
            tags = dados.get("tags", "acoustic pop")
            letra = dados.get("letra", "")
            motor = dados.get("motor", "aimusicapi")
            token_ui = dados.get("token", "").strip()

            ssl_ctx = criar_contexto_ssl()

            # --- MOTOR GOOGLE LYRIA (Gemini API) ---
            if motor in ("google_lyria_pro", "google_lyria_clip"):
                google_key = token_ui or os.getenv("GEMINI_API_KEY", "").strip()
                if not google_key or google_key == "sua_chave_gemini_aqui":
                    self._responder_json({"sucesso": False, "erro": "Informe sua Gemini API Key (Google AI Studio) no campo Token acima ou no .env (GEMINI_API_KEY)."})
                    return

                modelos_tentativa = (
                    ["lyria-3.5", "lyria-3-pro-preview"]
                    if motor == "google_lyria_pro"
                    else ["lyria-3-clip-preview"]
                )

                prompt_completo = (
                    f"Title: {titulo}\n"
                    f"Musical Style & Instrumentation: {tags}\n\n"
                    f"Create a high-fidelity complete song singing the exact lyrics below with matching vocals, rhythm, and arrangement:\n\n"
                    f"{letra}"
                )

                payload_google = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt_completo}],
                        }
                    ]
                }

                headers_google = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": google_key,
                }

                ultimo_erro_g = None
                resp_google = None
                modelo_usado = None

                for mod in modelos_tentativa:
                    try:
                        url_g = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent"
                        req_g = urllib.request.Request(
                            url_g,
                            data=json.dumps(payload_google).encode("utf-8"),
                            headers=headers_google,
                            method="POST",
                        )
                        with urllib.request.urlopen(req_g, timeout=180, context=ssl_ctx) as resp:
                            resp_google = json.loads(resp.read().decode("utf-8"))
                            modelo_usado = mod
                            break
                    except urllib.error.HTTPError as he:
                        ultimo_erro_g = f"Google Erro {he.code} ({mod}): {he.read().decode('utf-8', errors='ignore')}"
                    except Exception as ex:
                        ultimo_erro_g = str(ex)

                if not resp_google:
                    self._responder_json({"sucesso": False, "erro": ultimo_erro_g or "Erro ao chamar Google Lyria API."})
                    return

                # Extrai áudio base64 de inlineData
                audio_b64 = None
                mime_type = "audio/mp3"
                texto_retorno = ""
                try:
                    parts = resp_google.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    for p in parts:
                        if "inlineData" in p:
                            audio_b64 = p["inlineData"].get("data")
                            mime_type = p["inlineData"].get("mimeType", "audio/mp3")
                        elif "text" in p:
                            texto_retorno += p["text"]
                except Exception as ex_parse:
                    self._responder_json({"sucesso": False, "erro": f"Erro ao ler resposta do Lyria: {ex_parse}", "raw": resp_google})
                    return

                if not audio_b64:
                    self._responder_json({"sucesso": False, "erro": f"O modelo {modelo_usado} não retornou áudio. Resposta: {texto_retorno or json.dumps(resp_google)}"})
                    return

                ext = "wav" if "wav" in mime_type.lower() else "mp3"
                nome_limpo = "".join(c for c in titulo if c.isalnum() or c in (" ", "_")).rstrip().replace(" ", "_") or "Musica_Lyria"
                timestamp = int(time.time())
                nome_arquivo = f"{nome_limpo}_Lyria_{timestamp}.{ext}"
                caminho_audio = OUTPUT_DIR / nome_arquivo

                with open(caminho_audio, "wb") as fa:
                    fa.write(base64.b64decode(audio_b64))

                # Salva metadados para a biblioteca
                caminho_meta = OUTPUT_DIR / f"{nome_limpo}_Lyria_{timestamp}.json"
                with open(caminho_meta, "w", encoding="utf-8") as fm:
                    json.dump({
                        "title": titulo,
                        "tags": tags,
                        "lyrics": letra,
                        "motor": f"Google ({modelo_usado})",
                        "arquivo": f"/outputs/{nome_arquivo}",
                    }, fm, ensure_ascii=False, indent=2)

                self._responder_json({
                    "sucesso": True,
                    "motor": f"Google ({modelo_usado})",
                    "audio_url_direto": f"/outputs/{nome_arquivo}",
                    "arquivo_nome": nome_arquivo,
                })
                return

            # --- MOTOR 1: FAL.AI (MiniMax Music v2.6) ---
            if motor == "fal_minimax":
                if not token_ui:
                    self._responder_json({"sucesso": False, "erro": "Informe o seu Token da Fal.ai no campo de API Key acima."})
                    return

                headers_fal = {
                    "Authorization": f"Key {token_ui}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                }
                payload_fal = {
                    "prompt": tags,
                    "lyrics": letra,
                }
                try:
                    req = urllib.request.Request(
                        "https://queue.fal.run/fal-ai/minimax-music/v2.6",
                        data=json.dumps(payload_fal).encode("utf-8"),
                        headers=headers_fal,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                    self._responder_json({"sucesso": True, "motor": motor, "resultado": resp_data})
                except urllib.error.HTTPError as he:
                    self._responder_json({"sucesso": False, "erro": f"Fal.ai Erro {he.code}: {he.read().decode('utf-8', errors='ignore')}"})
                except Exception as e:
                    self._responder_json({"sucesso": False, "erro": str(e)})
                return

            # --- MOTOR 2: FAL.AI (ACE-Step Open Source) ---
            if motor == "fal_acestep":
                if not token_ui:
                    self._responder_json({"sucesso": False, "erro": "Informe o seu Token da Fal.ai no campo de API Key acima."})
                    return

                headers_fal = {
                    "Authorization": f"Key {token_ui}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                }
                payload_ace = {
                    "prompt": tags,
                    "lyrics": letra,
                    "instrumental": False,
                }
                try:
                    req = urllib.request.Request(
                        "https://queue.fal.run/fal-ai/ace-step/prompt-to-audio",
                        data=json.dumps(payload_ace).encode("utf-8"),
                        headers=headers_fal,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                    self._responder_json({"sucesso": True, "motor": motor, "resultado": resp_data})
                except urllib.error.HTTPError as he:
                    self._responder_json({"sucesso": False, "erro": f"Fal.ai Erro {he.code}: {he.read().decode('utf-8', errors='ignore')}"})
                except Exception as e:
                    self._responder_json({"sucesso": False, "erro": str(e)})
                return

            # --- MOTOR 3: AIMUSICAPI (Suno AI) ---
            api_key = token_ui or os.getenv("AI_MUSIC_API_KEY", "").strip()

            if not api_key or api_key == "sua_chave_aqui":
                nome_limpo = "".join(c for c in titulo if c.isalnum() or c in (" ", "_")).rstrip()
                caminho_salvo = OUTPUT_DIR / f"{nome_limpo.replace(' ', '_')}_rascunho.txt"
                with open(caminho_salvo, "w", encoding="utf-8") as f:
                    f.write(f"TÍTULO: {titulo}\nESTILO / TAGS: {tags}\n\nLETRA:\n{letra}")

                self._responder_json({
                    "sucesso": False,
                    "modo": "rascunho",
                    "mensagem": "Chave de API não configurada. O rascunho foi salvo!",
                    "arquivo_salvo": str(caminho_salvo.name),
                })
                return

            headers_api = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }
            payload = {
                "prompt": letra,
                "tags": tags,
                "title": titulo,
                "custom_mode": True,
                "make_instrumental": False,
                "mv": "chirp-v3-5",
            }

            try:
                url_alvo = "https://api.aimusicapi.ai/api/v1/sonic/create"
                req = urllib.request.Request(
                    url_alvo,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers_api,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))

                if isinstance(resp_data, dict) and "redirect" in resp_data:
                    req_red = urllib.request.Request(
                        resp_data["redirect"],
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers_api,
                        method="POST",
                    )
                    with urllib.request.urlopen(req_red, timeout=60, context=ssl_ctx) as resp_red:
                        resp_data = json.loads(resp_red.read().decode("utf-8"))

                self._responder_json({"sucesso": True, "motor": motor, "resultado": resp_data})
            except urllib.error.HTTPError as he:
                self._responder_json({"sucesso": False, "erro": f"Erro {he.code}: {he.read().decode('utf-8', errors='ignore')}"})
            except Exception as e:
                self._responder_json({"sucesso": False, "erro": str(e)})
            return

        self.send_response(404)
        self.end_headers()


def iniciar_servidor():
    os.chdir(Path(__file__).parent)
    endereco = ("", PORT)
    servidor = HTTPServer(endereco, MusicHandler)
    print("=" * 65)
    print(f"🎵 ESTÚDIO DE CRIAÇÃO MUSICAL MULTI-MOTOR INICIADO!")
    print(f"👉 Abra no seu navegador: http://localhost:{PORT}")
    print("=" * 65)
    print("Pressione Ctrl+C para encerrar o servidor.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    iniciar_servidor()
