#!/usr/bin/env python3
"""
Script automatisé pour prendre des captures d'écran de l'application GetYourShare
et générer un template HTML interactif.

Usage:
    python auto_screenshot.py

Prérequis:
    pip install playwright
    playwright install chromium
"""

import asyncio
import os
import sys
from pathlib import Path

# Vérifier si playwright est installé
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright n'est pas installé.")
    print("📦 Installation en cours...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright

# Configuration
BASE_URL = "http://localhost:5173"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
OUTPUT_HTML = Path(__file__).parent / "GUIDE_INTERACTIF.html"

# Credentials pour les différents rôles
CREDENTIALS = {
    "influencer": {"email": "influencer@test.com", "password": "Test123!"},
    "merchant": {"email": "merchant@test.com", "password": "Test123!"},
    "admin": {"email": "admin@test.com", "password": "Test123!"},
}

# Liste des pages à capturer
PAGES_TO_CAPTURE = [
    # Espace Influenceur
    {"name": "01_page_accueil", "url": "/", "title": "Page d'Accueil", "role": None, "section": "general"},
    {"name": "02_login", "url": "/login", "title": "Page de Connexion", "role": None, "section": "general"},
    {"name": "03_register", "url": "/register", "title": "Page d'Inscription", "role": None, "section": "general"},
    {"name": "04_dashboard_influenceur", "url": "/dashboard/influencer", "title": "Dashboard Influenceur", "role": "influencer", "section": "influencer"},
    {"name": "05_marketplace", "url": "/marketplace", "title": "Marketplace", "role": "influencer", "section": "influencer"},
    {"name": "06_mes_liens", "url": "/influencer/my-links", "title": "Mes Liens d'Affiliation", "role": "influencer", "section": "influencer"},
    {"name": "07_live_shopping", "url": "/influencer/live-shopping", "title": "Live Shopping Studio", "role": "influencer", "section": "influencer"},
    {"name": "08_content_ia", "url": "/influencer/ai-content", "title": "Générateur de Contenu IA", "role": "influencer", "section": "influencer"},
    {"name": "09_smart_matching", "url": "/influencer/matching", "title": "Smart Matching", "role": "influencer", "section": "influencer"},
    {"name": "10_wallet", "url": "/influencer/payouts", "title": "Wallet & Revenus", "role": "influencer", "section": "influencer"},
    {"name": "11_analytics", "url": "/influencer/analytics", "title": "Analytics", "role": "influencer", "section": "influencer"},
    {"name": "12_messages", "url": "/messages", "title": "Messagerie", "role": "influencer", "section": "influencer"},
    
    # Espace Marchand
    {"name": "14_dashboard_marchand", "url": "/dashboard/merchant", "title": "Dashboard Marchand", "role": "merchant", "section": "merchant"},
    {"name": "15_produits", "url": "/merchant/products", "title": "Gestion des Produits", "role": "merchant", "section": "merchant"},
    {"name": "16_commissions", "url": "/merchant/commissions", "title": "Configuration des Commissions", "role": "merchant", "section": "merchant"},
    {"name": "17_analytics_marchand", "url": "/merchant/analytics", "title": "Analytics Marchand", "role": "merchant", "section": "merchant"},
    
    # Espace Admin
    {"name": "22_dashboard_admin", "url": "/admin/dashboard", "title": "Dashboard Admin", "role": "admin", "section": "admin"},
    {"name": "23_users_admin", "url": "/admin/users", "title": "Gestion des Utilisateurs", "role": "admin", "section": "admin"},
    {"name": "24_transactions_admin", "url": "/admin/transactions", "title": "Gestion des Transactions", "role": "admin", "section": "admin"},
    {"name": "25_settings_admin", "url": "/admin/settings", "title": "Paramètres Système", "role": "admin", "section": "admin"},
]


async def login(page, role):
    """Connecte l'utilisateur avec le rôle spécifié."""
    if role not in CREDENTIALS:
        return False
    
    creds = CREDENTIALS[role]
    await page.goto(f"{BASE_URL}/login")
    await page.wait_for_load_state("networkidle")
    
    # Remplir le formulaire de connexion
    try:
        await page.fill('input[type="email"], input[name="email"]', creds["email"])
        await page.fill('input[type="password"], input[name="password"]', creds["password"])
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # Attendre la redirection
        return True
    except Exception as e:
        print(f"⚠️ Erreur de connexion pour {role}: {e}")
        return False


async def take_screenshot(page, page_config):
    """Prend une capture d'écran d'une page."""
    name = page_config["name"]
    url = page_config["url"]
    
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    
    try:
        await page.goto(f"{BASE_URL}{url}")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)  # Attendre les animations
        
        # Screenshot pleine page
        await page.screenshot(path=str(filepath), full_page=True)
        print(f"✅ {name}.png - {page_config['title']}")
        return True
    except Exception as e:
        print(f"❌ {name}.png - Erreur: {e}")
        return False


