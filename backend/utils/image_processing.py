"""
Utilitaires de traitement d'images
Fonctions de validation, analyse et optimisation
"""
import io
import hashlib
import colorsys
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from PIL import Image, ImageFilter, ImageStat, ExifTags

from utils.logger import logger


class ImageValidationError(Exception):
    """Exception pour les erreurs de validation d'image"""
    pass


# Configuration des formats supportés
SUPPORTED_FORMATS = {
    'jpeg': {'extensions': ['.jpg', '.jpeg'], 'mime': 'image/jpeg'},
    'png': {'extensions': ['.png'], 'mime': 'image/png'},
    'webp': {'extensions': ['.webp'], 'mime': 'image/webp'},
    'avif': {'extensions': ['.avif'], 'mime': 'image/avif'},
    'gif': {'extensions': ['.gif'], 'mime': 'image/gif'}
}

# Limites de sécurité
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_DIMENSIONS = (10000, 10000)  # 10000x10000 pixels
MIN_DIMENSIONS = (1, 1)


def validate_image(
    image_data: bytes,
    filename: str,
    max_size: int = MAX_IMAGE_SIZE,
    allowed_formats: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Valide une image uploadée

    Args:
        image_data: Données binaires de l'image
        filename: Nom du fichier
        max_size: Taille maximale en bytes
        allowed_formats: Liste des formats autorisés

    Returns:
        Dict contenant les informations de validation

    Raises:
        ImageValidationError: Si la validation échoue
    """
    try:
        # Vérifier la taille du fichier
        file_size = len(image_data)
        if file_size > max_size:
            raise ImageValidationError(
                f"Image trop grande: {file_size / 1024 / 1024:.2f}MB "
                f"(max: {max_size / 1024 / 1024:.2f}MB)"
            )

        if file_size == 0:
            raise ImageValidationError("Fichier image vide")

        # Vérifier l'extension
        file_ext = Path(filename).suffix.lower()
        if allowed_formats is None:
            allowed_formats = list(SUPPORTED_FORMATS.keys())

        format_valid = False
        detected_format = None
        for fmt, config in SUPPORTED_FORMATS.items():
            if fmt in allowed_formats and file_ext in config['extensions']:
                format_valid = True
                detected_format = fmt
                break

        if not format_valid:
            raise ImageValidationError(
                f"Format non supporté: {file_ext}. "
                f"Formats autorisés: {', '.join(allowed_formats)}"
            )

        # Ouvrir et valider l'image avec PIL
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # Vérifie l'intégrité

            # Réouvrir pour accéder aux données (verify ferme le fichier)
            image = Image.open(io.BytesIO(image_data))

        except Exception as e:
            raise ImageValidationError(f"Image corrompue ou invalide: {str(e)}")

        # Vérifier les dimensions
        width, height = image.size
        if width > MAX_DIMENSIONS[0] or height > MAX_DIMENSIONS[1]:
            raise ImageValidationError(
                f"Dimensions trop grandes: {width}x{height} "
                f"(max: {MAX_DIMENSIONS[0]}x{MAX_DIMENSIONS[1]})"
            )

        if width < MIN_DIMENSIONS[0] or height < MIN_DIMENSIONS[1]:
            raise ImageValidationError(
                f"Dimensions trop petites: {width}x{height} "
                f"(min: {MIN_DIMENSIONS[0]}x{MIN_DIMENSIONS[1]})"
            )

        # Calculer le hash pour détecter les duplicatas
        image_hash = hashlib.sha256(image_data).hexdigest()

        logger.info(
            f"Image validée avec succès: {filename}",
            width=width,
            height=height,
            format=detected_format,
            size_kb=file_size / 1024
        )

        return {
            'valid': True,
            'filename': filename,
            'format': detected_format,
            'width': width,
            'height': height,
            'size': file_size,
            'hash': image_hash,
            'aspect_ratio': width / height,
            'mode': image.mode
        }

    except ImageValidationError:
        raise
    except Exception as e:
        logger.error(f"Erreur validation image: {str(e)}")
        raise ImageValidationError(f"Erreur inattendue: {str(e)}")


def calculate_optimal_quality(
    image: Image.Image,
    target_format: str = 'webp',
    max_file_size: Optional[int] = None
) -> int:
    """
    Calcule la qualité optimale pour une image

    Args:
        image: Image PIL
        target_format: Format cible (webp, jpeg, etc.)
        max_file_size: Taille maximale souhaitée en bytes

    Returns:
        Qualité optimale (0-100)
    """
    try:
        # Analyser la complexité de l'image
        stat = ImageStat.Stat(image)

        # Calculer la variance moyenne (mesure de complexité)
        variance = sum(stat.var) / len(stat.var) if stat.var else 0

        # Base quality selon le format
        base_quality = {
            'webp': 85,
            'jpeg': 85,
            'avif': 80,
            'png': 95  # PNG est sans perte
        }.get(target_format, 85)

        # Ajuster selon la complexité
        if variance < 1000:  # Image simple (aplats de couleur)
            quality = base_quality + 5
        elif variance > 5000:  # Image complexe (beaucoup de détails)
            quality = base_quality
        else:
            quality = base_quality + 2

        # Si une taille max est spécifiée, ajuster par binary search
        if max_file_size and target_format != 'png':
            quality = _find_quality_for_size(image, target_format, max_file_size, quality)

        quality = max(50, min(100, quality))

        logger.debug(
            f"Qualité optimale calculée: {quality}",
            format=target_format,
            variance=variance
        )

        return quality

    except Exception as e:
        logger.error(f"Erreur calcul qualité: {str(e)}")
        return 85  # Valeur par défaut


def _find_quality_for_size(
    image: Image.Image,
    format: str,
    max_size: int,
    initial_quality: int
) -> int:
    """
    Trouve la qualité optimale pour atteindre une taille cible
    Utilise une recherche binaire
    """
    low, high = 50, initial_quality
    best_quality = low

    for _ in range(5):  # Max 5 itérations
        mid = (low + high) // 2

        # Tester cette qualité
        buffer = io.BytesIO()
        image.save(buffer, format=format.upper(), quality=mid, optimize=True)
        size = buffer.tell()

        if size <= max_size:
            best_quality = mid
            low = mid + 1
        else:
            high = mid - 1

    return best_quality


def generate_blurhash(image: Image.Image, components: Tuple[int, int] = (4, 3)) -> str:
    """
    Génère un blurhash pour placeholder
    Implémentation simplifiée

    Args:
        image: Image PIL
        components: Nombre de composants (x, y)

    Returns:
        String blurhash (ou couleur moyenne si blurhash non disponible)
    """
    try:
        # Pour une implémentation complète, utiliser la lib blurhash
        # Ici on retourne une couleur moyenne comme fallback

        # Redimensionner pour accélérer
        small = image.copy()
        small.thumbnail((100, 100))

        # Convertir en RGB si nécessaire
        if small.mode != 'RGB':
            small = small.convert('RGB')

        # Calculer la couleur moyenne
        stat = ImageStat.Stat(small)
        r, g, b = [int(x) for x in stat.mean[:3]]

        # Retourner en format hex
        return f"#{r:02x}{g:02x}{b:02x}"

    except Exception as e:
        logger.error(f"Erreur génération blurhash: {str(e)}")
        return "#cccccc"  # Gris par défaut


def analyze_image_colors(
    image: Image.Image,
    num_colors: int = 5
) -> List[Dict[str, Any]]:
    """
    Analyse la palette de couleurs d'une image

    Args:
        image: Image PIL
        num_colors: Nombre de couleurs dominantes à extraire

    Returns:
        Liste de couleurs avec leurs propriétés
    """
    try:
        # Convertir en RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Redimensionner pour accélérer
        small = image.copy()
        small.thumbnail((150, 150))

        # Quantifier les couleurs
        quantized = small.quantize(colors=num_colors, method=2)
        palette = quantized.getpalette()

        # Convertir en liste de couleurs
        colors = []
        for i in range(num_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]

            # Calculer HSL
            h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)

            colors.append({
                'rgb': (r, g, b),
                'hex': f"#{r:02x}{g:02x}{b:02x}",
                'hsl': {
                    'h': int(h * 360),
                    's': int(s * 100),
                    'l': int(l * 100)
                },
                'luminance': l
            })

        # Trier par luminance
        colors.sort(key=lambda x: x['luminance'], reverse=True)

        logger.debug(f"Analysé {num_colors} couleurs dominantes")

        return colors

    except Exception as e:
        logger.error(f"Erreur analyse couleurs: {str(e)}")
        return []


def detect_faces(image: Image.Image) -> List[Dict[str, int]]:
    """
    Détecte les visages dans une image pour auto-crop intelligent

    Note: Implémentation basique sans ML
    Pour une vraie détection, utiliser OpenCV ou face_recognition

    Args:
        image: Image PIL

    Returns:
        Liste de bounding boxes des visages détectés
    """
    try:
        # Cette fonction nécessiterait OpenCV ou une lib de ML
        # Implémentation simplifiée qui retourne le centre de l'image

        width, height = image.size

        # Retourner le centre comme "zone d'intérêt" par défaut
        return [{
            'x': width // 4,
            'y': height // 4,
            'width': width // 2,
            'height': height // 2,
            'confidence': 0.5,
            'method': 'center_crop'
        }]

    except Exception as e:
        logger.error(f"Erreur détection visages: {str(e)}")
        return []


def calculate_sharpness(image: Image.Image) -> float:
    """
    Calcule la netteté d'une image
    Utilise la variance du Laplacien

    Args:
        image: Image PIL

    Returns:
        Score de netteté (plus élevé = plus net)
    """
    try:
        # Convertir en grayscale
        gray = image.convert('L')

        # Appliquer filtre Laplacien
        laplacian = gray.filter(ImageFilter.FIND_EDGES)

        # Calculer la variance
        stat = ImageStat.Stat(laplacian)
        sharpness = sum(stat.var) / len(stat.var) if stat.var else 0

        logger.debug(f"Netteté calculée: {sharpness:.2f}")

        return sharpness

    except Exception as e:
        logger.error(f"Erreur calcul netteté: {str(e)}")
        return 0.0


def estimate_compression_ratio(
    original_size: int,
    compressed_size: int
) -> Dict[str, Any]:
    """
    Calcule les statistiques de compression

    Args:
        original_size: Taille originale en bytes
        compressed_size: Taille compressée en bytes

    Returns:
        Statistiques de compression
    """
    if original_size == 0:
        return {
            'ratio': 0,
            'percentage': 0,
            'saved_bytes': 0,
            'saved_kb': 0
        }

    ratio = compressed_size / original_size
    percentage = (1 - ratio) * 100
    saved = original_size - compressed_size

    return {
        'ratio': round(ratio, 3),
        'percentage': round(percentage, 1),
        'saved_bytes': saved,
        'saved_kb': round(saved / 1024, 2),
        'saved_mb': round(saved / 1024 / 1024, 2),
        'original_kb': round(original_size / 1024, 2),
        'compressed_kb': round(compressed_size / 1024, 2)
    }


def get_safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Nettoie un nom de fichier pour le rendre sûr

    Args:
        filename: Nom de fichier original
        max_length: Longueur maximale

    Returns:
        Nom de fichier sécurisé
    """
    import re

    # Garder seulement le nom et l'extension
    path = Path(filename)
    name = path.stem
    ext = path.suffix

    # Remplacer les caractères non-alphanumériques
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

    # Limiter la longueur
    if len(safe_name) > max_length - len(ext):
        safe_name = safe_name[:max_length - len(ext)]

    return safe_name + ext.lower()
