# priemeiros testes com sqlite3, tentando implementar ao meus sistema de votação
# as ideias de banco de dados.

from os import remove
import sqlite3

# CLASSE E BANCO DOS CANDIDATOS A SEREM REGISTRADOS
class Candidatos():
    def __init__(self):
        self.banco_candidatos = sqlite3.connect('candidatos.db')
        self.cursor_candidatos = self.banco_candidatos.cursor()
        self.cursor_candidatos.execute(
            "create table if not exists candidatos (id integer primary key autoincrement, nome text unique not null)")

    # MÉTODOS DA CLASSE CANDIDATOS

    def adiciona_candidato(self, nome):
        try:
            self.cursor_candidatos.execute(f"insert into candidatos (nome) values ('{nome}')")
            self.banco_candidatos.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def remove_candidato(self, nome):
        try:
            self.cursor_candidatos.execute(f"delete from candidatos where nome = '{nome}'")
            self.banco_candidatos.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def mostra_candidatos(self):
        try:
            self.cursor_candidatos.execute('select * from candidatos')
            return self.cursor_candidatos.fetchall()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

# CLASSE E BANCO DE DADOS QUE ARMAZENA UNICAMENTE OS VOTANTES.
class Votantes():
    def __init__(self):
        self.banco_votantes = sqlite3.connect('votantes.db')
        self.cursor_votantes = self.banco_votantes.cursor()
        self.cursor_votantes.execute(
            '''create table if not exists votantes (id integer primary key autoincrement,
            quantidade integer not null default '-1')''')
        self.cursor_votantes.execute(f"insert into votantes (quantidade) values ('-1')")
        self.banco_votantes.commit()

    # MÉTODOS DA CLASSE VOTANTES
    def define_votantes(self, quantidade):
        try:
            self.cursor_votantes.execute(f"update votantes set quantidade = '{quantidade}' where id = '1'")
            self.banco_votantes.commit()
        except sqlite3.Error as erro:
            print("Erro ao executar: ", erro)

    def mostra_votantes(self):
        try:
            self.cursor_votantes.execute("select quantidade from votantes")
            mostra = self.cursor_votantes.fetchall()[0][0]
            return int(mostra)
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def diminui_votante(self):
        try:
            votantes = self.mostra_votantes()
            self.cursor_votantes.execute(f"update votantes set quantidade = '{(votantes-1) if votantes > 0 else 0}' where id = '1'")
            self.banco_votantes.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

class Desempate():
    def __init__(self) -> None:
        pass

# CLASSE DA VOTAÇÃO (QUE HERDA CANDIDATOS)
class Votacao(Candidatos, Votantes):
    def __init__(self, nome):
        Candidatos.__init__(self)
        Votantes.__init__(self)
        self.nome = nome.translate(str.maketrans('', '', ' '))
        self.banco_votacao = sqlite3.connect(f'{self.nome}.db')
        self.cursor_votacao = self.banco_votacao.cursor()
        self.inicio = False
        # CRIA A TABELA DE VOTAÇÃO COM DADOS DA TABELA CANDIDATOS
        self.cursor_votacao.execute(
            f'''create table if not exists {self.nome} (id integer primary key autoincrement,
            nome text unique not null, votos integer default '0',
            constraint fk_nome foreign key (nome) references candidatos(nome))''')

    # MÉTODOS DA CLASSE VOTAÇÃO

    def excluir_dados(self):
        self.banco_votacao.close()
        self.banco_votantes.close()
        self.banco_candidatos.close()

        remove("candidatos.db")
        remove(f"{self.nome}.db")
        remove("votantes.db")

    # IMPORTA OS DADOS DE CANDIDATOS APRA DENTRO DA VOTAÇÃO
    def __define_tabela__(self):
        try:
            self.cursor_candidatos.execute('select nome from candidatos')
            interavel = self.cursor_candidatos.fetchall()
            self.cursor_votacao.execute(f'select nome from {self.nome}')
            verificacao = self.cursor_votacao.fetchall()
            for elemento in interavel:
                if elemento not in verificacao:
                    self.cursor_votacao.execute(f"insert into {self.nome} (nome) values ('{elemento[0]}')")
            self.banco_votacao.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def adiciona_voto(self, nome):
        if not self.inicio:
            self.__define_tabela__()
            self.inicio = True
        votantes = int(self.mostra_votantes())
        if votantes > 0 or votantes < 0:
            try:
                self.cursor_votacao.execute(f"select votos from {self.nome} where nome = '{nome}'")
                votos = self.cursor_votacao.fetchall()[0][0]
                self.cursor_votacao.execute(f"update {self.nome} set votos = '{votos+1}' where nome = '{nome}'")
                self.banco_votacao.commit()
                self.diminui_votante()
            except sqlite3.Error as erro:
                print('Erro ao executar: ', erro)
        else: print('Votaçao encerrada: todos os já votaram')

    def remove_voto(self, nome):
        try:
            self.cursor_votacao.execute(f"select votos from votacao where nome = '{nome}'")
            votos = self.cursor_votacao.fetchall()[0][0]
            self.cursor_votacao.execute(f"update votacao set votos = '{(votos-1) if votos > 0 else 0}' where nome = '{nome}'")
            self.banco_votacao.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)
    
    def mostra_vencedor(self):
        if self.inicio or self.mostra_votantes() <= 0:
            try:
                self.cursor_votacao.execute(f"select max(votos) as vencedor from {self.nome}")
                votos = self.cursor_votacao.fetchall()[0][0]
                if votos == 0: raise ValueError
                self.cursor_votacao.execute(f"select nome from {self.nome} where votos = {votos}")
                vencedor = self.cursor_votacao.fetchall()

                if len(vencedor) > 1:
                    print(f"A votação empatou entre: ", end='')
                    for candidatos in vencedor:
                        print(f"{candidatos[0]} ", end='')
                else: print(f"O vencedor foi: {vencedor[0][0]}")

            except sqlite3.Error as erro:
                print('Erro ao executar: ', erro)
        else: print('Ainda não há votos resistrados')