async def main():
    """Fonction principale."""
    print("=" * 60)
    print("🚀 GetYourShare - Générateur de Screenshots Automatique")
    print("=" * 60)
    
    # Créer le dossier screenshots
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # Lancer le navigateur
        browser = await p.chromium.launch(headless=False)  # headless=False pour voir ce qui se passe
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        current_role = None
        success_count = 0
        
        for page_config in PAGES_TO_CAPTURE:
            role = page_config["role"]
            
            # Changer de rôle si nécessaire
            if role != current_role and role is not None:
                print(f"\n🔐 Connexion en tant que {role}...")
                await login(page, role)
                current_role = role
            
            # Prendre la capture
            if await take_screenshot(page, page_config):
                success_count += 1
        
        await browser.close()
    
    print("\n" + "=" * 60)
    print(f"📸 {success_count}/{len(PAGES_TO_CAPTURE)} captures réalisées")
    print("=" * 60)
    
    # Générer le HTML
    generate_html_template()
    
    print(f"\n✨ Template HTML généré: {OUTPUT_HTML}")
    print("\n📖 Pour visualiser le guide, ouvrez le fichier HTML dans votre navigateur.")


def generate_html_template():
    """Génère le template HTML interactif avec les screenshots."""
    
    # Vérifier quels screenshots existent
    screenshots = {}
    for page_config in PAGES_TO_CAPTURE:
        name = page_config["name"]
        filepath = SCREENSHOTS_DIR / f"{name}.png"
        screenshots[name] = {
            "exists": filepath.exists(),
            "path": f"screenshots/{name}.png",
            "title": page_config["title"],
            "section": page_config["section"],
            "url": page_config["url"]
        }
    
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GetYourShare - Guide Complet de l'Application</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e1b4b;
            --light: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-500: #64748b;
            --gray-700: #334155;
            --gray-900: #0f172a;
            --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --gradient-2: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gray-100);
            color: var(--gray-900);
            line-height: 1.6;
        }}

        /* Header */
        .header {{
            background: var(--gradient-2);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }}

        .header-content {{
            position: relative;
            z-index: 1;
            max-width: 900px;
            margin: 0 auto;
        }}

        .logo {{
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .badge {{
            display: inline-block;
            background: var(--gradient-1);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 1.5rem;
        }}

        /* Navigation */
        .nav {{
            background: white;
            border-bottom: 1px solid var(--gray-200);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow);
        }}

        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            gap: 0;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .nav-item {{
            padding: 1rem 1.5rem;
            color: var(--gray-500);
            text-decoration: none;
            font-weight: 500;
            white-space: nowrap;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }}

        .nav-item:hover, .nav-item.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
            background: var(--gray-100);
        }}

        .nav-item.influencer {{
            border-left: 3px solid var(--success);
        }}

        .nav-item.merchant {{
            border-left: 3px solid var(--warning);
        }}

        .nav-item.admin {{
            border-left: 3px solid var(--danger);
        }}

        /* Main Content */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        /* Section */
        .section {{
            margin-bottom: 4rem;
            scroll-margin-top: 80px;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--gray-200);
        }}

        .section-icon {{
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }}

        .section-icon.influencer {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}

        .section-icon.merchant {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}

        .section-icon.admin {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }}

        .section-icon.general {{
            background: var(--gradient-1);
        }}

        .section-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--dark);
        }}

        .section-subtitle {{
            color: var(--gray-500);
            font-size: 0.95rem;
        }}

        /* Screenshot Cards */
        .screenshots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 2rem;
        }}

        .screenshot-card {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow-lg);
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .screenshot-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-xl);
        }}

        .screenshot-header {{
            padding: 1.25rem 1.5rem;
            background: var(--gray-100);
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .screenshot-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--gray-900);
        }}

        .screenshot-url {{
            font-size: 0.8rem;
            color: var(--gray-500);
            font-family: 'Monaco', 'Consolas', monospace;
            background: var(--gray-200);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
        }}

        .screenshot-image-container {{
            position: relative;
            padding: 1rem;
            background: #f0f0f0;
            min-height: 300px;
        }}

        .screenshot-image {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease;
        }}

        .screenshot-card:hover .screenshot-image {{
            transform: scale(1.02);
        }}

        .screenshot-placeholder {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 300px;
            color: var(--gray-500);
            text-align: center;
            padding: 2rem;
        }}

        .screenshot-placeholder svg {{
            width: 64px;
            height: 64px;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            padding: 2rem;
            overflow: auto;
        }}

        .modal.active {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .modal-close {{
            position: fixed;
            top: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: white;
            border: none;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-lg);
            transition: transform 0.3s ease;
        }}

        .modal-close:hover {{
            transform: scale(1.1);
        }}

        .modal-content {{
            max-width: 95vw;
            max-height: 90vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: var(--shadow-xl);
        }}

        .modal-title {{
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
        }}

        /* Table of Contents */
        .toc {{
            background: white;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 3rem;
            box-shadow: var(--shadow);
        }}

        .toc h2 {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
            color: var(--dark);
        }}

        .toc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }}

        .toc-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            background: var(--gray-100);
            border-radius: 8px;
            text-decoration: none;
            color: var(--gray-700);
            transition: all 0.2s ease;
        }}

        .toc-item:hover {{
            background: var(--primary);
            color: white;
            transform: translateX(5px);
        }}

        .toc-number {{
            width: 28px;
            height: 28px;
            background: var(--gradient-1);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        /* Stats */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow);
        }}

        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            color: var(--gray-500);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        /* Footer */
        .footer {{
            background: var(--dark);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}

        .footer p {{
            opacity: 0.7;
        }}

        /* Print Styles */
        @media print {{
            .nav, .modal, .toc {{
                display: none !important;
            }}
            
            .header {{
                padding: 2rem;
            }}
            
            .screenshot-card {{
                break-inside: avoid;
                page-break-inside: avoid;
                box-shadow: none;
                border: 1px solid #ddd;
            }}
            
            .screenshots-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .screenshots-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header {{
                padding: 2rem 1rem;
            }}
            
            .logo {{
                font-size: 2.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <div class="logo">GetYourShare</div>
            <h1>Guide Complet de l'Application</h1>
            <p>Documentation visuelle interactive de toutes les fonctionnalités</p>
            <span class="badge">📸 Captures d'écran automatiques</span>
        </div>
    </header>

    <!-- Navigation -->
    <nav class="nav">
        <div class="nav-container">
            <a href="#general" class="nav-item">🏠 Général</a>
            <a href="#influencer" class="nav-item influencer">👤 Espace Influenceur</a>
            <a href="#merchant" class="nav-item merchant">🏪 Espace Marchand</a>
            <a href="#admin" class="nav-item admin">⚙️ Espace Admin</a>
        </div>
    </nav>

    <div class="container">
        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len([s for s in screenshots.values() if s['exists']])}</div>
                <div class="stat-label">Screenshots capturés</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(screenshots)}</div>
                <div class="stat-label">Pages documentées</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Espaces utilisateur</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">100%</div>
                <div class="stat-label">Couverture</div>
            </div>
        </div>

        <!-- Table of Contents -->
        <div class="toc">
            <h2>📑 Table des Matières</h2>
            <div class="toc-grid">
                {"".join([f'''
                <a href="#{name}" class="toc-item">
                    <span class="toc-number">{i+1}</span>
                    <span>{info['title']}</span>
                </a>''' for i, (name, info) in enumerate(screenshots.items())])}
            </div>
        </div>

        <!-- Sections -->
        {"".join([generate_section_html(section, screenshots) for section in ['general', 'influencer', 'merchant', 'admin']])}
    </div>

    <!-- Modal -->
    <div class="modal" id="imageModal">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <img src="" alt="" class="modal-content" id="modalImage">
        <div class="modal-title" id="modalTitle"></div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <p>GetYourShare &copy; 2024 - Documentation générée automatiquement</p>
    </footer>

    <script>
        // Modal functionality
        function openModal(src, title) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalTitle = document.getElementById('modalTitle');
            
            modal.classList.add('active');
            modalImg.src = src;
            modalTitle.textContent = title;
            document.body.style.overflow = 'hidden';
        }}

        function closeModal() {{
            document.getElementById('imageModal').classList.remove('active');
            document.body.style.overflow = '';
        }}

        document.getElementById('imageModal').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeModal();
            }}
        }});

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeModal();
            }}
        }});

        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});

        // Active navigation state
        const sections = document.querySelectorAll('.section');
        const navItems = document.querySelectorAll('.nav-item');

        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                if (pageYOffset >= sectionTop - 100) {{
                    current = section.getAttribute('id');
                }}
            }});

            navItems.forEach(item => {{
                item.classList.remove('active');
                if (item.getAttribute('href') === '#' + current) {{
                    item.classList.add('active');
                }}
            }});
        }});
    </script>
