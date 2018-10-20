# Hands #

Sistema para importação de vendas, tratamento e apresentação dos dados.



## Geral
* Repositório: [github.com/marcuslealsantos/hands](https://github.com/marcuslealsantos/hands/)
* Python: 3.5
* DB:sqlite3 


## Instalação
* [Projeto no Jive](https://portalitm.jiveon.com/groups/smart-th)
 

## Layout
* https://startbootstrap.com/template-overviews/sb-admin/
* https://www.highcharts.com/


### Base local ###
Inserir arquivo Visita.csv em /visits/jobs para testar a importação:
Para criar uma massa de testes, rode o seguinte commando:

    $ python manage.py visits
    
Obs: Não é necessário rodar o job de importação de visitas,
a base já vem importada no arquivo db.sqlite3 na raíz do projeto.
