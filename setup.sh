mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml

# Forçar a instalação manual das ferramentas de sistema
apt-get update && apt-get install -y cmake build-essential libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
