# 🧾 AutoContabil

**AutoContabil** é uma aplicação desktop de automação contábil desenvolvida em **Python (PyQt5)**, com foco em folha de pagamento, holerites e relatórios para contadores e escritórios de contabilidade.

---

## 🛠️ Funcionalidades

- ✅ Cadastro, edição e exclusão de colaboradores
- 📄 Geração automática de folha de pagamento
- 🧾 Emissão de holerite em **PDF com duas vias**
- ⚙️ Cálculo automático de **INSS**, **IRRF** e **FGTS**
- 🧮 Regras de desconto:
  - 🥗 Vale-refeição: até **20%**
  - 🚍 Vale-transporte: até **6% do salário**
- 📊 Relatórios por empresa, CPF, nome e MEI
- 📤 Exportação para **Excel (.xlsx)** e **PDF**
- 🖥️ Instalador com atalho na área de trabalho
- 🛡️ Compatível com Windows 10/11

---

## 📦 Instalação

### 1. Baixe o Instalador

> Arquivo: `AutoContabilInstaller.exe`  
> Recomendação: disponibilize o arquivo via **Google Drive** ou **seu site**.

### 2. Execute o Instalador

- Clique duas vezes em `AutoContabilInstaller.exe`
- Será instalado em: `C:\Program Files (x86)\AutoContabil`
- Um **atalho será criado na área de trabalho**
- O sistema será iniciado automaticamente

> ⚠️ **Importante:** Execute como **Administrador** se for necessário salvar PDFs ou acessar arquivos do sistema.

---

## 💻 Executar em Ambiente de Desenvolvimento

### Requisitos

- Python 3.10 ou superior
- Instalar dependências:

```bash
pip install -r requirements.txt

```

---

## 🏗️ Gerar Executável (.exe)

```bash
pyinstaller --noconfirm --onefile --windowed --name=AutoContabil --icon=installer/icon.ico --add-data "app/database.db;app" --add-data "app/tabs/modelos/holerite_modelo_em_branco.pdf;app/tabs/modelos" run.py
```

> O executável será gerado na pasta `dist/`

---

## 🛠️ Gerar Instalador com Inno Setup

### Pré-requisitos

- Instale o [Inno Setup](https://jrsoftware.org/isinfo.php)
- Copie o executável gerado (`dist/AutoContabil.exe`) para a pasta do instalador

### Estrutura esperada:

```
installer/
├── icon.ico
├── VC_redist.x64.exe
├── setup.iss
├── AutoContabilInstaller.exe (saída)
```

### Compile com o seguinte `setup.iss`:

```ini
[Setup]
AppName=AutoContabil
AppVersion=1.0
DefaultDirName={pf}\AutoContabil
DefaultGroupName=AutoContabil
UninstallDisplayIcon={app}\AutoContabil.exe
OutputDir=.
OutputBaseFilename=AutoContabilInstaller
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\AutoContabil.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app\database.db"; DestDir: "{app}\app"; Flags: ignoreversion
Source: "app\tabs\modelos\holerite_modelo_em_branco.pdf"; DestDir: "{app}\app\tabs\modelos"; Flags: ignoreversion
Source: "installer\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
Name: "{group}\AutoContabil"; Filename: "{app}\AutoContabil.exe"
Name: "{commondesktop}\AutoContabil"; Filename: "{app}\AutoContabil.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais"

[Run]
Filename: "{app}\AutoContabil.exe"; Description: "Executar AutoContabil"; Flags: nowait postinstall skipifsilent
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/quiet /norestart"; Flags: waituntilterminated

```


## 👤 Autor

**Juan Gabriel Rocha Santos**  
📧 juangabrieldev@gmail.com  
🔗 [github.com/Juangabrielrsz](https://github.com/Juangabrielrsz)

---

## 📃 Licença

Este projeto é de uso privado. Todos os direitos reservados.
