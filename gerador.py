"""
Gerador de Músicas com Inteligência Artificial
Gera músicas completas com letra, vocais, arranjos e instrumentos usando Suno / AIMusicAPI.ai.
Utiliza apenas a biblioteca padrão do Python (sem dependências externas).
"""

import os
import sys
import ssl
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

GENEROS_SUGERIDOS = {
    "1": {
        "nome": "Rock Brasileiro / Pop Rock",
        "tags": "brazilian pop rock, electric guitar riffs, punchy drums, driving bass, passionate male vocals, 125 bpm",
    },
    "2": {
        "nome": "Bossa Nova / MPB",
        "tags": "bossa nova, smooth nylon acoustic guitar, soft percussion, warm upright bass, gentle female vocals, intimate vibe",
    },
    "3": {
        "nome": "Sertanejo Contemporâneo",
        "tags": "brazilian sertanejo, acoustic steel guitar, accordion solo, modern pop drums, expressive male vocals, emotional",
    },
    "4": {
        "nome": "Synthwave / Retrowave 80s",
        "tags": "synthwave, 1980s analog synthesizers, gated reverb snare, driving arpeggiator, nostalgic atmospheric vocals, 115 bpm",
    },
    "5": {
        "nome": "Pop Acústico / Indie Folk",
        "tags": "indie folk pop, acoustic guitar fingerpicking, handclaps, warm vocal harmonies, uplifting chorus, 100 bpm",
    },
    "6": {
        "nome": "Heavy Metal / Metal Melódico",
        "tags": "melodic heavy metal, fast double bass drums, heavy distorted guitars, epic melodic guitar solo, powerful soaring vocals",
    },
    "7": {
        "nome": "Hip-Hop / Lo-Fi Melódico",
        "tags": "melodic lo-fi hip hop, chill Rhodes piano, soft 808 sub bass, relaxed drum groove, smooth vocal flow, 85 bpm",
    },
}

LETRA_EXEMPLO = """[Verse 1]
O asfalto brilha sob o sol da tarde
O rádio toca uma canção do passado
No retrovisor fica tudo o que arde
O futuro é um caminho a ser desbravado

[Verse 2]
Cortei as amarras que me prendiam
Pisei no acelerador sem olhar pra trás
As velhas dúvidas já não me ferem
A liberdade é o que me satisfaz

[Chorus]
Na estrada sem fim, vou me encontrar
O vento no rosto me faz acreditar
Não há tempestade que possa conter
Quem nasceu com a gana de sobreviver!

[Guitar Solo]

[Bridge]
E quando a noite apagar a cidade
Os faróis mostram a verdade
Eu sou o dono do meu recado

[Chorus]
Na estrada sem fim, vou me encontrar
O vento no rosto me faz acreditar
Não há tempestade que possa conter
Quem nasceu com a gana de sobreviver!

[Outro]
Acelerando pela escuridão...
Seguindo o ritmo do coração."""


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


def obter_configuracoes():
    carregar_env()
    api_key = os.getenv("AI_MUSIC_API_KEY", "").strip()
    base_url = os.getenv("API_BASE_URL", "https://api.aimusicapi.ai").rstrip("/")
    return api_key, base_url


def solicitar_dados_musica():
    print("=" * 65)
    print("  🎵  GERADOR DE MÚSICAS COMPLETAS COM INTELIGÊNCIA ARTIFICIAL  🎵")
    print("=" * 65)

    titulo = input("\n[1] Digite o TÍTULO da música [padrão: Estrada Sem Fim]: ").strip()
    if not titulo:
        titulo = "Estrada Sem Fim"

    print("\n[2] Escolha o GÊNERO MUSICAL:")
    for chave, item in GENEROS_SUGERIDOS.items():
        print(f"    [{chave}] {item['nome']}")
    print("    [8] Personalizado (digitar estilo e instrumentos)")

    opcao_genero = input("\nEscolha uma opção (1-8) [padrão: 1]: ").strip() or "1"

    if opcao_genero in GENEROS_SUGERIDOS:
        genero_escolhido = GENEROS_SUGERIDOS[opcao_genero]["tags"]
        print(f"-> Estilo selecionado: {GENEROS_SUGERIDOS[opcao_genero]['nome']}")
    else:
        genero_escolhido = input(
            "Digite os estilos/instrumentos separados por vírgula: "
        ).strip()
        if not genero_escolhido:
            genero_escolhido = "brazilian pop rock, electric guitar, punchy drums, passionate male vocals, 125 bpm"

    print("\n[3] LETRA DA MÚSICA:")
    print("    [1] Usar letra de exemplo estruturada (Rock de Estrada)")
    print("    [2] Escrever ou colar minha própria letra")

    opcao_letra = input("\nEscolha (1 ou 2) [padrão: 1]: ").strip() or "1"

    if opcao_letra == "2":
        print("\nCole sua letra abaixo. Quando terminar, digite 'FIM' em uma linha vazia:")
        linhas = []
        while True:
            try:
                linha = input()
                if linha.strip().upper() == "FIM":
                    break
                linhas.append(linha)
            except EOFError:
                break
        letra = "\n".join(linhas).strip()
        if not letra:
            print("Nenhuma letra inserida. Usando letra padrão.")
            letra = LETRA_EXEMPLO
    else:
        letra = LETRA_EXEMPLO
        print("-> Usando letra modelo estruturada.")

    return titulo, genero_escolhido, letra


