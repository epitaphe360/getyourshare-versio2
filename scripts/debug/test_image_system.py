#!/usr/bin/env python3
"""
Script de validation rapide du système d'optimisation d'images
Vérifie que toutes les dépendances sont installées et que le système fonctionne
"""
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")

    required = {
        'Pillow': 'PIL',
        'numpy': 'numpy',
        'pillow-heif': 'pillow_heif'
    }

    optional = {
        'rembg': 'rembg'
    }

    missing = []
    missing_optional = []

    for name, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✅ {name} installé")
        except ImportError:
            print(f"  ❌ {name} MANQUANT")
            missing.append(name)

    for name, import_name in optional.items():
        try:
            __import__(import_name)
            print(f"  ✅ {name} installé (optionnel)")
        except ImportError:
            print(f"  ⚠️  {name} non installé (optionnel)")
            missing_optional.append(name)

    if missing:
        print(f"\n❌ Dépendances manquantes: {', '.join(missing)}")
        print("Installez avec: pip install -r requirements-image-optimization.txt")
        return False

    if missing_optional:
        print(f"\nℹ️  Fonctionnalités optionnelles désactivées: {', '.join(missing_optional)}")

    print("\n✅ Toutes les dépendances requises sont installées!")
    return True


def test_image_processing():
    """Test des utilitaires de traitement d'images"""
    print("\n🧪 Test des utilitaires de traitement...")

    try:
        from backend.utils.image_processing import (
            validate_image,
            calculate_optimal_quality,
            generate_blurhash,
            analyze_image_colors,
            get_safe_filename
        )
        from PIL import Image
        import io

        # Créer une image de test
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_data = buffer.getvalue()

        # Test 1: Validation
        result = validate_image(image_data, 'test.jpg')
        assert result['valid'] is True
        print("  ✅ Validation d'image fonctionne")

        # Test 2: Qualité optimale
        quality = calculate_optimal_quality(img, 'webp')
        assert 50 <= quality <= 100
        print("  ✅ Calcul qualité optimale fonctionne")

        # Test 3: Blurhash
        blurhash = generate_blurhash(img)
        assert blurhash is not None
        print("  ✅ Génération blurhash fonctionne")

        # Test 4: Analyse couleurs
        colors = analyze_image_colors(img, num_colors=3)
        assert len(colors) > 0
        print("  ✅ Analyse de couleurs fonctionne")

        # Test 5: Nom de fichier sécurisé
        safe = get_safe_filename('Mon Image (2023)!.jpg')
        assert ' ' not in safe
        print("  ✅ Nettoyage nom de fichier fonctionne")

        print("\n✅ Tous les tests utilitaires réussis!")
        return True

    except Exception as e:
        print(f"\n❌ Erreur dans les tests utilitaires: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_optimizer():
    """Test du service ImageOptimizer"""
    print("\n🧪 Test du service ImageOptimizer...")

    try:
        from backend.services.image_optimizer import ImageOptimizer
        from PIL import Image
        import io

        # Créer une image de test
        img = Image.new('RGB', (800, 600), color=(255, 100, 50))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        image_data = buffer.getvalue()

        # Initialiser l'optimizer
        optimizer = ImageOptimizer(
            storage_path='/tmp/test_images',
            enable_avif=False,  # Désactiver AVIF pour tests rapides
            enable_webp=True
        )
        print("  ✅ ImageOptimizer initialisé")

        # Test 1: Optimisation basique
        result = optimizer.optimize_image(
            image_data=image_data,
            filename='test.jpg',
            generate_formats=['webp', 'jpeg']
        )
        assert result['success'] is True
        assert 'webp' in result['optimized']
        assert 'jpeg' in result['optimized']
        print("  ✅ Optimisation basique réussie")

        # Test 2: Génération de thumbnails
        result = optimizer.generate_thumbnails(
            image_data=image_data,
            filename='test.jpg',
            formats=['jpeg']
        )
        assert result['success'] is True
        assert len(result['thumbnails']) == 5  # 5 tailles
        print("  ✅ Génération de thumbnails réussie")

        # Test 3: Compression intelligente
        result = optimizer.compress_smart(
            image_data=image_data,
            filename='test.jpg',
            preserve_quality=True
        )
        assert result['success'] is True
        assert result['compressed_size'] < result['original_size']
        print("  ✅ Compression intelligente réussie")

        # Test 4: Srcset responsive
        result = optimizer.generate_responsive_srcset(
            image_data=image_data,
            filename='test.jpg',
            base_url='https://cdn.example.com'
        )
        assert result['success'] is True
        assert 'srcset' in result
        print("  ✅ Génération srcset réussie")

        # Test 5: Extraction métadonnées
        metadata = optimizer.extract_metadata(img, 'test.jpg')
        assert 'dimensions' in metadata
        assert 'colors' in metadata
        assert 'blurhash' in metadata
        print("  ✅ Extraction métadonnées réussie")

        print("\n✅ Tous les tests ImageOptimizer réussis!")
        return True

    except Exception as e:
        print(f"\n❌ Erreur dans les tests ImageOptimizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary():
    """Affiche un résumé du système"""
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DU SYSTÈME D'OPTIMISATION D'IMAGES")
    print("="*60)

    files = {
        'Backend - Service Principal': '/home/user/versionlivrable/backend/services/image_optimizer.py',
        'Backend - Utilitaires': '/home/user/versionlivrable/backend/utils/image_processing.py',
        'Frontend - Composant React': '/home/user/versionlivrable/frontend/src/components/OptimizedImage.jsx',
        'Exemples Backend': '/home/user/versionlivrable/backend/examples/image_optimization_example.py',
        'Exemples Frontend': '/home/user/versionlivrable/frontend/src/examples/OptimizedImageExample.jsx',
        'Tests Unitaires': '/home/user/versionlivrable/backend/tests/test_image_optimizer.py',
        'Documentation': '/home/user/versionlivrable/IMAGE_OPTIMIZATION_SYSTEM.md',
        'Requirements': '/home/user/versionlivrable/requirements-image-optimization.txt'
    }

    for name, path in files.items():
        if Path(path).exists():
            size = Path(path).stat().st_size
            lines = len(open(path).readlines())
            print(f"  ✅ {name}")
            print(f"     {path}")
            print(f"     {lines} lignes, {size/1024:.1f}KB")
        else:
            print(f"  ❌ {name} - MANQUANT")

    print("\n📚 Documentation complète:")
    print("  - IMAGE_OPTIMIZATION_SYSTEM.md")

    print("\n🚀 Pour commencer:")
    print("  1. Installer: pip install -r requirements-image-optimization.txt")
    print("  2. Tester: python test_image_system.py")
    print("  3. Exemples: python backend/examples/image_optimization_example.py")
    print("  4. Tests: pytest backend/tests/test_image_optimizer.py -v")

    print("\n" + "="*60)


def main():
    """Fonction principale"""
    print("🎨 SYSTÈME D'OPTIMISATION D'IMAGES - VALIDATION")
    print("="*60)

    # Vérifier les dépendances
    if not check_dependencies():
        print("\n⚠️  Installation requise avant de continuer")
        return 1

    # Tester les utilitaires
    if not test_image_processing():
        return 1

    # Tester le service principal
    if not test_image_optimizer():
        return 1

    # Afficher le résumé
    print_summary()

    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    print("Le système d'optimisation d'images est prêt à l'emploi.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
