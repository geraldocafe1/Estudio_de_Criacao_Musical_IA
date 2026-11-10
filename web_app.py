"""
Servidor Web Local do Gerador de Músicas
Disponibiliza uma interface visual no navegador para compor e gerar músicas.
Funciona 100% com a biblioteca padrão do Python (sem pacotes adicionais).
"""

import os
import ssl
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

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


class MusicHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Permite carregar o frontend sem problemas de cache
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

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
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"has_api_key": tem_chave}).encode("utf-8"))
            return

        elif self.path.startswith("/api/status-task"):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            task_id = query.get("taskId", [""])[0] or query.get("id", [""])[0]

            api_key = os.getenv("AI_MUSIC_API_KEY", "").strip()
            headers_api = {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            }
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

            rotas_check = [
                f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}",
                f"https://api.musicapi.ai/api/v1/producer/task/{task_id}",
                f"https://api.aimusicapi.ai/api/v1/sonic/task/{task_id}",
                f"https://api.aimusicapi.ai/api/v1/producer/task/{task_id}",
            ]

            resultado_task = None
            for r in rotas_check:
                try:
                    req = urllib.request.Request(r, headers=headers_api, method="GET")
                    with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
                        resultado_task = json.loads(resp.read().decode("utf-8"))
                        break
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resultado_task or {"status": "processing"}).encode("utf-8"))
            return

        elif self.path.startswith("/outputs/"):
            # Serve arquivos de áudio gerados
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/gerar":
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tamanho).decode("utf-8")
            dados = json.loads(corpo)

            titulo = dados.get("titulo", "Minha Música")
            tags = dados.get("tags", "acoustic pop")
            letra = dados.get("letra", "")

            api_key = os.getenv("AI_MUSIC_API_KEY", "").strip()
            base_url = os.getenv("API_BASE_URL", "https://api.aimusicapi.ai").rstrip("/")

            # Se não houver chave real, salva um rascunho em outputs/
            if not api_key or api_key == "sua_chave_aqui":
                nome_limpo = "".join(c for c in titulo if c.isalnum() or c in (" ", "_")).rstrip()
                caminho_salvo = OUTPUT_DIR / f"{nome_limpo.replace(' ', '_')}_rascunho.txt"
                with open(caminho_salvo, "w", encoding="utf-8") as f:
                    f.write(f"TÍTULO: {titulo}\n")
                    f.write(f"ESTILO / TAGS: {tags}\n\n")
                    f.write("LETRA DA MÚSICA:\n")
                    f.write(letra)

                resposta = {
                    "sucesso": False,
                    "modo": "rascunho",
                    "mensagem": "Chave de API não configurada no arquivo .env. O rascunho com o arranjo e letra foi salvo com sucesso!",
                    "arquivo_salvo": str(caminho_salvo.name),
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resposta).encode("utf-8"))
                return

            # Caso haja chave configurada, dispara a chamada à API
            headers_api = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
                ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE

                # Tenta primeiro a rota direta para onde o serviço redireciona
                url_alvo = "https://api.aimusicapi.ai/api/v1/sonic/create"

                req = urllib.request.Request(
                    url_alvo,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers_api,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))

                # Se a resposta contiver redirect (ex: status 308)
                if isinstance(resp_data, dict) and "redirect" in resp_data:
                    url_redirecionada = resp_data["redirect"]
                    req_red = urllib.request.Request(
                        url_redirecionada,
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers_api,
                        method="POST",
                    )
                    with urllib.request.urlopen(req_red, timeout=60, context=ssl_ctx) as resp_red:
                        resp_data = json.loads(resp_red.read().decode("utf-8"))

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"sucesso": True, "resultado": resp_data}).encode("utf-8"))

            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"sucesso": False, "erro": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def iniciar_servidor():
    os.chdir(Path(__file__).parent)
    endereco = ("", PORT)
    servidor = HTTPServer(endereco, MusicHandler)
    print("=" * 65)
    print(f"🎵 ESTÚDIO DE CRIAÇÃO MUSICAL INICIADO!")
    print(f"👉 Abra no seu navegador: http://localhost:{PORT}")
    print("=" * 65)
    print("Pressione Ctrl+C para encerrar o servidor.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    iniciar_servidor()

