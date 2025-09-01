FROM elixir:1.16-erlang-26

# Install Rust
RUN apt-get update && apt-get install -y curl build-essential pkg-config libssl-dev && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    /bin/bash -lc "rustc -V" && \
    mix local.hex --force && mix local.rebar --force

WORKDIR /app
COPY . .
RUN mix deps.get && mix compile && \
    cd workers/solver_port && \
    /bin/bash -lc "source $HOME/.cargo/env && cargo build --release" && \
    cd /app

CMD ["mix", "run", "examples/lev_demo.exs"]
