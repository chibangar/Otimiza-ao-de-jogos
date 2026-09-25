# -*- coding: utf-8 -*-
"""
Motor de Gestão e Instalação de Softwares & Ferramentas para Pulse Gaming Optimizer.
Suporta:
- Deteção instantânea de programas instalados via Windows Registry e Winget
- Catálogo completo de 10 categorias com ~90 aplicações essenciais
- Instalação e desinstalação silenciosa em lote (batch background)
- Seleção inteligente (Tudo, Apenas Instalados, Apenas Não Instalados)
"""

import os
import re
import sys
import json
import winreg
import subprocess
import threading
from typing import Dict, List, Any

# Flag de cancelamento de lote
_CANCEL_FLAG = threading.Event()
_INSTALL_LOCK = threading.Lock()
_CURRENT_PROGRESS = {"running": False, "current": "", "total": 0, "done": 0, "log": []}

SOFTWARE_CATALOG: List[Dict[str, Any]] = [
    # 1. Aplicações de Desenvolvimento
    {
        "id": "git", "name": "Git", "category": "Aplicações de Desenvolvimento",
        "desc": "Sistema de controlo de versões distribuído amplamente utilizado.",
        "winget": "Git.Git", "reg": ["git version", "git"], "link": "https://git-scm.com/",
        "icon": "git"
    },
    {
        "id": "vscode", "name": "VS Code", "category": "Aplicações de Desenvolvimento",
        "desc": "Editor de código fonte ultra-rápido com extensões e depuração.",
        "winget": "Microsoft.VisualStudioCode", "reg": ["visual studio code", "vscode"], "link": "https://code.visualstudio.com/",
        "icon": "code"
    },
    {
        "id": "python", "name": "Python", "category": "Aplicações de Desenvolvimento",
        "desc": "Linguagem de programação versátil para automação, IA e desenvolvimento.",
        "winget": "Python.Python.3.12", "reg": ["python 3", "python launcher"], "link": "https://www.python.org/",
        "icon": "terminal"
    },
    {
        "id": "eclipse", "name": "Eclipse", "category": "Aplicações de Desenvolvimento",
        "desc": "IDE robusto para desenvolvimento Java, C/C++ e ferramentas web.",
        "winget": "EclipseFoundation.Eclipse", "reg": ["eclipse"], "link": "https://www.eclipse.org/",
        "icon": "code"
    },
    {
        "id": "githubdesktop", "name": "GitHub Desktop", "category": "Aplicações de Desenvolvimento",
        "desc": "Interface visual intuitiva para trabalhar com repositórios GitHub.",
        "winget": "GitHub.GitHubDesktop", "reg": ["github desktop"], "link": "https://desktop.github.com/",
        "icon": "git"
    },
    {
        "id": "meld", "name": "Meld", "category": "Aplicações de Desenvolvimento",
        "desc": "Ferramenta gráfica de comparação e fusão visual de código (diff).",
        "winget": "GNOME.Meld", "reg": ["meld"], "link": "https://meldmerge.org/",
        "icon": "code"
    },
    {
        "id": "notepadplus", "name": "Notepad++", "category": "Aplicações de Desenvolvimento",
        "desc": "Editor de texto e código extremamente leve com realce de sintaxe.",
        "winget": "Notepad++.Notepad++", "reg": ["notepad++"], "link": "https://notepad-plus-plus.org/",
        "icon": "code"
    },
    {
        "id": "powershell7", "name": "PowerShell", "category": "Aplicações de Desenvolvimento",
        "desc": "Shell de comandos moderno e multiplataforma de alta performance.",
        "winget": "Microsoft.PowerShell", "reg": ["powershell 7", "powershell-7"], "link": "https://microsoft.com/powershell",
        "icon": "terminal"
    },
    {
        "id": "putty", "name": "PuTTY", "category": "Aplicações de Desenvolvimento",
        "desc": "Cliente SSH, Telnet e emulador de terminal clássico para Windows.",
        "winget": "PuTTY.PuTTY", "reg": ["putty"], "link": "https://www.putty.org/",
        "icon": "terminal"
    },
    {
        "id": "winscp", "name": "WinSCP", "category": "Aplicações de Desenvolvimento",
        "desc": "Cliente SFTP, FTP, WebDAV e SCP com gestão gráfica de ficheiros.",
        "winget": "WinSCP.WinSCP", "reg": ["winscp"], "link": "https://winscp.net/",
        "icon": "terminal"
    },

    # 2. Visualizadores de Documentos
    {
        "id": "acrobat", "name": "Acrobat", "category": "Visualizadores de Documentos",
        "desc": "Leitor padrão mundial para visualizar e assinar ficheiros PDF.",
        "winget": "Adobe.Acrobat.Reader.64-bit", "reg": ["adobe acrobat", "acrobat reader"], "link": "https://get.adobe.com/reader/",
        "icon": "file"
    },
    {
        "id": "cherrytree", "name": "CherryTree", "category": "Visualizadores de Documentos",
        "desc": "Aplicação hierárquica para anotações em árvore com formatação rica.",
        "winget": "giuspen.cherrytree", "reg": ["cherrytree"], "link": "https://www.giuspen.net/cherrytree/",
        "icon": "file"
    },
    {
        "id": "evernote", "name": "Evernote", "category": "Visualizadores de Documentos",
        "desc": "Organizador e bloco de notas sincronizado na nuvem para equipas.",
        "winget": "Evernote.Evernote", "reg": ["evernote"], "link": "https://evernote.com/",
        "icon": "file"
    },
    {
        "id": "foxit", "name": "Foxit", "category": "Visualizadores de Documentos",
        "desc": "Leitor e anotador de documentos PDF rápido, leve e seguro.",
        "winget": "Foxit.FoxitReader", "reg": ["foxit reader", "foxit pdf"], "link": "https://www.foxit.com/pdf-reader/",
        "icon": "file"
    },
    {
        "id": "libreoffice", "name": "LibreOffice", "category": "Visualizadores de Documentos",
        "desc": "Suite de produtividade e escritório completa e de código aberto.",
        "winget": "TheDocumentFoundation.LibreOffice", "reg": ["libreoffice"], "link": "https://www.libreoffice.org/",
        "icon": "file"
    },
    {
        "id": "office365", "name": "Microsoft 365", "category": "Visualizadores de Documentos",
        "desc": "Pacote Microsoft 365 (Word, Excel, PowerPoint) para Windows.",
        "winget": "Microsoft.Office", "reg": ["microsoft office", "microsoft 365"], "link": "https://www.office.com/",
        "icon": "file"
    },
    {
        "id": "onlyoffice", "name": "ONLYOFFICE", "category": "Visualizadores de Documentos",
        "desc": "Editores de escritório de alta compatibilidade com formatos MS Office.",
        "winget": "ONLYOFFICE.DesktopEditors", "reg": ["onlyoffice"], "link": "https://www.onlyoffice.com/",
        "icon": "file"
    },
    {
        "id": "openoffice", "name": "OpenOffice", "category": "Visualizadores de Documentos",
        "desc": "Pacote de escritório clássico para processamento de texto e folhas de cálculo.",
        "winget": "Apache.OpenOffice", "reg": ["openoffice"], "link": "https://www.openoffice.org/",
        "icon": "file"
    },
    {
        "id": "pdf24", "name": "PDF24", "category": "Visualizadores de Documentos",
        "desc": "Ferramentas completas para converter, juntar, dividir e editar PDFs.",
        "winget": "geeksoftwareGmbH.PDF24Creator", "reg": ["pdf24 creator", "pdf24"], "link": "https://www.pdf24.org/",
        "icon": "file"
    },
    {
        "id": "pdfgear", "name": "PDFGear", "category": "Visualizadores de Documentos",
        "desc": "Editor de PDF gratuito avançado com inteligência artificial integrada.",
        "winget": "PDFgear.PDFgear", "reg": ["pdfgear"], "link": "https://www.pdfgear.com/",
        "icon": "file"
    },
    {
        "id": "sumatrapdf", "name": "SumatraPDF", "category": "Visualizadores de Documentos",
        "desc": "O leitor de PDF, ePub, MOBI e CBZ mais leve e rápido para Windows.",
        "winget": "SumatraPDF.SumatraPDF", "reg": ["sumatrapdf"], "link": "https://www.sumatrapdfreader.org/",
        "icon": "file"
    },

    # 3. Gestão de Ficheiros e Discos
    {
        "id": "advancedrenamer", "name": "Advanced Renamer", "category": "Gestão de Ficheiros e Discos",
        "desc": "Renomeador em lote com múltiplos métodos para ficheiros e pastas.",
        "winget": "Hulubalu.AdvancedRenamer", "reg": ["advanced renamer"], "link": "https://www.advancedrenamer.com/",
        "icon": "folder"
    },
    {
        "id": "bulkrename", "name": "Bulk Rename", "category": "Gestão de Ficheiros e Discos",
        "desc": "Utilitário clássico de renomeação em massa com critérios flexíveis.",
        "winget": "TGRMNSoftware.BulkRenameUtility", "reg": ["bulk rename utility"], "link": "https://www.bulkrenameutility.co.uk/",
        "icon": "folder"
    },
    {
        "id": "crystaldiskinfo", "name": "CrystalDiskInfo", "category": "Gestão de Ficheiros e Discos",
        "desc": "Monitor de saúde e temperatura S.M.A.R.T para SSDs e HDDs.",
        "winget": "CrystalDewWorld.CrystalDiskInfo", "reg": ["crystaldiskinfo"], "link": "https://crystalmark.info/en/software/crystaldiskinfo/",
        "icon": "folder"
    },
    {
        "id": "everything", "name": "Everything", "category": "Gestão de Ficheiros e Discos",
        "desc": "Motor de pesquisa instantâneo por nome de ficheiros no Windows.",
        "winget": "voidtools.Everything", "reg": ["everything"], "link": "https://www.voidtools.com/",
        "icon": "search"
    },
    {
        "id": "fileconverter", "name": "File Converter", "category": "Gestão de Ficheiros e Discos",
        "desc": "Conversor universal no menu de contexto para áudio, vídeo e imagem.",
        "winget": "AdrienAllard.FileConverter", "reg": ["file converter"], "link": "https://file-converter.io/",
        "icon": "folder"
    },
    {
        "id": "rufus", "name": "Rufus", "category": "Gestão de Ficheiros e Discos",
        "desc": "Criador de unidades USB inicializáveis (pendrives de instalação Windows/Linux).",
        "winget": "Rufus.Rufus", "reg": ["rufus"], "link": "https://rufus.ie/",
        "icon": "folder"
    },
    {
        "id": "sandisk", "name": "SanDisk", "category": "Gestão de Ficheiros e Discos",
        "desc": "Painel de gestão de unidades de armazenamento e SSDs SanDisk/WD.",
        "winget": "WesternDigital.Dashboard", "reg": ["sandisk", "western digital dashboard"], "link": "https://www.westerndigital.com/",
        "icon": "folder"
    },
    {
        "id": "teracopy", "name": "TeraCopy", "category": "Gestão de Ficheiros e Discos",
        "desc": "Copiador de ficheiros de alta velocidade com pausa, verificação e integridade.",
        "winget": "CodeSector.TeraCopy", "reg": ["teracopy"], "link": "https://www.codesector.com/teracopy",
        "icon": "folder"
    },
    {
        "id": "treesize", "name": "TreeSize", "category": "Gestão de Ficheiros e Discos",
        "desc": "Analisador rápido de espaço em disco mostrando quais pastas ocupam mais espaço.",
        "winget": "JAMSoftware.TreeSize.Free", "reg": ["treesize free", "treesize"], "link": "https://www.jam-software.com/treesize_free",
        "icon": "folder"
    },
    {
        "id": "windirstat", "name": "WinDirStat", "category": "Gestão de Ficheiros e Discos",
        "desc": "Visualizador de estatísticas de uso de disco com mapa de árvore colorido.",
        "winget": "WinDirStat.WinDirStat", "reg": ["windirstat"], "link": "https://windirstat.net/",
        "icon": "folder"
    },
    {
        "id": "wiztree", "name": "WizTree", "category": "Gestão de Ficheiros e Discos",
        "desc": "O analisador de espaço em disco mais veloz do mundo lendo a tabela MFT.",
        "winget": "AntibodySoftware.WizTree", "reg": ["wiztree"], "link": "https://diskanalyzer.com/",
        "icon": "folder"
    },

    # 4. Jogos
    {
        "id": "battlenet", "name": "Battle.net", "category": "Jogos",
        "desc": "Plataforma oficial da Blizzard para Diablo, Overwatch, WoW e Call of Duty.",
        "winget": "Blizzard.BattleNet", "reg": ["battle.net"], "link": "https://www.blizzard.com/",
        "icon": "game"
    },
    {
        "id": "faceit", "name": "FACEIT", "category": "Jogos",
        "desc": "Cliente competitivo e anti-cheat oficial para matchmaking CS2 e eSports.",
        "winget": "FACEIT.FACEITClient", "reg": ["faceit", "faceit client"], "link": "https://www.faceit.com/",
        "icon": "game"
    },
    {
        "id": "eaapp", "name": "EA App", "category": "Jogos",
        "desc": "Novo lançador oficial de jogos e subscrição EA Play da Electronic Arts.",
        "winget": "ElectronicArts.EADesktop", "reg": ["ea app", "ea desktop"], "link": "https://www.ea.com/ea-app",
        "icon": "game"
    },
    {
        "id": "epicgames", "name": "Epic Games", "category": "Jogos",
        "desc": "Loja e lançador da Epic Games para Fortnite, Unreal Engine e jogos grátis.",
        "winget": "EpicGames.EpicGamesLauncher", "reg": ["epic games launcher"], "link": "https://store.epicgames.com/",
        "icon": "game"
    },
    {
        "id": "gog", "name": "GOG", "category": "Jogos",
        "desc": "Cliente GOG Galaxy para gerir e jogar títulos sem DRM de forma limpa.",
        "winget": "GOG.Galaxy", "reg": ["gog galaxy"], "link": "https://www.gog.com/galaxy",
        "icon": "game"
    },
    {
        "id": "playnite", "name": "Playnite", "category": "Jogos",
        "desc": "Gestor unificado de bibliotecas de videojogos com suporte a emuladores.",
        "winget": "Playnite.Playnite", "reg": ["playnite"], "link": "https://playnite.link/",
        "icon": "game"
    },
    {
        "id": "rockstar", "name": "Rockstar", "category": "Jogos",
        "desc": "Lançador oficial para GTA V, Red Dead Redemption 2 e clássicos Rockstar.",
        "winget": "RockstarGames.Launcher", "reg": ["rockstar games launcher"], "link": "https://www.rockstargames.com/",
        "icon": "game"
    },
    {
        "id": "steam", "name": "Steam", "category": "Jogos",
        "desc": "A maior plataforma de distribuição e comunidade de videojogos do mundo.",
        "winget": "Valve.Steam", "reg": ["steam"], "link": "https://store.steampowered.com/",
        "icon": "game"
    },
    {
        "id": "ubisoft", "name": "Ubisoft", "category": "Jogos",
        "desc": "Ecossistema Ubisoft Connect para Rainbow Six Siege, Assassin's Creed e mais.",
        "winget": "Ubisoft.Connect", "reg": ["ubisoft connect"], "link": "https://ubisoftconnect.com/",
        "icon": "game"
    },

    # 5. Imagem
    {
        "id": "blender", "name": "Blender", "category": "Imagem",
        "desc": "Suite completa e profissional de modelação 3D, animação e renderização.",
        "winget": "BlenderFoundation.Blender", "reg": ["blender"], "link": "https://www.blender.org/",
        "icon": "image"
    },
    {
        "id": "faststone", "name": "FastStone", "category": "Imagem",
        "desc": "Visualizador, conversor e editor básico de imagens veloz e intuitivo.",
        "winget": "FastStone.Viewer", "reg": ["faststone image viewer"], "link": "https://www.faststone.org/",
        "icon": "image"
    },
    {
        "id": "flameshot", "name": "Flameshot", "category": "Imagem",
        "desc": "Utilitário avançado de captura de ecrã com anotações e setas néon.",
        "winget": "Flameshot.Flameshot", "reg": ["flameshot"], "link": "https://flameshot.org/",
        "icon": "image"
    },
    {
        "id": "gimp", "name": "GIMP", "category": "Imagem",
        "desc": "Editor de imagem e pintura digital avançado equivalente ao Photoshop.",
        "winget": "GIMP.GIMP", "reg": ["gimp"], "link": "https://www.gimp.org/",
        "icon": "image"
    },
    {
        "id": "greenshot", "name": "Greenshot", "category": "Imagem",
        "desc": "Capturador de ecrã leve para produtividade e envio rápido de imagens.",
        "winget": "Greenshot.Greenshot", "reg": ["greenshot"], "link": "https://getgreenshot.org/",
        "icon": "image"
    },
    {
        "id": "imageglass", "name": "ImageGlass", "category": "Imagem",
        "desc": "Visualizador de imagens leve e moderno para substituir o visualizador do Windows.",
        "winget": "DuongDieuPhap.ImageGlass", "reg": ["imageglass"], "link": "https://imageglass.org/",
        "icon": "image"
    },
    {
        "id": "inkscape", "name": "Inkscape", "category": "Imagem",
        "desc": "Editor profissional de gráficos vetoriais (SVG, ilustrações e logótipos).",
        "winget": "Inkscape.Inkscape", "reg": ["inkscape"], "link": "https://inkscape.org/",
        "icon": "image"
    },
    {
        "id": "irfanview", "name": "IrfanView", "category": "Imagem",
        "desc": "Visualizador ultra-rápido de fotos com processamento em lote e plugins.",
        "winget": "IrfanSkiljan.IrfanView", "reg": ["irfanview"], "link": "https://www.irfanview.com/",
        "icon": "image"
    },
    {
        "id": "krita", "name": "Krita", "category": "Imagem",
        "desc": "Estúdio profissional de pintura digital, ilustração e arte concetual.",
        "winget": "KDE.Krita", "reg": ["krita"], "link": "https://krita.org/",
        "icon": "image"
    },
    {
        "id": "paintnet", "name": "Paint.NET", "category": "Imagem",
        "desc": "Editor de fotos fácil de usar com suporte a camadas e efeitos especiais.",
        "winget": "dotPDN.PaintDotNet", "reg": ["paint.net"], "link": "https://www.getpaint.net/",
        "icon": "image"
    },
    {
        "id": "sharex", "name": "ShareX", "category": "Imagem",
        "desc": "A melhor ferramenta de captura de ecrã, gravação de GIF e envio automático.",
        "winget": "ShareX.ShareX", "reg": ["sharex"], "link": "https://getsharex.com/",
        "icon": "image"
    },
    {
        "id": "xnviewmp", "name": "XnViewMP", "category": "Imagem",
        "desc": "Organizador e gestor de grandes galerias de imagens e fotos RAW.",
        "winget": "XnSoft.XnView.MP", "reg": ["xnview mp", "xnview"], "link": "https://www.xnview.com/",
        "icon": "image"
    },

    # 6. Runtimes e Dependências
    {
        "id": "directx", "name": "DirectX", "category": "Runtimes e Dependências",
        "desc": "Bibliotecas DirectX essenciais para compatibilidade de jogos legados e novos.",
        "winget": "Microsoft.DirectX", "reg": ["directx"], "link": "https://www.microsoft.com/download/details.aspx?id=35",
        "icon": "cpu"
    },
    {
        "id": "java", "name": "Java", "category": "Runtimes e Dependências",
        "desc": "Ambiente de execução Java Runtime (JRE/JDK) para Minecraft e utilitários.",
        "winget": "Oracle.JavaRuntimeEnvironment", "reg": ["java", "openjdk"], "link": "https://www.java.com/",
        "icon": "cpu"
    },
    {
        "id": "dotnet6", "name": ".NET 6.0 Runtime", "category": "Runtimes e Dependências",
        "desc": "Runtime do Microsoft .NET 6.0 para execução de programas e launchers modernos.",
        "winget": "Microsoft.DotNet.DesktopRuntime.6", "reg": ["microsoft .net core runtime - 6", "microsoft windows desktop runtime - 6"], "link": "https://dotnet.microsoft.com/",
        "icon": "cpu"
    },
    {
        "id": "dotnet7", "name": ".NET 7.0 Runtime", "category": "Runtimes e Dependências",
        "desc": "Runtime Microsoft .NET 7.0 para aplicações desktop otimizadas.",
        "winget": "Microsoft.DotNet.DesktopRuntime.7", "reg": ["microsoft windows desktop runtime - 7"], "link": "https://dotnet.microsoft.com/",
        "icon": "cpu"
    },
    {
        "id": "dotnet8", "name": ".NET 8.0 Runtime", "category": "Runtimes e Dependências",
        "desc": "Runtime LTS mais recente do Microsoft .NET 8 para máximo desempenho.",
        "winget": "Microsoft.DotNet.DesktopRuntime.8", "reg": ["microsoft windows desktop runtime - 8"], "link": "https://dotnet.microsoft.com/",
        "icon": "cpu"
    },
    {
        "id": "dotnet9", "name": ".NET 9.0 Runtime", "category": "Runtimes e Dependências",
        "desc": "Última versão do Microsoft .NET 9.0 com aceleração de hardware.",
        "winget": "Microsoft.DotNet.DesktopRuntime.9", "reg": ["microsoft windows desktop runtime - 9"], "link": "https://dotnet.microsoft.com/",
        "icon": "cpu"
    },
    {
        "id": "vcredist_x64", "name": "Visual C++ (x64)", "category": "Runtimes e Dependências",
        "desc": "Microsoft Visual C++ Redistributable 2015-2022 para sistemas de 64 bits.",
        "winget": "Microsoft.VCRedist.2015+.x64", "reg": ["microsoft visual c++ 2015-2022 redistributable (x64)", "microsoft visual c++ 2022 x64"], "link": "https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist",
        "icon": "cpu"
    },
    {
        "id": "vcredist_x86", "name": "Visual C++ (x86)", "category": "Runtimes e Dependências",
        "desc": "Microsoft Visual C++ Redistributable 2015-2022 para aplicações de 32 bits.",
        "winget": "Microsoft.VCRedist.2015+.x86", "reg": ["microsoft visual c++ 2015-2022 redistributable (x86)", "microsoft visual c++ 2022 x86"], "link": "https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist",
        "icon": "cpu"
    },
    {
        "id": "vcredist_aio", "name": "Visual C++ All-in-One", "category": "Runtimes e Dependências",
        "desc": "Instalador mestre com todos os Visual C++ desde 2005 até 2022.",
        "winget": "abbodi1406.vcredist", "reg": ["visual c++ aio", "microsoft visual c++ 2010"], "link": "https://github.com/abbodi1406/vcredist",
        "icon": "cpu"
    },
    {
        "id": "dotnet481", "name": ".NET Framework 4.8.1", "category": "Runtimes e Dependências",
        "desc": "Framework nativo clássico do Windows necessário para quase todos os jogos.",
        "winget": "Microsoft.DotNet.Framework.DeveloperPack_4", "reg": ["microsoft .net framework 4"], "link": "https://dotnet.microsoft.com/",
        "icon": "cpu"
    },

    # 7. Privacidade e Segurança
    {
        "id": "malwarebytes", "name": "Malwarebytes", "category": "Privacidade e Segurança",
        "desc": "Deteção e remoção de vírus, trojans, ransomwares e ameaças ativas.",
        "winget": "Malwarebytes.Malwarebytes", "reg": ["malwarebytes"], "link": "https://www.malwarebytes.com/",
        "icon": "shield"
    },
    {
        "id": "adwcleaner", "name": "AdwCleaner", "category": "Privacidade e Segurança",
        "desc": "Removedor veloz de adware, barras de ferramentas e programas indesejados (PUPs).",
        "winget": "Malwarebytes.AdwCleaner", "reg": ["adwcleaner"], "link": "https://www.malwarebytes.com/adwcleaner",
        "icon": "shield"
    },
    {
        "id": "ooshutup", "name": "O&O ShutUp10++", "category": "Privacidade e Segurança",
        "desc": "Desativa a telemetria, rastreamento e espionagem nativa do Windows 10/11.",
        "winget": "O&OSoftware.ShutUp10", "reg": ["o&o shutup10"], "link": "https://www.oo-software.com/en/shutup10",
        "icon": "shield"
    },
    {
        "id": "onionshare", "name": "OnionShare", "category": "Privacidade e Segurança",
        "desc": "Partilha anónima e segura de ficheiros usando a rede encriptada Tor.",
        "winget": "MicahLee.OnionShare", "reg": ["onionshare"], "link": "https://onionshare.org/",
        "icon": "shield"
    },
    {
        "id": "simplewall", "name": "SimpleWall", "category": "Privacidade e Segurança",
        "desc": "Firewall simples e ultra-poderoso para bloquear conexões sem aviso.",
        "winget": "Henry++Simplewall", "reg": ["simplewall"], "link": "https://www.henrypp.org/product/simplewall",
        "icon": "shield"
    },
    {
        "id": "teleguard", "name": "TeleGuard", "category": "Privacidade e Segurança",
        "desc": "Mensageiro seguro focado em privacidade absoluta e sem recolha de dados.",
        "winget": "TeleGuard.TeleGuard", "reg": ["teleguard"], "link": "https://teleguard.com/",
        "icon": "shield"
    },
    {
        "id": "wfc", "name": "Windows Firewall Control", "category": "Privacidade e Segurança",
        "desc": "Extensão para controlar e afinar o Firewall nativo do Windows em 2 cliques.",
        "winget": "Malwarebytes.WindowsFirewallControl", "reg": ["windows firewall control"], "link": "https://binisoft.org/wfc",
        "icon": "shield"
    },

    # 8. Navegadores
    {
        "id": "brave", "name": "Brave", "category": "Navegadores",
        "desc": "Navegador ultra-rápido com bloqueador nativo de anúncios e rastreadores.",
        "winget": "Brave.Brave", "reg": ["brave"], "link": "https://brave.com/",
        "icon": "globe"
    },
    {
        "id": "chrome", "name": "Chrome", "category": "Navegadores",
        "desc": "O navegador da Google, rápido, seguro e totalmente integrado com o ecossistema.",
        "winget": "Google.Chrome", "reg": ["google chrome"], "link": "https://www.google.com/chrome/",
        "icon": "globe"
    },
    {
        "id": "edgewebview", "name": "Edge WebView", "category": "Navegadores",
        "desc": "Componente essencial para renderizar interfaces web em apps modernas.",
        "winget": "Microsoft.EdgeWebView2Runtime", "reg": ["microsoft edge webview2 runtime"], "link": "https://developer.microsoft.com/microsoft-edge/webview2/",
        "icon": "globe"
    },
    {
        "id": "floorp", "name": "Ablaze Floorp", "category": "Navegadores",
        "desc": "Navegador baseado em Firefox com abas verticais e extrema personalização.",
        "winget": "Ablaze.Floorp", "reg": ["floorp"], "link": "https://floorp.app/",
        "icon": "globe"
    },
    {
        "id": "duckduckgo", "name": "DuckDuckGo", "category": "Navegadores",
        "desc": "Navegador desktop com proteção de privacidade e botão Fire para apagar dados.",
        "winget": "DuckDuckGo.DesktopBrowser", "reg": ["duckduckgo"], "link": "https://duckduckgo.com/windows",
        "icon": "globe"
    },
    {
        "id": "librewolf", "name": "LibreWolf", "category": "Navegadores",
        "desc": "Versão do Firefox configurada de fábrica para máxima privacidade e sem telemetria.",
        "winget": "LibreWolf.LibreWolf", "reg": ["librewolf"], "link": "https://librewolf.net/",
        "icon": "globe"
    },
    {
        "id": "maxthon", "name": "Maxthon", "category": "Navegadores",
        "desc": "Navegador com motor duplo, bloqueador de anúncios e downloads avançados.",
        "winget": "Maxthon.Maxthon", "reg": ["maxthon"], "link": "https://www.maxthon.com/",
        "icon": "globe"
    },
    {
        "id": "mercury", "name": "Mercury", "category": "Navegadores",
        "desc": "Compilação veloz do Firefox com instruções de CPU AVX e flags de performance.",
        "winget": "Alex313031.Mercury", "reg": ["mercury browser", "mercury"], "link": "https://thorium.rocks/mercury",
        "icon": "globe"
    },
    {
        "id": "vivaldi", "name": "Vivaldi", "category": "Navegadores",
        "desc": "Navegador de alta produtividade com gestão de abas em pilha e painéis laterais.",
        "winget": "Vivaldi.Vivaldi", "reg": ["vivaldi"], "link": "https://vivaldi.com/",
        "icon": "globe"
    },
    {
        "id": "waterfox", "name": "Waterfox", "category": "Navegadores",
        "desc": "Navegador de alta velocidade baseado no Firefox com foco em liberdade do utilizador.",
        "winget": "Waterfox.Waterfox", "reg": ["waterfox"], "link": "https://www.waterfox.net/",
        "icon": "globe"
    },

    # 9. Compressão
    {
        "id": "winrar", "name": "WinRAR", "category": "Compressão",
        "desc": "O utilitário de compressão RAR e descompactação mais famoso do mundo.",
        "winget": "RARLab.WinRAR", "reg": ["winrar"], "link": "https://www.rarlab.com/",
        "icon": "archive"
    },
    {
        "id": "sevenzip", "name": "7-Zip", "category": "Compressão",
        "desc": "Descompactador open-source de altíssima taxa de compressão e velocidade.",
        "winget": "7zip.7zip", "reg": ["7-zip"], "link": "https://www.7-zip.org/",
        "icon": "archive"
    },
    {
        "id": "nanazip", "name": "NanaZip", "category": "Compressão",
        "desc": "Versão moderna do 7-Zip integrada no novo menu de contexto do Windows 11.",
        "winget": "M2Team.NanaZip", "reg": ["nanazip"], "link": "https://github.com/M2Team/NanaZip",
        "icon": "archive"
    },
    {
        "id": "peazip", "name": "PeaZip", "category": "Compressão",
        "desc": "Gestor de arquivos gratuito com suporte a mais de 200 formatos de compressão.",
        "winget": "GiorgioTani.PeaZip", "reg": ["peazip"], "link": "https://peazip.github.io/",
        "icon": "archive"
    },

    # 10. Utilitários de Personalização
    {
        "id": "autohotkey", "name": "AutoHotkey", "category": "Utilitários de Personalização",
        "desc": "Linguagem de script para automação de teclado, macros e atalhos globais.",
        "winget": "AutoHotkey.AutoHotkey", "reg": ["autohotkey"], "link": "https://www.autohotkey.com/",
        "icon": "settings"
    },
    {
        "id": "explorerpatcher", "name": "Explorer Patcher", "category": "Utilitários de Personalização",
        "desc": "Restaura a barra de tarefas clássica do Windows 10 e menu iniciar no Windows 11.",
        "winget": "valinet.ExplorerPatcher", "reg": ["explorerpatcher"], "link": "https://github.com/valinet/ExplorerPatcher",
        "icon": "settings"
    },
    {
        "id": "johnbackground", "name": "John's Background", "category": "Utilitários de Personalização",
        "desc": "Alternador automático de papéis de parede com efeitos e coleções.",
        "winget": "JohnConners.JohnsBackgroundSwitcher", "reg": ["john's background switcher"], "link": "https://johnsad.ventures/software/backgroundswitcher/",
        "icon": "settings"
    },
    {
        "id": "lively", "name": "Lively", "category": "Utilitários de Personalização",
        "desc": "Papéis de parede animados, interativos e em vídeo para a sua área de trabalho.",
        "winget": "rocksdanister.Lively", "reg": ["lively wallpaper"], "link": "https://www.rocksdanister.com/lively/",
        "icon": "settings"
    },
    {
        "id": "nexus", "name": "Nexus", "category": "Utilitários de Personalização",
        "desc": "Barra de atalhos e dock animada ao estilo macOS para Windows.",
        "winget": "Winstep.Nexus", "reg": ["winstep nexus", "nexus dock"], "link": "https://www.winstep.net/nexus.asp",
        "icon": "settings"
    },
    {
        "id": "nilesoftshell", "name": "Nilesoft Shell", "category": "Utilitários de Personalização",
        "desc": "Menu de contexto de clique direito ultra-rápido, moderno e customizável.",
        "winget": "Nilesoft.Shell", "reg": ["nilesoft shell"], "link": "https://nilesoft.org/",
        "icon": "settings"
    },
    {
        "id": "openshell", "name": "Open-Shell", "category": "Utilitários de Personalização",
        "desc": "O menu Iniciar clássico do Windows 7 para Windows 10 e 11.",
        "winget": "Open-Shell.Open-Shell-Menu", "reg": ["open-shell"], "link": "https://github.com/Open-Shell/Open-Shell-Menu",
        "icon": "settings"
    },
    {
        "id": "startallback", "name": "StartAllBack", "category": "Utilitários de Personalização",
        "desc": "Melhora a barra de tarefas, o Explorer e o menu Iniciar do Windows 11.",
        "winget": "StartIsBack.StartAllBack", "reg": ["startallback"], "link": "https://www.startallback.com/",
        "icon": "settings"
    },
    {
        "id": "sucrose", "name": "Sucrose", "category": "Utilitários de Personalização",
        "desc": "Motor de papéis de parede animados leves com suporte a temas web.",
        "winget": "Aram.Sucrose", "reg": ["sucrose"], "link": "https://github.com/Aram-Dev/Sucrose",
        "icon": "settings"
    },
    {
        "id": "windhawk", "name": "Windhawk", "category": "Utilitários de Personalização",
        "desc": "Plataforma de modificações e melhorias modulares para o sistema Windows.",
        "winget": "RamonUnch.Windhawk", "reg": ["windhawk"], "link": "https://windhawk.net/",
        "icon": "settings"
    }
]


