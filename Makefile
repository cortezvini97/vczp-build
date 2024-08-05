createbuild:
	@echo "Criando arquivo run-build.sh"
	@echo "#!/bin/bash" > run-build.sh
	@echo "" >> run-build.sh
	@echo "# Função para exibir o uso do script" >> run-build.sh
	@echo "usage() {" >> run-build.sh
	@echo "    echo \"Uso: $$0 --create-env | --configure | --compile | --clean | --install | --createrpm | --resetproject | --uninstall\"" >> run-build.sh
	@echo "    exit 1" >> run-build.sh
	@echo "}" >> run-build.sh
	@echo "" >> run-build.sh
	@echo "# Função para exibir a mensagem de erro de configuração" >> run-build.sh
	@echo "configure_message() {" >> run-build.sh
	@echo "    echo \"O projeto já está configurado corretamente.\"" >> run-build.sh
	@echo "    echo \"Digite 'run-build.sh --clean' para limpar e 'run-build.sh --configure' para configurar novamente.\"" >> run-build.sh
	@echo "}" >> run-build.sh
	@echo "" >> run-build.sh
	@echo "# Verifica o argumento passado" >> run-build.sh
	@echo "case \"\$$1\" in" >> run-build.sh
	@echo "    --create-env)" >> run-build.sh
	@echo "        echo \"Criando e configurando o ambiente virtual...\"" >> run-build.sh
	@echo "        python3 -m venv venv" >> run-build.sh
	@echo "        source venv/bin/activate" >> run-build.sh
	@echo "        pip install --upgrade pip" >> run-build.sh
	@echo "        pip install cython" >> run-build.sh
	@echo "        deactivate" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --configure)" >> run-build.sh
	@echo "        if [ -d \"src\" ] && [ -f \"src/create_vczp.c\" ] && [ -f \"src/main.c\" ]; then" >> run-build.sh
	@echo "            configure_message" >> run-build.sh
	@echo "        else" >> run-build.sh
	@echo "            echo \"Configurando o build...\"" >> run-build.sh
	@echo "            source venv/bin/activate" >> run-build.sh
	@echo "            make build" >> run-build.sh
	@echo "            deactivate" >> run-build.sh
	@echo "        fi" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --compile)" >> run-build.sh
	@echo "        if [ -d \"src\" ] && [ -f \"src/create_vczp.c\" ] && [ -f \"src/main.c\" ]; then" >> run-build.sh
	@echo "            echo \"Começando a compilar...\"" >> run-build.sh
	@echo "            make compile" >> run-build.sh
	@echo "        else" >> run-build.sh
	@echo "            echo \"Erro: O diretório src deve conter os arquivos create_vczp.c e main.c\"" >> run-build.sh
	@echo "            exit 1" >> run-build.sh
	@echo "        fi" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --clean)" >> run-build.sh
	@echo "        echo \"Limpando o diretório projeto...\"" >> run-build.sh
	@echo "        make clean" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --install)" >> run-build.sh
	@echo "        if [ -d \"dist\" ] && [ -f \"dist/libcreate_vczp.so\" ] && [ -f \"dist/vczp-devel\" ]; then" >> run-build.sh
	@echo "            echo \"Instalando...\"" >> run-build.sh
	@echo "            make install" >> run-build.sh
	@echo "            echo 'export LD_LIBRARY_PATH=/usr/local/lib:\$$LD_LIBRARY_PATH' >> ~/.bashrc" >> run-build.sh
	@echo "        else" >> run-build.sh
	@echo "            ./run-build.sh --clean && ./run-build.sh --configure && ./run-build.sh --compile && ./run-build.sh --install" >> run-build.sh
	@echo "        fi" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --createrpm)" >> run-build.sh
	@echo "        if [ -d \"dist\" ] && [ -f \"dist/libcreate_vczp.so\" ] && [ -f \"dist/vczp-devel\" ]; then" >> run-build.sh
	@echo "            echo \"Criando RPM Package...\"" >> run-build.sh
	@echo "            make createRPM" >> run-build.sh
	@echo "        else" >> run-build.sh
	@echo "            ./run-build.sh --clean && ./run-build.sh --configure && ./run-build.sh --compile && ./run-build.sh --createrpm" >> run-build.sh
	@echo "        fi" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --resetproject)" >> run-build.sh
	@echo "        echo \"Resetando o Projeto...\"" >> run-build.sh
	@echo "            make resetproject" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    --uninstall)" >> run-build.sh
	@echo "        echo \"Desinstalando...\"" >> run-build.sh
	@echo "        make uninstall" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "    *)" >> run-build.sh
	@echo "        usage" >> run-build.sh
	@echo "        ;;" >> run-build.sh
	@echo "esac" >> run-build.sh
	@echo "" >> run-build.sh
	@echo "echo \"FIM\"" >> run-build.sh
	make run-build
	@rm -rf run-build.sh
	mv run-build run-build.sh


