# priemeiros testes com sqlite3, tentando implementar ao meus sistema de votação
# as ideias de banco de dados.


import sqlite3

# CLASSE E BANCO DOS CANDIDATOS A SEREM REGISTRADOS
class Candidatos():
    def __init__(self):
        self.banco_canidatos = sqlite3.connect('candidatos.db')
        self.cursor_canidatos = self.banco_canidatos.cursor()
        self.cursor_canidatos.execute(
            "create table if not exists candidatos (id integer primary key autoincrement, nome text unique not null)")

    # MÉTODOS DA CLASSE CANDIDATOS

    def adiciona_candidato(self, nome):
        try:
            self.cursor_canidatos.execute(f"insert into candidatos (nome) values ('{nome}')")
            self.banco_canidatos.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def remove_candidato(self, nome):
        try:
            self.cursor_canidatos.execute(f"delete from candidatos where nome = '{nome}'")
            self.banco_canidatos.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)


# CLASSE DA VOTAÇÃO (QUE HERDA CANDIDATOS)
class Votacao(Candidatos):
    def __init__(self, nome):
        Candidatos.__init__(self)
        self.nome = nome.translate(str.maketrans('', '', ' '))
        self.banco_votacao = sqlite3.connect(f'{self.nome}.db')
        self.cursor_votacao = self.banco_votacao.cursor()
        self.inicio = False
        # CRIA A TABELA DE VOTAÇÃO COM DADOS DA TABELA CANDIDATOS
        self.cursor_votacao.execute(
            f"create table if not exists {self.nome} (id integer primary key autoincrement,"+
            "nome text unique not null, votos integer default '0',"+
            "constraint fk_nome foreign key (nome) references candidatos(nome))")

    # MÉTODOS DA VOTAÇÃO

    # IMPORTA OS DADOS DE CANDIDATOS APRA DENTRO DA VOTAÇÃO
    def preenche_tabela(self):
        try:
            self.cursor_canidatos.execute('select nome from candidatos')
            interavel = self.cursor_canidatos.fetchall()
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
            self.preenche_tabela()
            self.inicio = True
        try:
            self.cursor_votacao.execute(f"select votos from {self.nome} where nome = '{nome}'")
            votos = self.cursor_votacao.fetchall()[0][0]
            self.cursor_votacao.execute(f"update {self.nome} set votos = '{votos+1}' where nome = '{nome}'")
            self.banco_votacao.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)

    def remove_voto(self, nome):
        try:
            self.cursor_votacao.execute(f"select votos from votacao where nome = '{nome}'")
            votos = self.cursor_votacao.fetchall()[0][0]
            self.cursor_votacao.execute(f"update votacao set votos = '{(votos-1) if votos > 0 else 0}' where nome = '{nome}'")
            self.banco_votacao.commit()
        except sqlite3.Error as erro:
            print('Erro ao executar: ', erro)
    
    def mostra_vencedor(self):
        if not self.inicio:
            try:
                self.cursor_votacao.execute(f"select max(votos) as vencedor from {self.nome}")
                votos = self.cursor_votacao.fetchall()[0][0]
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