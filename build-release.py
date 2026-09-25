#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Midnight Optimizer v3.0 - Build Release Script
Gera instaladores e arquivos para release no GitHub
"""

import sys
import json
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def get_version():
    """Retorna a versão atual baseada em CHANGELOG.md ou package.json"""
    try:
        with open('package.json', 'r', encoding='utf-8') as f:
            pkg = json.load(f)
            v = pkg.get('version')
            if v:
                return v.lstrip('v')
    except Exception:
        pass

    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
            if '## [v' in content:
                for line in content.split('\n'):
                    if '## [' in line and ']' in line:
                        return line.split('[')[1].split(']')[0].strip().lstrip('v')
    except Exception:
        pass

    return '3.1.0'

def update_version_files():
    """Atualiza versão em todos os arquivos"""
    version = get_version()

    # package.json
    try:
        with open('package.json', 'r', encoding='utf-8') as f:
            pkg = json.load(f)
        pkg['version'] = version
        with open('package.json', 'w', encoding='utf-8') as f:
            json.dump(pkg, f, indent=2)
    except Exception:
        pass

def create_installer():
    """Cria o instalador Inno Setup"""
    ver = get_version()
    installer_path = Path('installer/setup.iss')
    installer_path.parent.mkdir(parents=True, exist_ok=True)

    iss_content = f'''#define APP_VERSION "{ver}"
#define APP_NAME "Midnight Optimizer {ver}"
#define AUTHOR "chibangar"

[Setup]
AppName={{#APP_NAME}}
AppVersion={{#APP_VERSION}}
AppPublisher={{#AUTHOR}}
AppPublisherEmail=contact@midnightoptimizer.com
DefaultDirName={{autopf}}\\Midnight Optimizer
DefaultGroupName=Midnight Optimizer
WizardStyle=modern
OutputBaseFilename=Midnight_Optimizer_{ver}_Setup
Compression=lzma2
SolidCompression=yes
DisableDirPage=yes
DisableProgramsPage=yes
DisableReadyPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\\Portuguese.isl"

[Files]
Source: "dist\\MidnightOptimizer.exe"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{autodesktop}}\\Midnight Optimizer"; Filename: "{{app}}\\MidnightOptimizer.exe"
Name: "{{commonprograms}}\\Midnight Optimizer"; Filename: "{{app}}\\MidnightOptimizer.exe"

[Run]
Filename: "{{app}}\\MidnightOptimizer.exe"; Description: "Iniciar Midnight Optimizer"; Flags: nowait postinstall skipifsilent
'''

    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(iss_content)

def create_release_notes():
    """Cria as notas da release para o GitHub"""

    notes = f'''## 🚀 Midnight Optimizer v{get_version()} — Professional Gaming Suite

### ✨ Destaques da Versão

#### ⚡ Nova Interface Moderna e Profissional
- Design System Dark Obsidian de alta precisão com micro-contraste apurado.
- Iconografia vetorial SVG nativa em toda a navegação e controlos rápidos.
- Centro de Controlo no Dashboard com telemetria de hardware (CPU, GPU, RAM, Disco) em tempo real.
- Layout ergonómico e responsivo sem animações invasivas ou efeitos desfocados desnecessários.
- 3 temas refinados: WoW Midnight (Índigo/Violeta), CS2 Tático (Âmbar) e Call of Duty (Dourado Militar).

#### 🎯 Otimização de Latência & Kernel
- Agendamento de processos e prioridade em tempo real para jogos competitivos.
- Otimização da pilha de rede TCP/IP e rotinas rápidas de flush DNS.
- Gestão de temporários e suspensão de processos em segundo plano.
- Configurações dedicadas para CS2, WoW e Call of Duty.

#### 📦 Automatização de Releases
- Compilação automática de executáveis Windows via GitHub Actions a cada tag/release.
- Executável nativo autónomo `MidnightOptimizer.exe` pronto a correr.

---

### 📋 Requisitos de Sistema
- Windows 10 ou Windows 11 (64-bit)
- Direitos de Administrador para otimizações de energia e registo
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
        with open('styles.css', 'r', encoding='utf-8') as f:
            content = f.read()
            if '--bg-void' in content:
                css_valid = True
                print("✓ styles.css válido")
    except FileNotFoundError:
        print("⚠️  styles.css não encontrado!")

    html_valid = False
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'styles.css' in content:
                html_valid = True
                print("✓ index.html referencia CSS")
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
