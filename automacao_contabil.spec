# automacao_contabil.spec
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('app.tabs.modelos')  # inclui o PDF modelo

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/database.db', 'app'),
        ('app/tabs/modelos/holerite_modelo_em_branco.pdf', 'app/tabs/modelos'),
    ],
    ...
)
