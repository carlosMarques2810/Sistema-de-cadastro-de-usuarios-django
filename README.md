# Sistema de Cadastro de Usuários

Este projeto é um sistema de cadastro de usuários desenvolvido com Django. Ele permite o gerenciamento de usuários com funcionalidades como CRUD, ativaçao de conta, recuperação de acesso por e-mail, controle de acesso com middleware e uma interface grafica intuitiva.

## Funcionalidades

-**Cadastro de Usuários:** Os usuários podem se registrar fornecendo nome, e-mail e senha.
-**CRUD Completo:** Criar, visualizar, editar e excluir seu perfil.
-**Ativação de Conta:** O usuário recebe, após o seu registror, um e-mail com um link de ativação, implementado via signal do **Django**.
-**Recuperação de Acesso:** Caso o usuário esqueça a senha, pode solicitar um link de recuperação que é enviado por e-mail.
-**Controle de Acesso com Middleware:** Garante que apenas usuários autenticados acessem determinadas áreas.
-**Interface Gráfica:** O sistema possue uma UI amigável, que responde com messagens a cada ação do usuário, facilitando sua navegação.

## Tecnologias Utilizadas

-**Djando**  - Framework web para desenvolvimento rápido e seguro.
-**Python:** - Linguagem de programação principal.
-**Sqlite:** - Banco de dados utilizado (padrão do python).
-**Tailwind CSS:** - Estilização básica dos templates.

##**Observação:** O sistema possui uma view chamada `superuser`, acessivel pela url `http://localhost:account/superuser/`, que gera um Superusuário fornecendo acesso a **Área administrativa do Django**. Após a criação e realização de login, com as credencias fornecidas, o usuário pode alterar esses dados no proprio sistema.
> O usuário gerado terá as seguintes credencias padrão:
> - **username:** - `superuser`
> - **e-mail**: - `superuser@email.com`
> - **password**: - `superuser1234`