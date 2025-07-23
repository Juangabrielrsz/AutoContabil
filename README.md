# 🧾 AutoContabil

**AutoContabil** é uma aplicação desktop de automação contábil desenvolvida em **Python (PyQt5)** com funcionalidades voltadas para gestão de colaboradores, geração de folhas de pagamento e holerites.  

---

## 🛠️ Funcionalidades

- Cadastro, edição e exclusão de colaboradores
- Geração automática de folha de pagamento
- Emissão de holerite em PDF (duas vias)
- Cálculo automático de INSS, IRRF e FGTS
- Regras aplicadas:
  - 🥗 Vale-refeição: desconto máximo de **20%**
  - 🚍 Vale-transporte: desconto máximo de **6% do salário**
- Relatórios com número de colaboradores e MEIs
- Filtros avançados por Nome/CPF e por Empresa
- Exportação para **Excel** e **PDF**
- Instalador para Windows com atalho na área de trabalho

---

## 📦 Instalação

### 1. Baixe o Instalador

> Arquivo: `AutoContabilInstaller.exe`

Disponibilize o instalador para seus usuários (via Google Drive, Dropbox ou site institucional).

### 2. Execute o Instalador

- Clique duas vezes em `AutoContabilInstaller.exe`
- O sistema será instalado em `C:\Program Files\AutoContabil`
- Um **atalho será criado na área de trabalho**
- O programa será iniciado automaticamente após a instalação

---

## 💻 Executar em Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.10+
- Instale as dependências:

```bash
pip install -r requirements.txt
```

### Executar o app:

```bash
python run.py
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

---

## 📁 Estrutura do Projeto

```
automacao_contabil/
├── app/
│   ├── database.db
│   └── tabs/
│       ├── colaborador_dialog.py
│       ├── folhas_geradas_dialog.py
│       ├── gerar_pdf_holerite.py
│       ├── tabs_dp.py
│       ├── tabs_relatorios.py
│       └── modelos/
│           └── holerite_modelo_em_branco.pdf
├── dist/
│   └── AutoContabil.exe
├── installer/
│   ├── icon.ico
│   ├── VC_redist.x64.exe
│   └── AutoContabilInstaller.exe
├── run.py
└── README.md
```

---

## 👤 Autor

**Juan Gabriel Rocha Santos**  
📧 juangabrieldev@gmail.com  
🔗 [github.com/Juangabrielrsz](https://github.com/Juangabrielrsz)

---

## 📃 Licença

Este projeto é de uso privado. Todos os direitos reservados.