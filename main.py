# Importa a Biblioteca Kivy para trabalhar as informações. Importações especificas
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from kivy.lang import Builder
from kivy.core.window import Window

# Biblioteca para leitura e manipulação de informações no formato .json
import json

# Biblioteca para acessar conteúdo web
import requests

# Bibloteca para envio de mensagem na tela do usuário.
import ctypes  # An included library with Python install.

# Bilioteca para salvar informações de data e hora da pesquisa realizada
import datetime

# Começa com uma tela menor e que o tamanho atual além de cor cinza, mantendo o formato original
Window.clearcolor = (0.5, 0.5, 0.5, 1)
#Window.clearcolor = (1, 1, 1, 1)
Window.size = (700, 350)


# noinspection PyUnreachableCode
class TelaPesquisa(Widget):
    cnpj = ObjectProperty(None)

    # Adicionando um método para o botão Pesquisar realizar a tarefa
    def btn(self):

        # Se o usuário informar mais de 1 CNPJ, separar os CNPJs em uma matriz
        cnpj = self.cnpj.text.split(';')

        # Iniciando a váriavel que será usada na mensagem após o for
        qtde_busca = 0

        # iniciando o loop conforme quantidade de CNPJ informado.
        for x in cnpj:

            """
            Falta incluir o código para pausa de 1 min para cada 3 consultas.
            O permitido pela RFDB(Receita Fed..) com custo gratuito
            """

            # Chamando a função para validar o campo CNPJ
            if not TelaPesquisa.validacao(x):
                break

            # Realiza o incremento para informar a quantidade de CNPJ's pesquisados.
            qtde_busca += 1

            # Realiza a busca no Web Service da receita federal com a biblioteca requisição
            r = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{x}')

            # Verifica se o status da requisição foi aceita
            if r.status_code == 200:

                # Salva o texto formato .json em uma variável manipulavel
                pesquisa = json.loads(r.content)

                # Realiza uma conferência se retorno de erro na consulta, e informa o usuário onde está o problema.
                # Caso encontre um CNPJ inválido mesmo com 14 posições.
                if pesquisa['status'] == 'ERROR':
                    ctypes.windll.user32.MessageBoxW(0, f'O Item: {x}  na posição {qtde_busca} Não corresponde a um CNPJ válido. Verifique', 'Informativo', 1)
                    qtde_busca -= 1
                    break

                # Adiconando apenas as informações que preciso. Se der um print(pesquisa) será exibido toda informação
                # retornada no arquivo .json
                atividade_principal = pesquisa['atividade_principal']
                nome_empresarial = pesquisa['nome']
                email = pesquisa['email']
                fantasia = pesquisa['fantasia']
                tipo = pesquisa['tipo']
                situacao = pesquisa['situacao']
                datapesquisa = datetime.datetime.now()

                # Salvando o resultado da consulta em um arquivo .txt na mesma pasta da aplicação
                f = open('ResultadoPesquisa.txt', 'a')
                f.write(
                    f'Nome Empresa: {nome_empresarial}\n'
                    f'Atividade Principal: {atividade_principal}\n'
                    f'Email: {email}\n'
                    f'Nome Fantasia: {fantasia}\n'
                    f'Tipo: {tipo}\n'
                    f'Situação: {situacao}\n'
                    f'Data e Hora Pesquisa: {datapesquisa}\n' + '\n')
                f.close()

                # Fecha a variável de requisição, para naõ ocorrer erro no tratamento.
                r.close()

        # Exibindo mensagem de sucesso, caso realize pelo menos 1 pesquisa.
        if qtde_busca > 0:
            ctypes.windll.user32.MessageBoxW(0,
                                             f' {qtde_busca} CNPJ(s) pesquisado(s). \n\nResultado salvo em: ResultadoPesquisa.txt',
                                             'Informativo', 1)

        # Após realizar o processo, limpa a caixa de texto.
        self.cnpj.text = ""

    # Metodo para validar o campo CNPJ
    @staticmethod
    def validacao(valida):

        # Variavel de controle após verificação
        continua = True

        """
        1° Condição, se campo vazio; 
        2° Condição, se não tem 14 caracteres informados para cada lista; 
        3° Condição, se não foram informados números.
        """
        if valida == '':
            ctypes.windll.user32.MessageBoxW(0, f' Campo Vazio, verifique', 'Informativo', 1)
            continua = False
        else:
            if len(valida) != 14:
                ctypes.windll.user32.MessageBoxW(0, f'O Item: {valida}  não possui 14 digitos, verifique', 'Informativo', 1)
                continua = False
            else:
                if not int(valida.isdigit()):
                    ctypes.windll.user32.MessageBoxW(0, f'O Item: {valida} não é CNPJ válido, verifique.', 'Informativo', 1)
                    continua = False

        # Retorna a variável de controle.
        return continua


class MyApp(App):

    def build(self):
        return Builder.load_file("TelaPesquisa.kv")


if __name__ == "__main__":
    MyApp().run()
