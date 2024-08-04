# Instruções

## Instruções de Instalação

1. Clone o repositório:

```bash
   git clone https://github.com/cortezvini97/vczp-build.git
```

2. Acesse o diretório do projeto:

````bash
cd vczp-build
````

3. Crie o build:

````bash
make createbuild
````

4. Criar ambiente virtual e instalar Cython:

````bash
./run-build --create-env
````

5. Instale o projeto:

````bash
source run-build --install
source ~/.bashrc
````

## Instruções de Desinstalação

````bash
source run-build --uninstall
source ~/.bashrc
````
## Comandos Manualmente

1. Clone o repositório:

```bash
   git clone https://github.com/cortezvini97/vczp-build.git
```

2. Acesse o diretório do projeto:

````bash
cd vczp-build
````

3. Crie o build:

````bash
make createbuild
````

4. Criar ambiente virtual e instalar Cython:

````bash
./run-build --create-env
````

5. Configurando o projeto:

````bash
./run-build --configure
````

5. compilando o projeto:

````bash
./run-build --compile
````

6. Instale o projeto

````bash
source run-build --install
source ~/.bashrc
````

## Clean And Reset

1. Limpando dados de compilação

````bash
./run-build --clean
````

2. Limpando projeto

````bash
./run-build --resetproject
````

# Usando o Programa

````bash
vczp-devel
````

