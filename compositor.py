"""
Compositor de Letras Estruturadas
Fornece templates e letras temáticas completas prontas para gerar no Suno AI.
"""

TEMPLATES_LETRAS = {
    "rock": {
        "titulo": "Estrada Sem Fim",
        "tags": "brazilian pop rock, 1980s barão vermelho style, energetic electric guitar riffs, punchy drums, driving bass, passionate male vocals, 128 bpm",
        "letra": """[Verse 1]
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
Não há destino marcado
Eu sou o dono do meu recado

[Chorus]
Na estrada sem fim, vou me encontrar
O vento no rosto me faz acreditar
Não há tempestade que possa conter
Quem nasceu com a gana de sobreviver!

[Outro]
Acelerando pela escuridão...
Seguindo o ritmo do coração.
(Fade out com solo de guitarra)"""
    },
    "bossa_nova": {
        "titulo": "Café na Chuva",
        "tags": "bossa nova, smooth nylon acoustic guitar, soft brushes on snare, warm upright bass, gentle whispering female vocals, melancholy romantic, 85 bpm",
        "letra": """[Verse 1]
A chuva cai devagar na vidraça
O café esfria enquanto o tempo passa
Lembro do teu sorriso sem compromisso
Deixando no ar um doce feitiço

[Verse 2]
O vento sopra e balança a cortina
Trazendo de volta a tua lembrança
Um dia cinzento que me fascina
Onde a saudade ainda tem esperança

[Chorus]
E assim vai a tarde, num tom menor
Ouvindo o silêncio que se faz melhor
Um violão afinado pra te cantar
Na bossa suave desse meu olhar

[Bridge]
Talvez amanhã o sol queira abrir
E essa canção te faça sorrir

[Outro]
Chuva no café...
Saudade que é...
(Vocal suave em fade out)"""
    },
    "sertanejo": {
        "titulo": "Madrugada e Viola",
        "tags": "brazilian sertanejo, acoustic steel guitar, accordion solo, modern pop drums, expressive emotional male vocals, 105 bpm",
        "letra": """[Verse 1]
Bateu duas da manhã no relógio da parede
O copo vazio não mata essa minha sede
Olho pro celular esperando tocar
Mas sei que dessa vez você não vai ligar

[Verse 2]
A casa tá quieta, o silêncio judia
A cama é grande demais pra essa agonia
Peguei a viola pra desabafar
Cada acorde que sai parece chorar

[Chorus]
E a sanfona chora junto com meu peito
Amar desse jeito não tem mais conserto
Eu tento esquecer mas não tem saída
Você ainda é o vício da minha vida!

[Accordion Solo]

[Bridge]
Se for pra sofrer, que seja cantando
Mas a cada gole eu continuo te amando

[Chorus]
E a sanfona chora junto com meu peito
Amar desse jeito não tem mais conserto
Eu tento esquecer mas não tem saída
Você ainda é o vício da minha vida!

[Outro]
Você ainda é o vício da minha vida...
Ô sofrimento..."""
    },
    "synthwave": {
        "titulo": "Luzes de Neon",
        "tags": "synthwave, 1980s retro analog synths, linndrum gated snare, pulsating bassline, smooth vocoder harmonies, moody night drive, 118 bpm",
        "letra": """[Verse 1]
Cruising down the highway in the midnight glow
Reflections of the neon everywhere I go
Digital horizon calling out my name
In this city of wire, it's a dangerous game

[Chorus]
Neon lights, burning in the dark
Electric pulse straight through my heart
We ride the grid into the endless night
Lost in time beneath the laser light!

[Synth Solo]

[Bridge]
Analog dreams, cassette tapes rewinding
In the shadows of the future, we keep finding

[Chorus]
Neon lights, burning in the dark
Electric pulse straight through my heart
We ride the grid into the endless night
Lost in time beneath the laser light!

[Outro]
Riding the grid...
Lost in the neon...
(Synth arpeggio fade out)"""
    }
}

def listar_modelos():
    print("Modelos de Letras Prontas:")
    for key, item in TEMPLATES_LETRAS.items():
        print(f"- {key}: {item['titulo']}")

if __name__ == "__main__":
    listar_modelos()

