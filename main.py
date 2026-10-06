import flet as ft


def main(page: ft.Page):
    page.title = "PizzaDev"
    page.scroll = ft.ScrollMode.AUTO

    estado = {"pizza": "Nenhuma", "tamanho": "M", "quantidade": 1}

    carrinho = []

  
    nome = ft.TextField(label="Nome")
    telefone = ft.TextField(label="Telefone")

    tipo_recebimento = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="retirada", label="Retirada no Local"),
                ft.Radio(value="entrega", label="Entrega (R$ 6,00)"),
            ]
        ),
        value="retirada",
    )

    rua = ft.TextField(label="Rua", visible=False)
    numero = ft.TextField(label="Número", visible=False, width=150)
    bairro = ft.TextField(label="Bairro")
    complemento = ft.TextField(label="Complemento")


    pagamento = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="dinheiro", label="Dinheiro"),
                ft.Radio(value="pix", label="Pix"),
                ft.Radio(value="cartao", label="Cartão"),
            ]
        ),
        value="dinheiro",
    )

    valor_recebido = ft.TextField(label="Valor recebido", visible=True)
    observacao = ft.TextField(
        label="Observação", multiline=True, max_length=120
    )

    def pagamento_mudou(e):
        valor_recebido.visible = pagamento.value == "dinheiro"
        page.update()

    pagamento.on_change = pagamento_mudou

    def recebimento_mudou(e):
        eh_entrega = e.control.value == "entrega"
        rua.visible = eh_entrega
        numero.visible = eh_entrega
        atualizar_carrinho()
        page.update()

    tipo_recebimento.on_change = recebimento_mudou

    def validar_cliente():
        nome.error_text = (
            None if nome.value and nome.value.strip() else "Informe o nome"
        )
        digitos = "".join(c for c in (telefone.value or "") if c.isdigit())
        telefone.error_text = (
            None if len(digitos) in (10, 11) else "Use DDD + número"
        )

    
        if pagamento.value == "dinheiro":
            try:
                val = float(
                    (valor_recebido.value or "").replace(",", ".")
                )
                if val < 110.00:
                    valor_recebido.error_text = (
                        "Valor menor que R$ 110,00"
                    )
                else:
                    valor_recebido.error_text = None
            except ValueError:
                valor_recebido.error_text = "Digite um valor válido"
        else:
            valor_recebido.error_text = None

        page.update()
        return (
            nome.error_text is None
            and telefone.error_text is None
            and valor_recebido.error_text is None
        )

    texto_estado = ft.Text(
        f"Último item editado: Pizza {estado['pizza']} | "
        f"Tamanho: {estado['tamanho']} | "
        f"Qtd: {estado['quantidade']}",
        size=12,
        color=ft.Colors.BLUE_700,
        italic=True,
        weight=ft.FontWeight.BOLD,
    )

    def atualizar_estado_header():
        texto_estado.value = (
            f"Último item editado: Pizza {estado['pizza']} | "
            f"Tamanho: {estado['tamanho']} | "
            f"Qtd: {estado['quantidade']}"
        )

    lista_visual = ft.ListView(spacing=8, expand=True, height=200)

    subtotal_texto = ft.Text(
        "Subtotal: R$ 0,00", size=18, weight=ft.FontWeight.BOLD
    )

    def avancar_etapa(e):
        if len(carrinho) == 0:
            avisar("Seu carrinho está vazio!")
            return
        mostrar_dados_cliente()

    botao_avancar = ft.Button(
        "Avançar",
        disabled=True,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        on_click=avancar_etapa,
    )

    def avisar(texto):
        page.open(ft.SnackBar(content=ft.Text(texto)))

    precos_tabela = {
        "Calabresa": {"M": 32, "G": 42},
        "Muçarela": {"M": 20, "G": 40},
        "Frango": {"M": 30, "G": 39},
        "Portuguesa": {"M": 30, "G": 55},
    }

    def atualizar_carrinho():
        lista_visual.controls.clear()
        subtotal = 0

        for index, item in enumerate(carrinho):
            parcial = item["preco"] * item["qtd"]
            subtotal += parcial

            def criar_funcao_remover(idx):
                return lambda e: remover_item(idx)

            linha_item = ft.Row(
                [
                    ft.Text(
                        f'{item["nome"]} ({item["tamanho"]}) '
                        f'x{item["qtd"]} - R$ {parcial:.2f}'
                    ),
                    ft.Button(
                        "Remover",
                        on_click=criar_funcao_remover(index),
                        color=ft.Colors.RED,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            lista_visual.controls.append(linha_item)

        if tipo_recebimento.value == "entrega":
            subtotal += 6.00
            lista_visual.controls.append(
                ft.Row(
                    [
                        ft.Text(
                            "Taxa de Entrega",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Text(
                            "R$ 6.00",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

        subtotal_texto.value = f"Subtotal: R$ {subtotal:.2f}"
        botao_avancar.disabled = len(carrinho) == 0

        page.update()

    def remover_item(index):
        if 0 <= index < len(carrinho):
            item_removido = carrinho.pop(index)
            atualizar_carrinho()
            avisar(f"Item {item_removido['nome']} removido com sucesso!")

    def limpar_carrinho_confirmado(e, dialogo):
        carrinho.clear()
        page.close(dialogo)
        atualizar_carrinho()
        avisar("Carrinho limpo com sucesso!")

    def confirmar_limpeza(e):
        dialogo = ft.AlertDialog(
            title=ft.Text("Limpar carrinho?"),
            content=ft.Text("Todos os itens serão removidos."),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=lambda e: page.close(dialogo)
                ),
                ft.TextButton(
                    "Confirmar",
                    on_click=lambda e: limpar_carrinho_confirmado(e, dialogo),
                ),
            ],
        )

        page.open(dialogo)

    botao_limpar = ft.Button(
        "Limpar Carrinho", on_click=confirmar_limpeza, color=ft.Colors.RED_700
    )

    titulo = ft.Text("PizzaDev", size=32, weight=ft.FontWeight.BOLD)

    subtitulo = ft.Text(
        "Pizza nunca é uma pergunta, é sempre a resposta.",
        size=22,
        font_family="Arial",
        italic=True,
    )

    subsubtitulo = ft.Text(
        "Whatsapp - (84) 9 6572-9784", size=12, font_family="Arial"
    )

    subssubtitulo = ft.Text(
        "----------------------- Versão didática -----------------------",
        size=8,
        font_family="Arial",
    )

    page.add(
        ft.Container(content=titulo, alignment=ft.Alignment.CENTER),
        ft.Container(content=subtitulo, alignment=ft.Alignment.CENTER),
        ft.Container(content=subsubtitulo, alignment=ft.Alignment.CENTER),
        ft.Container(content=subssubtitulo, alignment=ft.Alignment.CENTER),
        ft.Container(
            content=texto_estado, alignment=ft.Alignment.CENTER, padding=5
        ),
    )

    pizza_escolhida = ft.Text(
        "Nenhuma pizza escolhida", size=18, weight=ft.FontWeight.BOLD
    )

    def escolher_pizza(nome, tamanho_val="M", qtd_val=1):
        if not isinstance(qtd_val, int) or qtd_val < 1 or qtd_val > 10:
            pizza_escolhida.value = (
                "Digite uma quantidade inteira entre 1 e 10."
            )
            pizza_escolhida.color = ft.Colors.RED
            page.update()
            return

        preco_unitario = precos_tabela[nome][tamanho_val]
        item_encontrado = False

        for item in carrinho:
            if item["nome"] == nome and item["tamanho"] == tamanho_val:
                item_encontrado = True
                nova_qtd = item["qtd"] + qtd_val

                if nova_qtd > 10:
                    item["qtd"] = 10
                    pizza_escolhida.value = (
                        f"Atenção: Limite de 10 atingido para {nome} ({tamanho_val})."
                    )
                    pizza_escolhida.color = ft.Colors.ORANGE
                else:
                    item["qtd"] = nova_qtd
                    pizza_escolhida.value = (
                        f"Adicionado mais {qtd_val}x {nome} ({tamanho_val}) ao carrinho!"
                    )
                    pizza_escolhida.color = ft.Colors.GREEN
                break

        if not item_encontrado:
            pizza_escolhida.value = (
                f"{qtd_val}x {nome} ({tamanho_val}) adicionada ao carrinho!"
            )
            pizza_escolhida.color = ft.Colors.GREEN

            carrinho.append(
                {
                    "nome": nome,
                    "tamanho": tamanho_val,
                    "qtd": qtd_val,
                    "preco": preco_unitario,
                }
            )

        estado["pizza"] = nome
        estado["tamanho"] = tamanho_val
        estado["quantidade"] = qtd_val

        atualizar_estado_header()
        atualizar_carrinho()
        page.update()

    def calcular(e, quantidade, tamanho, resultado, preco_m, preco_g):
        valor = (quantidade.value or "").strip()

        if not valor.isdigit():
            resultado.value = "Digite uma quantidade inteira."
            resultado.color = ft.Colors.RED
            page.update()
            return

        qtd = int(valor)

        if qtd < 1 or qtd > 10:
            resultado.value = "Quantidade deve ficar entre 1 e 10."
            resultado.color = ft.Colors.RED
            page.update()
            return

        preco = preco_m if tamanho.value == "M" else preco_g
        total = preco * qtd

        resultado.value = f"Parcial: R$ {total:.2f}"
        resultado.color = ft.Colors.GREEN
        page.update()

    def obter_quantidade(campo):
        valor = (campo.value or "").strip()
        if not valor.isdigit():
            return 0
        return int(valor)

    # Calabresa
    quantidade_calabresa = ft.TextField(
        label="Quantidade", value="1", width=200
    )
    tamanho_calabresa = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="M", label="M (R$ 32,00)"),
                ft.Radio(value="G", label="G (R$ 42,00)"),
            ]
        ),
        value="M",
    )
    resultado_calabresa = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    botao_calcular_calabresa = ft.Button(
        "Calcular Parcial",
        on_click=lambda e: calcular(
            e,
            quantidade_calabresa,
            tamanho_calabresa,
            resultado_calabresa,
            32,
            42,
        ),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )
    botao_escolher_calabresa = ft.Button(
        "Adicionar ao Carrinho",
        on_click=lambda e: escolher_pizza(
            "Calabresa",
            tamanho_calabresa.value,
            obter_quantidade(quantidade_calabresa),
        ),
    )
    card_calabresa = ft.Container(
        padding=15,
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Calabresa", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Calabresa, cebola e queijo"),
                ft.Divider(),
                ft.Text("Tamanho:"),
                tamanho_calabresa,
                quantidade_calabresa,
                ft.Row([botao_calcular_calabresa, botao_escolher_calabresa]),
                resultado_calabresa,
            ]
        ),
    )

    # Muçarela
    quantidade_mucarela = ft.TextField(
        label="Quantidade", value="1", width=200
    )
    tamanho_mucarela = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="M", label="M (R$ 20,00)"),
                ft.Radio(value="G", label="G (R$ 40,00)"),
            ]
        ),
        value="M",
    )
    resultado_mucarela = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    botao_calcular_mucarela = ft.Button(
        "Calcular Parcial",
        on_click=lambda e: calcular(
            e,
            quantidade_mucarela,
            tamanho_mucarela,
            resultado_mucarela,
            20,
            40,
        ),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )
    botao_escolher_mucarela = ft.Button(
        "Adicionar ao Carrinho",
        on_click=lambda e: escolher_pizza(
            "Muçarela",
            tamanho_mucarela.value,
            obter_quantidade(quantidade_mucarela),
        ),
    )
    card_mucarela = ft.Container(
        padding=15,
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Muçarela", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Muçarela, molho e cebola"),
                ft.Divider(),
                ft.Text("Tamanho:"),
                tamanho_mucarela,
                quantidade_mucarela,
                ft.Row([botao_calcular_mucarela, botao_escolher_mucarela]),
                resultado_mucarela,
            ]
        ),
    )

    # Frango
    quantidade_frango = ft.TextField(label="Quantidade", value="1", width=200)
    tamanho_frango = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="M", label="M (R$ 30,00)"),
                ft.Radio(value="G", label="G (R$ 39,00)"),
            ]
        ),
        value="M",
    )
    resultado_frango = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    botao_calcular_frango = ft.Button(
        "Calcular Parcial",
        on_click=lambda e: calcular(
            e, quantidade_frango, tamanho_frango, resultado_frango, 30, 39
        ),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )
    botao_escolher_frango = ft.Button(
        "Adicionar ao Carrinho",
        on_click=lambda e: escolher_pizza(
            "Frango",
            tamanho_frango.value,
            obter_quantidade(quantidade_frango),
        ),
    )
    card_frango = ft.Container(
        padding=15,
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Frango", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Frango, catupiry e cebola"),
                ft.Divider(),
                ft.Text("Tamanho:"),
                tamanho_frango,
                quantidade_frango,
                ft.Row([botao_calcular_frango, botao_escolher_frango]),
                resultado_frango,
            ]
        ),
    )

    # Portuguesa
    quantidade_portuguesa = ft.TextField(
        label="Quantidade", value="1", width=200
    )
    tamanho_portuguesa = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="M", label="M (R$ 30,00)"),
                ft.Radio(value="G", label="G (R$ 55,00)"),
            ]
        ),
        value="M",
    )
    resultado_portuguesa = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    botao_calcular_portuguesa = ft.Button(
        "Calcular Parcial",
        on_click=lambda e: calcular(
            e,
            quantidade_portuguesa,
            tamanho_portuguesa,
            resultado_portuguesa,
            30,
            55,
        ),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )
    botao_escolher_portuguesa = ft.Button(
        "Adicionar ao Carrinho",
        on_click=lambda e: escolher_pizza(
            "Portuguesa",
            tamanho_portuguesa.value,
            obter_quantidade(quantidade_portuguesa),
        ),
    )
    card_portuguesa = ft.Container(
        padding=15,
        border_radius=12,
        content=ft.Column(
            [
                ft.Text("Portuguesa", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Ovo, queijo, cebola, presunto e tomate"),
                ft.Divider(),
                ft.Text("Tamanho:"),
                tamanho_portuguesa,
                quantidade_portuguesa,
                ft.Row(
                    [botao_calcular_portuguesa, botao_escolher_portuguesa]
                ),
                resultado_portuguesa,
            ]
        ),
    )

    area_central = ft.Container(padding=10)

    def mostrar_inicio():
        atualizar_estado_header()
        area_central.content = ft.Column(
            [
                ft.Text("Início", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Bem-vindo ao aplicativo PizzaDev!"),
                ft.Row(
                    [
                        ft.Button(
                            "Abrir Cardápio",
                            on_click=lambda e: mostrar_cardapio(),
                        ),
                        ft.Button(
                            "Ver Carrinho",
                            on_click=lambda e: mostrar_selecao(),
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                    ]
                ),
            ]
        )
        area_central.update()

    def mostrar_cardapio():
        atualizar_estado_header()
        area_central.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Cardápio", size=24, weight=ft.FontWeight.BOLD),
                        ft.Button(
                            "Voltar", on_click=lambda e: mostrar_inicio()
                        ),
                        ft.Button(
                            "Ver Carrinho",
                            on_click=lambda e: mostrar_selecao(),
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                    ]
                ),
                ft.Container(
                    content=pizza_escolhida,
                    alignment=ft.Alignment.CENTER,
                    padding=10,
                ),
                card_calabresa,
                card_mucarela,
                card_frango,
                card_portuguesa,
                ft.Row(
                    [
                        ft.Button(
                            "Voltar para Início",
                            on_click=lambda e: mostrar_inicio(),
                        ),
                        ft.Button(
                            "Ver Carrinho",
                            on_click=lambda e: mostrar_selecao(),
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                    ]
                ),
            ]
        )
        area_central.update()

    def mostrar_dados_cliente():
        atualizar_estado_header()
        area_central.content = ft.Column(
            [
                ft.Text(
                    "Dados do Cliente, Entrega e Pagamento",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                nome,
                telefone,
                ft.Text("Tipo de Recebimento:"),
                tipo_recebimento,
                rua,
                numero,
                bairro,
                complemento,
                ft.Text("Forma de Pagame:"),
                pagamento,
                valor_recebido,
                observacao,
                ft.Row(
                    [
                        ft.Button(
                            "Voltar ao Carrinho",
                            on_click=lambda e: mostrar_selecao(),
                        ),
                        ft.Button(
                            "Finalizar Pedido",
                            on_click=lambda e: finalizar_pedido(e),
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                        ),
                    ]
                ),
            ]
        )
        area_central.update()

    def finalizar_pedido(e):
        if validar_cliente():
            avisar("Pedido finalizado com sucesso!")

    def mostrar_selecao():
        atualizar_estado_header()
        atualizar_carrinho()

        area_central.content = ft.Column(
            [
                ft.Text(
                    "Seu Carrinho de Compras", size=24, weight=ft.FontWeight.BOLD
                ),
                ft.Container(
                    padding=15,
                    border_radius=8,
                    border=ft.Border.all(1, ft.Colors.BLUE_200),
                    content=ft.Column(
                        [lista_visual, ft.Divider(), subtotal_texto]
                    ),
                ),
                ft.Container(
                    padding=15,
                    border_radius=8,
                    border=ft.Border.all(1, ft.Colors.GREY_400),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Último item editado:", color=ft.Colors.GREY_600
                            ),
                            ft.Text(
                                f"Pizza em Estado: {estado['pizza']}", size=14
                            ),
                            ft.Text(
                                f"Tamanho Guardado: {estado['tamanho']}",
                                size=14,
                            ),
                            ft.Text(
                                f"Quantidade Guardada: {estado['quantidade']}",
                                size=14,
                            ),
                        ]
                    ),
                ),
                ft.Row([botao_limpar, botao_avancar]),
                ft.Row(
                    [
                        ft.Button(
                            "Voltar ao Cardápio",
                            on_click=lambda e: mostrar_cardapio(),
                        ),
                        ft.Button(
                            "Voltar ao Início",
                            on_click=lambda e: mostrar_inicio(),
                        ),
                    ]
                ),
            ]
        )

        area_central.update()

    page.add(area_central)
    mostrar_inicio()


ft.run(main)