def _get_installed_display_names() -> set:
    """Extrai todos os DisplayNames registados no Windows Registry em <0.02s."""
    installed = set()
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hkey, subkey in roots:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    try:
                        sk_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sk_name) as sk:
                            try:
                                dn = winreg.QueryValueEx(sk, "DisplayName")[0]
                                if dn:
                                    installed.add(str(dn).strip().lower())
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass
    return installed


def get_software_catalog_with_status() -> List[Dict[str, Any]]:
    """Devolve a lista completa com a indicação se cada aplicação está instalada."""
    installed_names = _get_installed_display_names()

    # Também obtém lista de IDs do winget para precisão extra
    winget_ids = set()
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        res = subprocess.run(
            ["winget", "list", "--source", "winget"],
            capture_output=True, text=True, timeout=5,
            startupinfo=startupinfo
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    winget_ids.add(parts[1].lower())
    except Exception:
        pass

    result = []
    for app in SOFTWARE_CATALOG:
        is_installed = False
        wid = app.get("winget", "").lower()
        if wid and wid in winget_ids:
            is_installed = True
        else:
            # Testa correspondência no registo
            for pattern in app.get("reg", []):
                pat = pattern.lower()
                if any(pat in iname for iname in installed_names):
                    is_installed = True
                    break

        item = dict(app)
        item["installed"] = is_installed
        result.append(item)

    return result


def install_app_silent(winget_id: str) -> bool:
    """Executa a instalação silenciosa via winget."""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        cmd = [
            "winget", "install",
            "--id", winget_id,
            "--exact",
            "--silent",
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--disable-interactivity"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300, startupinfo=startupinfo)
        return res.returncode == 0
    except Exception:
        return False


def uninstall_app_silent(winget_id: str) -> bool:
    """Executa a desinstalação silenciosa via winget."""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        cmd = [
            "winget", "uninstall",
            "--id", winget_id,
            "--exact",
            "--silent",
            "--disable-interactivity"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180, startupinfo=startupinfo)
        return res.returncode == 0
    except Exception:
        return False


def run_batch_action(action: str, app_ids: List[str]) -> Dict[str, Any]:
    """
    Executa em lote a instalação ou desinstalação dos programas selecionados.
    action: 'install' ou 'uninstall'
    """
    global _CURRENT_PROGRESS
    with _INSTALL_LOCK:
        _CANCEL_FLAG.clear()
        _CURRENT_PROGRESS = {
            "running": True,
            "action": action,
            "total": len(app_ids),
            "done": 0,
            "current": "",
            "log": []
        }

        # Mapeia IDs para objetos do catálogo
        catalog_map = {a["id"]: a for a in SOFTWARE_CATALOG}
        success_count = 0
        failed_count = 0

        for aid in app_ids:
            if _CANCEL_FLAG.is_set():
                _CURRENT_PROGRESS["log"].append("Operação cancelada pelo utilizador.")
                break

            app_info = catalog_map.get(aid)
            if not app_info:
                continue

            name = app_info["name"]
            wid = app_info["winget"]
            _CURRENT_PROGRESS["current"] = f"A processar {name}..."
            _CURRENT_PROGRESS["log"].append(f"A iniciar {action} de {name} ({wid})...")

            if action == "install":
                ok = install_app_silent(wid)
            else:
                ok = uninstall_app_silent(wid)

            if ok:
                success_count += 1
                _CURRENT_PROGRESS["log"].append(f"✔ {name} concluído com sucesso!")
            else:
                failed_count += 1
                _CURRENT_PROGRESS["log"].append(f"✘ Falha ou já atualizado em {name}.")

            _CURRENT_PROGRESS["done"] += 1

        _CURRENT_PROGRESS["running"] = False
        _CURRENT_PROGRESS["current"] = "Concluído!"

        verb = "instalados" if action == "install" else "desinstalados"
        return {
            "success": success_count > 0 or failed_count == 0,
            "success_count": success_count,
            "failed_count": failed_count,
            "output": f"{success_count} programas {verb} com sucesso."
        }


def get_progress():
    """Consulta o progresso em tempo real da operação em lote."""
    return dict(_CURRENT_PROGRESS)


def cancel_batch():
    """Sinaliza cancelamento da fila."""
    _CANCEL_FLAG.set()
    return {"success": True, "output": "A cancelar..."}
