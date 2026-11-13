(() => {
  "use strict";

  const reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Cabeçalho: ganha sombra depois que a página rola. */
  const cabecalho = document.querySelector("[data-header]");

  if (cabecalho) {
    let agendado = false;

    const atualizarCabecalho = () => {
      cabecalho.classList.toggle("is-scrolled", window.scrollY > 8);
      agendado = false;
    };

    window.addEventListener("scroll", () => {
      if (!agendado) {
        agendado = true;
        window.requestAnimationFrame(atualizarCabecalho);
      }
    }, { passive: true });

    atualizarCabecalho();
  }

  /* Executa uma ação quando o elemento aparece na tela, uma vez só. */
  const aoAparecer = (elemento, acao, limite = 0.25) => {
    if (!("IntersectionObserver" in window)) {
      acao();
      return;
    }

    const observador = new IntersectionObserver((entradas) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          acao();
          observador.disconnect();
        }
      });
    }, { threshold: limite });

    observador.observe(elemento);
  };

  /* Linha pontilhada dos três passos. */
  const listaPassos = document.querySelector(".step-list");

  if (listaPassos) {
    aoAparecer(listaPassos, () => listaPassos.classList.add("is-lit"), 0.2);
  }

  /* Fluxo da arquitetura: acende um nó por vez. */
  const fluxo = document.querySelector(".arch-flow");

  if (fluxo) {
    const nos = Array.from(fluxo.querySelectorAll(".arch-node"));

    aoAparecer(fluxo, () => {
      if (reduzirMovimento) {
        nos.forEach((no) => no.classList.add("is-lit"));
        return;
      }

      nos.forEach((no, indice) => {
        window.setTimeout(() => no.classList.add("is-lit"), indice * 160);
      });
    }, 0.3);
  }

  /* Agenda de exemplo: uma atividade é concluída e volta a pendente.
     O ciclo para quando o card sai da tela ou a aba fica escondida. */
  const itemDemo = document.querySelector("[data-agenda-demo]");
  const contador = document.querySelector("[data-agenda-count]");
  const selo = document.querySelector("[data-agenda-badge]");

  if (itemDemo && contador && selo && !reduzirMovimento) {
    let timer = null;
    let ativo = false;
    let visivel = false;
    let concluida = false;

    const aplicarEstado = (novoEstado) => {
      concluida = novoEstado;
      itemDemo.classList.toggle("is-done", concluida);
      selo.textContent = concluida ? "Concluída" : "Pendente";
      selo.classList.toggle("agenda-badge--done", concluida);
      selo.classList.toggle("agenda-badge--pending", !concluida);
      contador.textContent = concluida ? "2" : "3";
    };

    const agendar = (atraso) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        aplicarEstado(!concluida);
        agendar(concluida ? 4200 : 3600);
      }, atraso);
    };

    const iniciar = () => {
      if (ativo) {
        return;
      }

      ativo = true;
      agendar(2400);
    };

    const parar = () => {
      ativo = false;
      window.clearTimeout(timer);
    };

    const observador = new IntersectionObserver((entradas) => {
      visivel = entradas[0].isIntersecting;

      if (visivel && !document.hidden) {
        iniciar();
      } else {
        parar();
      }
    }, { threshold: 0.35 });

    observador.observe(itemDemo);

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        parar();
      } else if (visivel) {
        iniciar();
      }
    });
  }
})();