def requisicao_http(url: str, metodo: str = "GET", headers: dict = None, dados: dict = None):
    if headers is None:
        headers = {}

    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    headers["Accept"] = "application/json"

    corpo_bytes = None
    if dados is not None:
        corpo_bytes = json.dumps(dados).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=corpo_bytes, headers=headers, method=metodo)

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl_ctx) as resp:
            conteudo = resp.read().decode("utf-8")
            return json.loads(conteudo)
    except urllib.error.HTTPError as e:
        detalhes = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Erro HTTP {e.code}: {detalhes}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Erro de conexão: {e.reason}")


def criar_musica(api_key: str, base_url: str, titulo: str, tags: str, prompt: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "prompt": prompt,
        "tags": tags,
        "title": titulo,
        "custom_mode": True,
        "make_instrumental": False,
        "mv": "chirp-v3-5",
    }

    print("\n🚀 Enviando solicitação para AIMusicAPI.ai...")
    try:
        return requisicao_http(f"{base_url}/api/v1/producer/create", metodo="POST", headers=headers, dados=payload)
    except Exception:
        return requisicao_http(f"{base_url}/api/v1/sonic/create", metodo="POST", headers=headers, dados=payload)


def extrair_id_tarefa(resposta):
    if isinstance(resposta, dict):
        if "taskId" in resposta:
            return resposta["taskId"]
        if "id" in resposta:
            return resposta["id"]
        if "data" in resposta and isinstance(resposta["data"], dict):
            return resposta["data"].get("taskId") or resposta["data"].get("id")
    elif isinstance(resposta, list) and len(resposta) > 0:
        return resposta[0].get("id") or resposta[0].get("taskId")
    return None


def aguardar_geracao(api_key: str, base_url: str, task_id: str, max_tentativas: int = 40):
    headers = {"Authorization": f"Bearer {api_key}"}
    print(f"\n⏳ Aguardando a síntese de áudio pelo Suno (ID: {task_id})...")

    urls_tentativa = [
        f"{base_url}/api/v1/suno/feed?ids={task_id}",
        f"{base_url}/api/v1/sonic/task/{task_id}",
        f"{base_url}/api/v1/producer/task/{task_id}",
    ]

    for tentativa in range(1, max_tentativas + 1):
        for url_check in urls_tentativa:
            try:
                resp = requisicao_http(url_check, metodo="GET", headers=headers)
                
                # Formato lista direta: [{status, audio_url, ...}]
                if isinstance(resp, list) and len(resp) > 0:
                    item = resp[0]
                    st = item.get("status")
                    audio = item.get("audio_url")
                    print(f"[{tentativa}/{max_tentativas}] Status: {st}...")
                    if st in ("complete", "streaming", "succeeded", "SUCCESS") and audio:
                        return audio

                # Formato envelopado: {data: {status, response: {sunoData: [...]}}}
                if isinstance(resp, dict):
                    data = resp.get("data") or resp
                    st = data.get("status")
                    if st:
                        print(f"[{tentativa}/{max_tentativas}] Status: {st}...")
                    
                    suno_data = (data.get("response") or {}).get("sunoData") or []
                    if suno_data and len(suno_data) > 0:
                        audio = suno_data[0].get("audio_url") or suno_data[0].get("stream_audio_url")
                        if audio:
                            return audio
            except Exception:
                pass

        time.sleep(12)

    raise TimeoutError("Tempo limite excedido aguardando a geração da música.")


def baixar_audio(audio_url: str, nome_arquivo: str):
    caminho = OUTPUT_DIR / nome_arquivo
    print(f"\n💾 Baixando áudio MP3 para: {caminho.resolve()} ...")
    urllib.request.urlretrieve(audio_url, str(caminho))
    print(f"✨ Música salva com sucesso em: {caminho.resolve()}")
    return caminho


def main():
    api_key, base_url = obter_configuracoes()

    titulo, tags, letra = solicitar_dados_musica()

    print("\n" + "=" * 65)
    print("RESUMO DO PROJETO DE MÚSICA:")
    print(f"• Título:       {titulo}")
    print(f"• Estilo/Tags:  {tags}")
    print(f"• Letra:        {len(letra.splitlines())} linhas")
    print("=" * 65)

    try:
        resposta = criar_musica(api_key, base_url, titulo, tags, letra)
        task_id = extrair_id_tarefa(resposta)

        if not task_id:
            print(f"Resposta recebida da API: {json.dumps(resposta, indent=2)}")
            task_id = input("Digite o ID retornado pela API para acompanhar: ").strip()

        audio_url = aguardar_geracao(api_key, base_url, task_id)
        nome_limpo = "".join(c for c in titulo if c.isalnum() or c in (" ", "_")).rstrip()
        nome_arquivo = f"{nome_limpo.replace(' ', '_')}_{str(task_id)[:8]}.mp3"
        baixar_audio(audio_url, nome_arquivo)

    except Exception as e:
        print(f"\n❌ Erro durante o processo: {e}")


if __name__ == "__main__":
    main()
