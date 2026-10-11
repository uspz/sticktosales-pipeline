# Stick To Sales: pipeline de animação

Vídeos verticais (1080x1920, 30 fps) de dicas de vendas com um professor de boneco palito na frente de um quadro branco. O fluxo completo do canal (roteiro, ganchos, legendas, Metricool) está na skill `stick-to-sales-canal`. Este repositório guarda só o código.

## Estrutura
- `prof/cairoc.py`: wrapper ctypes da libcairo do sistema (pip costuma estar bloqueado, não precisa de pycairo).
- `prof/rig2.py`: personagem (pose, IK, mãos, rosto). `prof/perf.py`: atuação (gestos, olhar, andar, boca pelo envelope do áudio).
- `prof/board.py`: desenhos do quadro com animação de "desenhar".
- `prof/align.py <áudio> <roteiro.txt> <saida.json> 65.5`: alinha a narração ao roteiro (9 blocos), encurta pausas e grava `<saida>.wav`.
- `prof/lessonNN.py`: um módulo por lição. Para uma lição nova, copie o último, troque TXT/MARKED/ANCHORS/SLIDE_ITEMS/DUR/draw_item e o `cover()`. Rode sempre de dentro de `prof/`, porque os roteiros são lidos de `../script_vNN_xx.txt`.
  - `python3 lessonNN.py stills PT saida.png 5,12,20 [al.json]` para conferir o layout
  - `python3 lessonNN.py render PT al.json saida.mp4`
  - `python3 lessonNN.py cover PT capa.png`
- `prof/cuts.py render <n> PT <dicas|exemplo> saida.mp4`: cortes de 20–27 s com o gancho na tela (dicionário HOOKS). Procura o alinhamento em `alinhamentos/al<n>_pt.json`.
- `add_cover.sh capa.png video.mp4 saida.mp4`: põe a capa de 0,5 s no início. Só para aulas antigas. As aulas novas abrem com o gancho na tela.
- `add_music.sh video.mp4 saida.mp4 [trilha]`: lo-fi original com ducking. Revezar as trilhas em `trilhas/`. Para criar mais: `python3 lofi2.py saida.wav <seed> <bpm> <prog 0-4> <transpor> <ep|pluck>`.

## Conferência antes de publicar
Extrair frames do meio e do fim de cada bloco (ffmpeg -ss) e olhar. Volume alvo de −13 a −14 LUFS, pico abaixo de −0,4 dB (`ffmpeg -af ebur128=peak=true`). Voz já no primeiro segundo.

## Áudio
PT vem de um site de voz que corta por volta de 76 s, então o roteiro PT tem no máximo 145 palavras e pausa depois de cada frase. EN vem do Kokoro (.wav), com pausa entre parágrafos.