</body>
</html>
'''
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_section_html(section, screenshots):
    """Génère le HTML pour une section."""
    section_config = {
        'general': {'title': 'Pages Générales', 'icon': '🏠', 'subtitle': 'Accueil, connexion et inscription'},
        'influencer': {'title': 'Espace Influenceur', 'icon': '👤', 'subtitle': 'Dashboard, marketplace, liens d\'affiliation et outils'},
        'merchant': {'title': 'Espace Marchand', 'icon': '🏪', 'subtitle': 'Gestion des produits et des commissions'},
        'admin': {'title': 'Espace Administrateur', 'icon': '⚙️', 'subtitle': 'Gestion de la plateforme'},
    }
    
    config = section_config.get(section, {})
    items = {k: v for k, v in screenshots.items() if v['section'] == section}
    
    if not items:
        return ''
    
    cards_html = ''
    for name, info in items.items():
        if info['exists']:
            image_html = f'''
            <div class="screenshot-image-container">
                <img src="{info['path']}" alt="{info['title']}" class="screenshot-image" 
                     onclick="openModal('{info['path']}', '{info['title']}')" loading="lazy">
            </div>'''
        else:
            image_html = '''
            <div class="screenshot-placeholder">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <p><strong>Capture non disponible</strong></p>
                <p style="font-size: 0.85rem;">Lancez le script auto_screenshot.py</p>
            </div>'''
        
        cards_html += f'''
        <div class="screenshot-card" id="{name}">
            <div class="screenshot-header">
                <span class="screenshot-title">{info['title']}</span>
                <span class="screenshot-url">{info['url']}</span>
            </div>
            {image_html}
        </div>'''
    
    return f'''
    <section class="section" id="{section}">
        <div class="section-header">
            <div class="section-icon {section}">{config.get('icon', '📄')}</div>
            <div>
                <h2 class="section-title">{config.get('title', section.capitalize())}</h2>
                <p class="section-subtitle">{config.get('subtitle', '')}</p>
            </div>
        </div>
        <div class="screenshots-grid">
            {cards_html}
        </div>
    </section>'''


if __name__ == "__main__":
    # On génère d'abord le template HTML même sans screenshots
    print("🎨 Génération du template HTML initial...")
    generate_html_template()
    print(f"✅ Template HTML créé: {OUTPUT_HTML}")
    
    # Ensuite, on tente de prendre les screenshots
    print("\n📸 Lancement de la capture automatique...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n⚠️ Impossible de prendre les screenshots automatiquement: {e}")
        print("💡 Assurez-vous que:")
        print("   1. Le frontend est lancé (npm run dev)")
        print("   2. Le backend est lancé (python run.py)")
        print("   3. Playwright est installé (pip install playwright && playwright install chromium)")
