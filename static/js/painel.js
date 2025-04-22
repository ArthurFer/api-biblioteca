const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  carregarUsuarios();

  const formLivro = document.getElementById("formCadastrarLivro");
  if (formLivro) {
    formLivro.addEventListener("submit", cadastrarLivro);
  }

  const formEmprestimo = document.getElementById("formEmprestimoLivro");
  if (formEmprestimo) {
    formEmprestimo.addEventListener("submit", emprestarLivro);
  }

  const formDevolucao = document.getElementById("formDevolucaoLivro");
  if (formDevolucao) {
    formDevolucao.addEventListener("submit", devolverLivroForm);
  }

  const formAtualizar = document.getElementById("formAtualizarLivro");
  if (formAtualizar) {
    formAtualizar.addEventListener("submit", atualizarLivro);
  }
});

function mostrarFormulario(aba) {
    // Oculta todos os formulários
    document.querySelectorAll(".formulario").forEach((form) => form.style.display = "none");

    // Oculta a aba de devolução e o container de livros
    document.getElementById("aba-devolucao").style.display = "none";
    document.getElementById("containerLivros").style.display = "none";

    if (aba === "devolucao") {
      document.getElementById("aba-devolucao").style.display = "block";
      carregarEmprestimosAtivos();
    } else {
      document.getElementById(`formulario${capitalize(aba)}`).style.display = "block";
      document.getElementById("containerLivros").style.display = "block";
    }
  }

function capitalize(texto) {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}


document.getElementById("formCadastrarLivro").addEventListener("submit", function(event) {
    event.preventDefault();

    const livroData = {
        titulo: document.getElementById("titulo").value,
        autor: document.getElementById("autor").value,
        isbn: document.getElementById("isbn").value,
        quantidade: parseInt(document.getElementById("quantidade").value, 10),
        localizacao: document.getElementById("localizacao").value
    };

    fetch(`${API_URL}/livros`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(livroData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                console.log("Erro de resposta:", err); // Log para ver o erro completo
                throw new Error(err.detail || "Erro desconhecido ao cadastrar livro");
            });
        }
        return response.json();
    })
    .then(data => {
        alert("Livro cadastrado com sucesso!");
    })
    .catch(error => {
        console.error("Erro ao cadastrar livro:", error);
        alert("Erro ao cadastrar livro: " + (error.message || error));
    });
});


document.getElementById("formEmprestimoLivro").addEventListener("submit", function(event) {
    event.preventDefault();

    const emprestimoData = {
        livro_id: document.getElementById("livro_id").value, // Setado manualmente
        usuario_id: document.getElementById("usuario_id").value // Agora pega o ID do usuário da combobox
    };

    fetch(`${API_URL}/emprestimos`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(emprestimoData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || "Erro desconhecido ao emprestar livro");
            });
        }
        return response.json();
    })
    .then(data => {
        alert("Empréstimo realizado com sucesso!");
    })
    .catch(error => {
        console.error("Erro ao realizar empréstimo:", error);
    });
});

document.getElementById("formDevolucaoLivro").addEventListener("submit", function(event) {
    event.preventDefault();

    const devolucaoData = {
        livro_id: document.getElementById("livro_id").value,
        usuario_id: document.getElementById("usuario_id").value
    };

    fetch(`${API_URL}/devolucoes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(devolucaoData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || "Erro desconhecido ao devolver livro");
            });
        }
        return response.json();
    })
    .then(data => {
        alert("Devolução realizada com sucesso!");
    })
    .catch(error => {
        console.error("Erro ao realizar devolução:", error);
    });
});

async function carregarEmprestimosAtivos() {
    const resposta = await fetch(`${API_URL}/emprestimos/ativos`);
    const emprestimos = await resposta.json();

    const lista = document.getElementById("lista-emprestimos");
    lista.innerHTML = "";

    emprestimos.forEach((e) => {
      const div = document.createElement("div");

      const dataFormatada = new Date(e.data_emprestimo).toLocaleDateString("pt-BR", {
        day: '2-digit', month: '2-digit', year: 'numeric'
      });

      div.innerHTML = `
        <strong>Usuário:</strong> ${e.nome_usuario} |
        <strong>Livro:</strong> ${e.titulo_livro} |
        <strong>Data:</strong> ${dataFormatada}
        <button onclick="devolverLivro(${e.usuario_id}, ${e.livro_id})">Devolver</button>
      `;

      lista.appendChild(div);
    });
  }


  async function devolverLivro(usuario_id, livro_id) {
    const resposta = await fetch(`${API_URL}/emprestimos/devolver`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ usuario_id, livro_id })
    });

    if (resposta.ok) {
      alert("Livro devolvido com sucesso!");
      carregarEmprestimosAtivos();
    } else {
      const erro = await resposta.json();
      alert(`Erro ao devolver: ${erro.detail}`);
    }
  }

document.getElementById("formAtualizarLivro").addEventListener("submit", function(event) {
    event.preventDefault();

    const isbn = document.getElementById("isbnAtualizar").value;
    const novaQuantidade = parseInt(document.getElementById("quantidadeAtualizar").value);
    const novaLocalizacao = document.getElementById("localizacao").value;

    fetch(`${API_URL}/livros/atualizar/${isbn}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ quantidade: novaQuantidade, localizacao: novaLocalizacao })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Erro ao atualizar o livro");
        }
        return response.json();
    })
    .then(data => {
        alert("Quantidade atualizada com sucesso!");
    })
    .catch(error => {
        console.error("Erro ao atualizar livro:", error);
        alert("Falha ao atualizar o livro. Verifique o ISBN.");
    });
});


function carregarTabelaLivros() {
    const tbody = document.querySelector("#tabelaLivros tbody");
    tbody.innerHTML = ""; // ← primeiro limpa

    fetch(`${API_URL}/livros/listar`)
    .then(response => {
        if (!response.ok) {
            throw new Error("Falha na resposta da API: " + response.status);
        }
        return response.json();
    })
    .then(livros => {
        livros.forEach(livro => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${livro.id}</td>
                <td>${livro.titulo}</td>
                <td>${livro.autor}</td>
                <td>${livro.isbn}</td>
                <td>${livro.quantidade}</td>
                <td>${livro.disponivel ? "Sim" : "Não"}</td>
                <td>${livro.localizacao}</td>
                <td>${new Date(livro.data_cadastro).toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error("Erro ao carregar livros:", error);
        alert("Erro ao carregar livros: " + error.message); // Mostra o erro na interface para o usuário
    });
}

// Chamar ao carregar a página
document.addEventListener("DOMContentLoaded", carregarTabelaLivros);

function carregarUsuarios() {
    fetch(`${API_URL}/usuarios`)
      .then(response => response.json())
      .then(usuarios => {
        const select = document.getElementById("usuario_id");
        select.innerHTML = ""; // Limpa antes de adicionar novos

        usuarios.forEach(usuario => {
          const option = document.createElement("option");
          option.value = usuario.id;           // Isso será enviado no formulário
          option.textContent = usuario.username;   // Isso será exibido na tela
          select.appendChild(option);
        });
      })
      .catch(error => {
        console.error("Erro ao carregar usuários:", error);
      });
  }

// Chama a função para carregar os usuários ao carregar a página
document.addEventListener("DOMContentLoaded", carregarUsuarios);