config:
	@echo "Configurando o build..."
	mkdir -p src
	cp main.py main.pyx
	sed -i 's/import create_vczp/import ctypes/g' main.pyx
	awk '/import ctypes/ { \
	    print "import ctypes\n\ntry:\n    create_vczp = ctypes.CDLL(\"/usr/local/lib/libcreate_vczp.so\")\n    print(\"Biblioteca carregada com sucesso!\")\nexcept OSError as e:\n    print(f\"Erro ao carregar a biblioteca: {e}\")"; \
	    next \
	} \
	{print}' main.pyx > temp.pyx && mv temp.pyx main.pyx
	sed -i 's/\r//' main.pyx
	cp create_vczp.py create_vczp.pyx
build: config
	cython create_vczp.pyx -o src/create_vczp.c
	cython main.pyx -o src/main.c --embed
	rm -f create_vczp.pyx
	rm -f main.pyx

config_compile:
	mkdir -p dist src/build

compile: config_compile
	gcc -c -fPIC -I/usr/include/python3.9 src/create_vczp.c -o src/build/libcreate_vczp.o
	gcc -shared -o dist/libcreate_vczp.so src/build/libcreate_vczp.o
	gcc -o dist/vczp-devel src/main.c -I/usr/include/python3.9 -Ldist -lcreate_vczp -L/usr/lib/ -lpython3.9

install:
	mv dist/libcreate_vczp.so /usr/local/lib/
	mv dist/vczp-devel /usr/local/bin/
	rm -rf dist

uninstall:
	rm -rf /usr/local/lib/libcreate_vczp.so
	rm -rf /usr/local/bin/vczp-devel
	sed -i '/export LD_LIBRARY_PATH=\/usr\/local\/lib:$$LD_LIBRARY_PATH/d' ~/.bashrc
clean:
	rm -rf dist
	rm -rf src
	rm -rf main.pyx
	rm -rf create_vczp.pyx
	rm -rf rpmbuild

resetproject:
	make clean
	rm -rf venv
	rm -rf __pycache__
	rm -rf run-build.sh

createRPM:
	rm -rf ~/rpmbuild
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	rm -rf vczp-devel-1.0.0
	mkdir vczp-devel-1.0.0
	cp ./dist/vczp-devel ./vczp-devel-1.0.0/vczp-devel
	cp ./dist/libcreate_vczp.so ./vczp-devel-1.0.0/libcreate_vczp.so
	tar --create --file ./vczp-devel-1.0.0.tar.gz vczp-devel-1.0.0
	mv ./vczp-devel-1.0.0.tar.gz ~/rpmbuild/SOURCES
	rm -rf vczp-devel-1.0.0
	@echo "Name:           vczp-devel" > ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "Version:        1.0.0" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "Release:        1%{?dist}" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "Summary:        create vczp package" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "BuildArch:      x86_64" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "License:        GPL" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "Source0:        %{name}-%{version}.tar.gz" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "Requires:       bash" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%description" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "VCZP Developement packeage" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%prep" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%setup -q" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%install" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "rm -rf &RPM_BUILD_ROOT" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "mkdir -p &RPM_BUILD_ROOT/usr/local/bin" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "mkdir -p &RPM_BUILD_ROOT/usr/local/lib" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "cp %{name} &RPM_BUILD_ROOT/usr/local/bin" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "cp libcreate_vczp.so &RPM_BUILD_ROOT/usr/local/lib" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%clean" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "rm -rf $RPM_BUILD_ROOT" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%files" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "/usr/local/bin/%{name}" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "/usr/local/lib/libcreate_vczp.so" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%post" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "# Adicione o caminho ao .bashrc se ainda não estiver lá" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "if ! grep -q '/usr/local/lib' /etc/bashrc; then" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "    echo 'export LD_LIBRARY_PATH=&LD_LIBRARY_PATH:/usr/local/lib' >> /etc/bashrc" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "fi" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "source /etc/bashrc" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%postun" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "sed -i '/export LD_LIBRARY_PATH=\&LD_LIBRARY_PATH:\/usr\/local\/lib/d' /etc/bashrc" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "source /etc/bashrc" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "%changelog" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "* Sun AUG  04 2024 Vinicius Cortez <cortezvinicius881@gmail.com> - 1.0.0" >> ~/rpmbuild/SPECS/vczp-devel.spec
	@echo "- First version being packaged" >> ~/rpmbuild/SPECS/vczp-devel.spec
	sed -i 's/&RPM_BUILD_ROOT/$$RPM_BUILD_ROOT/g' ~/rpmbuild/SPECS/vczp-devel.spec
	sed -i 's/&LD_LIBRARY_PATH/$$LD_LIBRARY_PATH/g' ~/rpmbuild/SPECS/vczp-devel.spec
	rpmbuild -bb ~/rpmbuild/SPECS/vczp-devel.spec
	mv ~/rpmbuild/RPMS/x86_64/vczp-devel-1.0.0-1.el9.x86_64.rpm ~/vczp-devel/dist
	rm -rf ~/rpmbuild
