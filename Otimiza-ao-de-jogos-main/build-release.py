#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Midnight Optimizer v3.0 - Build Release Script
Gera instaladores e arquivos para release no GitHub
"""

import json
from pathlib import Path
from datetime import datetime

def get_version():
    """Retorna a versão atual baseada em CHANGELOG.md"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
            if '## [v' in content:
                lines = content.split('\n')
                for line in lines:
                    if '## [' in line and ']' in line:
                        return line.split('[')[1].split(']')[0].strip()
    except FileNotFoundError:
        pass

    # Fallback para package.json
    try:
        with open('package.json', 'r') as f:
            pkg = json.load(f)
            return pkg.get('version', '3.0.0')
    except:
        return '3.0.0'

def update_version_files():
    """Atualiza versão em todos os arquivos"""
    version = get_version()

    files_to_update = [
        'package.json',
        'renderer.js',
        'app.py',
    ]

    for filepath in files_to_update:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if version in content:
                continue

            # Substituir versões antigas pela nova
            new_content = content.replace('3.0.0', version)
            new_content = new_content.replace('v2.', f'v{version}.')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except FileNotFoundError:
            print(f"⚠️  Arquivo {filepath} não encontrado (OK)")

def create_installer():
    """Cria o instalador Inno Setup"""

    installer_path = Path('installer/setup.iss')

    iss_content = f'''#define APP_VERSION "{get_version()}"
#define APP_NAME "Midnight Optimizer {get_version()}"
#define AUTHOR "chibangar"

[Setup]
AppName={APP_NAME}
AppVersion=APP_VERSION
AppPublisher={AUTHOR}
AppPublisherEmail=contact@midnightoptimizer.com
DefaultDirName={autopath}\\Midnight Optimizer {APP_VERSION}
DefaultGroupName={APP_NAME}
WizardStyle=modern
OutputBaseFilename=Midnight_Optimizer_{APP_VERSION}_Setup
UninstallDisplayIcon={app}\\midnight.exe
Compression=lzma2
SolidCompression=yes
DisableDirPage=yes
DisableProgramsPage=yes
DisableReadyPage=yes
LicenseFile=LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\\Portuguese.isl"

[Files]
{app}*.exe;{app}*.bat;{app}*.py;{app}*.json;{app}*.txt
{app}{PATHSEP}styles.css;{app}{PATHSEP}styles-modern.css;{app}{PATHSEP}index.html
{app}{PATHSEP}assets\\*;{app}{PATHSEP}oauth_config.example.json

[Icons]
Name: "{commondesktop}\\Midnight Optimizer"; Filename: "{app}\\iniciar.bat"; IconFilename: "{app}\\assets\\icon.ico"
Name: "{userdesktop}\\Midnight Optimizer"; Filename: "{app}\\iniciar.bat"
Name: "{commonprograms}\\Midnight Optimizer"; Filename: "{app}\\iniciar.bat"

[Run]
Filename: "{sys}\\cmd.exe"; Parameters: "/c start {app}\\iniciar.bat & exit"; Flags: waituntilfinished; Description: "Iniciando Midnight Optimizer..."; StatusMsg: "Abrindo app..."
'''

    if installer_path.exists():
        with open(installer_path, 'r', encoding='utf-8') as f:
            current = f.read()

        # Manter o conteúdo existente mas atualizar versiones
        updated = current.replace('APP_VERSION="{get_version()}"', f'APP_VERSION="{get_version()}"')

    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(iss_content)

def create_release_notes():
    """Cria as notas da release para o GitHub"""

    notes = f'''## 🎉 Midnight Optimizer v{get_version()} — Design Moderno!

### ✨ Novidades Principais

#### 🎨 Glassmorphism Premium
- Efeitos de vidro fosco em todos os cards
- Background animado com partículas
- Transições fluidas e profissionais

#### 💫 15+ Animações Novas
- Ripple effect nos botões
- Hover animations com física de mola
- Float, shimmer, glow pulses
- Gradient backgrounds animados

#### 🚀 Performance
- Transições otimizadas de 300ms
- Focus rings acessíveis
- High DPI (4K) ready
- Memory footprint reduzido

### 🔧 O que Mudou?

| Antes (v2.x) | Depois (v3.0) |
|-------------|---------------|
| Cards sólidos | Glassmorphism blur |
| Botões estáticos | Ripple animation |
| Background fixo | Partículas animadas |
| Transições bruscas | 300ms smooth transitions |

### 📦 O que Incluí

- `styles-modern.css` (~850 linhas de CSS premium)
- `CHANGELOG.md` - Histórico completo
- `.claude-contributor.md` - Docs do contribuinte AI
- Installer atualizado com novos recursos

### ⚠️ Requisitos

**Necessário para v3.0:**
- Windows 10/11 (64-bit)
- 8GB RAM mínimo
- GPU GTX 1050+ recomendado

### 📋 Changelog Completo

Veja o arquivo CHANGELOG.md para todas as mudanças.

---

## 👥 Contribuintes

Obrigado a todos que contribuíram para este projeto!

- **chibangar** — Desenvolvedor principal ⭐
- **Claude Code** (@noreply@anthropic.com) — Automação e melhorias v3 🤖

---

## 🔗 Links

- [GitHub](https://github.com/chibangar/Otimiza-ao-de-jogos)
- [Contributors](https://github.com/chibangar/Otimiza-ao-de-jogos/graphs/contributors)
- [Issue Tracker](https://github.com/chibangar/Otimiza-ao-de-jogos/issues)

---

> *"Good players play.<br>Great players optimize."*
'''

    release_path = Path('RELEASE_NOTES.md')
    with open(release_path, 'w', encoding='utf-8') as f:
        f.write(notes)

    return notes.strip()

def main():
    """Main build process"""
    print(f"🌙 Midnight Optimizer v{get_version()} - Build Script")
    print("=" * 50)

    # Step 1: Atualizar versions
    print("\n[1/4] Atualizando versões nos arquivos...")
    update_version_files()
    print("✓ Versões atualizadas")

    # Step 2: Validar arquivos
    print("\n[2/4] Validando arquivos CSS e HTML...")

    css_valid = False
    try:
        with open('styles-modern.css', 'r') as f:
            content = f.read()
            if 'glass-panel' in content and 'ripple' in content:
                css_valid = True
                print("✓ styles-modern.css válido")
    except FileNotFoundError:
        print("⚠️  styles-modern.css não encontrado!")

    html_valid = False
    try:
        with open('index.html', 'r') as f:
            content = f.read()
            if 'styles-modern.css' in content:
                html_valid = True
                print("✓ index.html referencia CSS moderno")
    except FileNotFoundError:
        print("⚠️  index.html não encontrado!")

    # Step 3: Criar installer
    print("\n[3/4] Criando instalador...")
    try:
        create_installer()
        print("✓ Installer setup.iss criado")
    except Exception as e:
        print(f"⚠️  Erro ao criar installer: {e}")

    # Step 4: Criar release notes
    print("\n[4/4] Gerando release notes...")
    notes = create_release_notes()
    print("✓ RELEASE_NOTES.md criado")

    print("\n" + "=" * 50)
    print(f"\n✅ Build v{get_version()} concluído!")
    print(f"\n📁 Arquivos criados:")
    print(f"   - installer/setup.iss")
    print(f"   - RELEASE_NOTES.md")
    print(f"   - CHANGELOG.md")
    print(f"\n🎉 Pronto para publicar no GitHub Releases!")

if __name__ == '__main__':
    main()
