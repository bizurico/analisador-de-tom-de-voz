Analisador de Tom de Voz para Apresentações

Projeto da disciplina de Computação Afetiva (UERN)
Autores: Luís Henrique, Maria Antonia
Orientação: Prof. Raul Paradeda

1. Descrição do Projeto

O Analisador de Tom de Voz é uma aplicação de desktop desenvolvida em Python que atua como um "coach" vocal automatizado para apresentadores. A ferramenta utiliza técnicas de processamento de sinal de áudio e computação afetiva para extrair métricas como Pitch, Jitter, Shimmer e Ritmo da Fala.

O objetivo é fornecer feedback objetivo e comparativo. O sistema guia o utilizador através de duas sessões de gravação ("Antes" e "Depois" do treino), gera relatórios visuais automáticos e oferece dicas práticas de melhoria baseadas na análise acústica da voz.

2. Funcionalidades Principais

Fluxo de Sessão Guiado: Interface intuitiva que conduz o utilizador passo a passo.

Deteção de Hardware: Lista e permite selecionar automaticamente qualquer microfone conectado.

Feedback Visual em Tempo Real: VU Meter (barra de volume) para confirmar a captação de áudio durante a gravação.

Análise Fonética Robusta: Utiliza as bibliotecas Librosa e Parselmouth (Praat) para precisão académica.

Relatórios Automáticos:

Gera feedback qualitativo ("Pontos Positivos" e "Melhorias") com base em limiares psicoacústicos.

Calcula a percentagem de evolução entre as sessões.

Gestão de Dados:

Cria automaticamente pastas organizadas por nome do participante.

Salva os áudios em alta qualidade (.wav).

Captura de Ecrã Automática: Salva o relatório visual como imagem (.png) assim que a análise termina, sem necessidade de ação do utilizador.

3. Métricas Analisadas

O sistema avalia 5 dimensões da fala:

Variação do Pitch (F0 SD): Mede a entonação. Variação alta indica engajamento; baixa indica monotonia.

Jitter Local: Mede a instabilidade da frequência (tremor). Associado a nervosismo.

Shimmer Local: Mede a instabilidade do volume. Associado a tensão ou rouquidão.

Ritmo da Fala: Sílabas por segundo. Deteta fala muito rápida (ansiedade) ou muito lenta (hesitação).

Volume Médio (RMS): Indicador de projeção vocal e confiança.

4. Tecnologias Utilizadas

Linguagem: Python 3.10+

Interface: tkinter (Native GUI), ttk

Áudio: PyAudio (Captura), wave (Armazenamento)

Análise: librosa (DSP), praat-parselmouth (Fonética), numpy

Utilitários: Pillow (Screenshots), threading (Concorrência)

5. Guia de Instalação e Execução

Pré-requisitos

Python 3.10 ou superior instalado.

Git instalado (para clonar o repositório).

Microfone funcional.

Passo a Passo

Clone o repositório:

git clone [https://github.com/bizurico/analisador-tom-voz.git]
cd analisador-tom-voz


Crie um ambiente virtual (Recomendado):

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate


Instale as dependências:

pip install numpy pyaudio pillow librosa praat-parselmouth


(Nota: Se tiver problemas com o PyAudio no Windows, instale o pipwin primeiro: pip install pipwin && pipwin install pyaudio).

Execute a aplicação:

python app.py


6. Como Usar (Fluxo do Utilizador)

Insira o nome do participante na tela inicial.

Selecione o microfone desejado na lista.

Clique em "Iniciar Gravação (Sessão 'Antes')".

Aguarde o countdown de 3 segundos e fale durante o tempo desejado.

Clique em "Parar Gravação". O sistema analisará o áudio e abrirá o relatório automaticamente.

Nota: O relatório é salvo automaticamente como imagem na pasta do participante.

Analise o feedback e feche a janela para prosseguir.

Clique em "Iniciar Sessão 'Depois'" e repita o processo.

O relatório final mostrará a comparação da sua evolução.

Desenvolvido com ❤️ para a UERN.
