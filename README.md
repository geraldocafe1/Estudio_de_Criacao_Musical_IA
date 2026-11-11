# 🎵 Estúdio de Criação Musical com IA Generativa

<p align="center">
  <img src="assets/capa_musica_1.jpeg" alt="Capa da Música Gerada por IA" width="420" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);"/>
</p>

<p align="center">
  <b>Componha, arranje e produza músicas autorais completas (letra, vocais realistas e instrumentos) utilizando Inteligência Artificial de ponta.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13"/>
  <img src="https://img.shields.io/badge/AI_Engine-Suno_Chirp_v3.5-7C3AED?style=for-the-badge&logo=openai&logoColor=white" alt="Suno AI"/>
  <img src="https://img.shields.io/badge/Interface-Web_Local-10B981?style=for-the-badge&logo=html5&logoColor=white" alt="Web UI"/>
  <img src="https://img.shields.io/badge/Status-Produção_Concluída-brightgreen?style=for-the-badge" alt="Status"/>
</p>

---

## ⚡ O Poder da IA Generativa na Música

A música tradicionalmente exigia estúdios caros, instrumentos físicos, cantores de sessão e mixagem complexa. Hoje, com modelos generativos de áudio como o **Suno AI (Chirp v3.5)**:

* 🎤 **Vocais Humanos Expressivos:** Fonética natural em português, com nuances emocionais, respiração e modulação vocal.
* 🎸 **Arranjos Completos Multi-Instrumentais:** Bateria acústica ou eletrônica com gated reverb, guitarras elétricas com distorção analógica, baixos marcantes, violões de aço e teclados vintage.
* ⏱️ **Músicas com Duração Comercial:** Faixas completas de **quase 4 minutos** com introdução, versos, refrões explosivos, pontes melódicas e solos instrumentais.

---

## 🌟 O Caso de Sucesso: *"Nossa História"*

Este repositório contém a produção real da faixa autoral **"Nossa História"**, uma canção emocionante sobre amor à distância, a ansiedade da viagem, as horas conversando e a despedida onde o *"eu te amo"* ficou entalado na garganta.

<p align="center">
  <img src="assets/capa_musica_1.jpeg" width="280" style="border-radius: 8px; margin: 8px;"/>
  <img src="assets/capa_musica_2.jpeg" width="280" style="border-radius: 8px; margin: 8px;"/>
</p>

### 🎧 Ouça as Faixas Geradas:
* 🔊 **[Versão 1 (3m 56s - Vocal emotivo com pegada de Pop Rock Nacional)](https://files.aimusicapi.ai/stems/e7cf2730-e8bf-4975-a5bc-0bd934bec62e.mp3)**
* 🔊 **[Versão 2 (4m 07s - Arranjo com bateria marcante e coro no refrão)](https://files.aimusicapi.ai/stems/416be0b5-5d55-4668-9324-3e0bfeca95bd.mp3)**

> Os arquivos `.mp3` masterizados também estão disponíveis localmente na pasta [`outputs/`](outputs/).

---

## 📁 Estrutura do Repositório

```text
Estudio_de_Criacao_Musical_IA/
├── web/
│   └── index.html          # Interface visual dark mode para composição no navegador
├── outputs/                # Catálogo de faixas geradas (.mp3, capas e letras)
│   ├── Nossa_Historia_Versao_1.mp3
│   ├── Nossa_Historia_Versao_2.mp3
│   ├── Nossa_Historia_Letra.txt
│   └── resultado_musica.json
├── assets/                 # Imagens e artes para documentação
├── web_app.py              # Servidor local HTTP que orquestra a interface web
├── gerador.py              # Script interativo em linha de comando (Python nativo)
├── compositor.py           # Biblioteca de letras e arranjos estruturados por gênero
├── musica.http             # Requisições REST prontas para a extensão REST Client
├── .env.example            # Modelo de configuração de chaves de API
└── requirements.txt        # Dependências do projeto
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.10 ou superior (testado com sucesso no Python 3.13)
* Git instalado

### 1. Clonar o Repositório
```bash
git clone https://github.com/geraldocafe1/Estudio_de_Criacao_Musical_IA.git
cd Estudio_de_Criacao_Musical_IA
```

### 2. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo e adicione sua chave de API:
```bash
cp .env.example .env
```
Edite o arquivo `.env`:
```env
AI_MUSIC_API_KEY=sua_chave_aqui
API_BASE_URL=https://api.aimusicapi.ai
```

### 3. Iniciar o Estúdio Visual
Execute o servidor embutido (100% desenvolvido em Python padrão, sem exigir bibliotecas pesadas):
```bash
python web_app.py
```
Abra no seu navegador: **`http://localhost:8080`**

---

## 🎛️ Formas de Utilização

### 1. Interface Web (`web_app.py`)
* Escolha de presets com um clique: Pop Rock, Bossa Nova, Sertanejo, Synthwave 80s, Heavy Metal, Lo-Fi, **Gospel (Worship, Pentecostal, Acústico)** e **Violão ➡️ Trap (Beat Switch)**.
* Inserção de blocos de arranjo e meta-tags direcionais com um clique (`[Verse]`, `[Chorus]`, `[Choir]`, `[Intro Violão]`, `[Virada Trap]`, `[Outro]`).
* Player de áudio integrado na página.

### 2. Terminal Interativo (`gerador.py`)
* Fluxo guiado em linha de comando que solicita os dados, processa com a IA e baixa o `.mp3` final direto para `outputs/`.

### 3. VS Code REST Client (`musica.http`)
* Teste requisições diretas à API sem sair do editor. Basta abrir o arquivo e clicar em **Send Request**.

---

## 🎼 Engenharia de Prompt Musical: Dicas de Composição

Para obter a melhor performance do modelo gerativo, a letra deve ser estruturada com tags de dinâmica:

```text
[Verse 1]
(Voz mais suave, tom narrativo)

[Pre-Chorus]
(Aumento gradual da dinâmica e ritmo)

[Chorus]
(Refrão explosivo, vocais dobrados e potência máxima)

[Guitar Solo] ou [Drop]
(Pausa vocal com destaque para os instrumentos)

[Bridge]
(Mudança de tom ou melodia mais reflexiva)

[Outro]
(Fade-out ou encerramento marcante)
```

E no campo de **Tags de Estilo**, combine referências de timbre, ritmo e produção:
```text
brazilian pop rock, electric guitar riffs, punchy drums, driving bass, passionate male vocals, 125 bpm
```

---

## 👤 Autor

Desenvolvido por **Geraldo Café**  
GitHub: [@geraldocafe1](https://github.com/geraldocafe1)

---

<p align="center">
  Feito com 🎵 e IA Generativa.
</p>
