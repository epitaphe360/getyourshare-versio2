"""
Service d'optimisation d'images automatique
Pipeline complet de transformation, compression et génération de formats optimaux
"""
import io
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageFilter, ImageOps, ExifTags
import tempfile

from utils.logger import logger
from utils.image_processing import (
    validate_image,
    calculate_optimal_quality,
    generate_blurhash,
    analyze_image_colors,
    detect_faces,
    calculate_sharpness,
    estimate_compression_ratio,
    get_safe_filename,
    ImageValidationError
)


import tempfile

# Configuration des tailles de thumbnails
THUMBNAIL_SIZES = {
    'thumbnail': (150, 150),    # Très petit pour listes
    'small': (320, 320),        # Mobile portrait
    'medium': (640, 640),       # Tablette
    'large': (1024, 1024),      # Desktop
    'xl': (1920, 1920)          # Full HD
}

# Configuration de compression par défaut
DEFAULT_QUALITY = {
    'webp': 85,
    'avif': 80,
    'jpeg': 85,
    'png': 95
}


class ImageOptimizer:
    """
    Service d'optimisation d'images avec support multi-format
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        enable_avif: bool = True,
        enable_webp: bool = True
    ):
        """
        Initialise le service d'optimisation

        Args:
            storage_path: Chemin de stockage des images optimisées
            enable_avif: Activer la génération AVIF
            enable_webp: Activer la génération WebP
        """
        if storage_path is None:
            storage_path = os.path.join(tempfile.gettempdir(), 'optimized_images')
            
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.enable_avif = enable_avif
        self.enable_webp = enable_webp

        logger.info(
            "ImageOptimizer initialisé",
            storage_path=str(storage_path),
            avif_enabled=enable_avif,
            webp_enabled=enable_webp
        )

    def optimize_image(
        self,
        image_data: bytes,
        filename: str,
        generate_formats: Optional[List[str]] = None,
        quality: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimise une image et génère plusieurs formats

        Args:
            image_data: Données binaires de l'image
            filename: Nom du fichier original
            generate_formats: Formats à générer (webp, avif, jpeg)
            quality: Qualité de compression (None = auto)

        Returns:
            Dictionnaire avec les URLs et métadonnées
        """
        start_time = time.time()

        try:
            # Validation
            validation_result = validate_image(image_data, filename)
            logger.info(f"Image validée: {filename}", **validation_result)

            # Charger l'image
            image = Image.open(io.BytesIO(image_data))

            # Correction d'orientation EXIF
            image = self._fix_orientation(image)

            # Formats à générer
            if generate_formats is None:
                generate_formats = []
                if self.enable_webp:
                    generate_formats.append('webp')
                if self.enable_avif:
                    generate_formats.append('avif')
                generate_formats.append('jpeg')  # Toujours générer JPEG comme fallback

            # Extraire métadonnées
            metadata = self.extract_metadata(image, filename)

            # Générer les formats optimisés
            optimized_formats = {}
            for fmt in generate_formats:
                try:
                    optimized = self._optimize_format(
                        image,
                        fmt,
                        quality or calculate_optimal_quality(image, fmt)
                    )
                    optimized_formats[fmt] = optimized
                    logger.info(
                        f"Format généré: {fmt}",
                        size_kb=optimized['size'] / 1024,
                        compression=optimized['compression']['percentage']
                    )
                except Exception as e:
                    logger.error(f"Erreur génération format {fmt}: {str(e)}")

            duration = time.time() - start_time

            result = {
                'success': True,
                'original': {
                    'filename': filename,
                    'size': len(image_data),
                    'format': validation_result['format'],
                    'dimensions': {
                        'width': validation_result['width'],
                        'height': validation_result['height']
                    }
                },
                'optimized': optimized_formats,
                'metadata': metadata,
                'processing_time': round(duration, 3)
            }

            logger.info(
                f"Image optimisée avec succès: {filename}",
                duration_ms=duration * 1000,
                formats_generated=len(optimized_formats)
            )

            return result

        except ImageValidationError as e:
            logger.error(f"Validation échouée: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'validation'
            }
        except Exception as e:
            logger.error(f"Erreur optimisation image: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'processing'
            }

    def generate_thumbnails(
        self,
        image_data: bytes,
        filename: str,
        sizes: Optional[Dict[str, Tuple[int, int]]] = None,
        formats: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Génère plusieurs tailles de thumbnails

        Args:
            image_data: Données binaires de l'image
            filename: Nom du fichier
            sizes: Dict des tailles personnalisées
            formats: Formats à générer pour chaque taille

        Returns:
            Dict avec tous les thumbnails générés
        """
        start_time = time.time()

        try:
            # Validation
            validate_image(image_data, filename)

            # Charger l'image
            image = Image.open(io.BytesIO(image_data))
            image = self._fix_orientation(image)

            # Utiliser les tailles par défaut si non spécifiées
            if sizes is None:
                sizes = THUMBNAIL_SIZES

            # Formats par défaut
            if formats is None:
                formats = ['webp', 'jpeg']

            thumbnails = {}

            for size_name, (width, height) in sizes.items():
                thumbnails[size_name] = {}

                # Créer le thumbnail
                thumb = self._create_thumbnail(image, width, height)

                # Générer dans chaque format
                for fmt in formats:
                    try:
                        quality = calculate_optimal_quality(thumb, fmt)
                        optimized = self._optimize_format(thumb, fmt, quality)

                        thumbnails[size_name][fmt] = {
                            'data': optimized['data'],
                            'size': optimized['size'],
                            'dimensions': {
                                'width': thumb.width,
                                'height': thumb.height
                            },
                            'url': optimized.get('url')
                        }

                        logger.debug(
                            f"Thumbnail généré: {size_name} ({fmt})",
                            size_kb=optimized['size'] / 1024
                        )

                    except Exception as e:
                        logger.error(
                            f"Erreur génération thumbnail {size_name}/{fmt}: {str(e)}"
                        )

            duration = time.time() - start_time

            logger.info(
                f"Thumbnails générés: {filename}",
                count=len(thumbnails),
                duration_ms=duration * 1000
            )

            return {
                'success': True,
                'thumbnails': thumbnails,
                'sizes_generated': list(thumbnails.keys()),
                'processing_time': round(duration, 3)
            }

        except Exception as e:
            logger.error(f"Erreur génération thumbnails: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def extract_metadata(
        self,
        image: Image.Image,
        filename: str
    ) -> Dict[str, Any]:
        """
        Extrait les métadonnées complètes d'une image

        Args:
            image: Image PIL
            filename: Nom du fichier

        Returns:
            Dictionnaire de métadonnées
        """
        try:
            metadata = {
                'filename': filename,
                'format': image.format or 'unknown',
                'mode': image.mode,
                'dimensions': {
                    'width': image.width,
                    'height': image.height
                },
                'aspect_ratio': round(image.width / image.height, 2),
                'created_at': datetime.utcnow().isoformat()
            }

            # EXIF data
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    # Filtrer les données binaires
                    if isinstance(value, (str, int, float)):
                        exif_data[tag] = value

            metadata['exif'] = exif_data

            # Palette de couleurs
            metadata['colors'] = analyze_image_colors(image, num_colors=5)

            # Blurhash pour placeholder
            metadata['blurhash'] = generate_blurhash(image)

            # Netteté
            metadata['sharpness'] = calculate_sharpness(image)

            # Détection de visages (zones d'intérêt)
            metadata['faces'] = detect_faces(image)

            logger.debug(f"Métadonnées extraites: {filename}")

            return metadata

        except Exception as e:
            logger.error(f"Erreur extraction métadonnées: {str(e)}")
            return {
                'filename': filename,
                'error': str(e)
            }

    def remove_background(
        self,
        image_data: bytes,
        output_format: str = 'png'
    ) -> Optional[bytes]:
        """
        Supprime le fond d'une image
        Note: Nécessite la librairie rembg

        Args:
            image_data: Données binaires de l'image
            output_format: Format de sortie

        Returns:
            Image sans fond (bytes) ou None si erreur
        """
        try:
            # Import conditionnel de rembg
            try:
                from rembg import remove
            except ImportError:
                logger.warning("rembg non installé, suppression de fond désactivée")
                return None

            # Supprimer le fond
            output_data = remove(image_data)

            # Convertir si nécessaire
            if output_format != 'png':
                image = Image.open(io.BytesIO(output_data))
                buffer = io.BytesIO()
                image.save(buffer, format=output_format.upper())
                output_data = buffer.getvalue()

            logger.info("Fond supprimé avec succès")

            return output_data

        except Exception as e:
            logger.error(f"Erreur suppression fond: {str(e)}")
            return None

    def compress_smart(
        self,
        image_data: bytes,
        filename: str,
        target_size_kb: Optional[int] = None,
        preserve_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Compression intelligente avec adaptation selon le contenu

        Args:
            image_data: Données binaires de l'image
            filename: Nom du fichier
            target_size_kb: Taille cible en KB
            preserve_quality: Préserver la qualité maximale

        Returns:
            Image compressée avec statistiques
        """
        try:
            # Charger l'image
            image = Image.open(io.BytesIO(image_data))
            image = self._fix_orientation(image)

            # Analyser le contenu
            sharpness = calculate_sharpness(image)
            colors = analyze_image_colors(image)

            # Déterminer le meilleur format
            has_transparency = image.mode in ('RGBA', 'LA', 'P')
            is_simple = len(colors) <= 10 or sharpness < 100

            if has_transparency:
                best_format = 'png' if is_simple else 'webp'
            else:
                best_format = 'webp' if self.enable_webp else 'jpeg'

            # Calculer la qualité
            if target_size_kb:
                quality = calculate_optimal_quality(
                    image,
                    best_format,
                    target_size_kb * 1024
                )
            else:
                quality = calculate_optimal_quality(image, best_format)

            # Ajuster selon preserve_quality
            if preserve_quality:
                quality = max(quality, 80)

            # Compresser
            compressed = self._optimize_format(image, best_format, quality)

            # Calculer les stats
            compression_stats = estimate_compression_ratio(
                len(image_data),
                compressed['size']
            )

            result = {
                'success': True,
                'original_size': len(image_data),
                'compressed_size': compressed['size'],
                'format': best_format,
                'quality': quality,
                'compression': compression_stats,
                'data': compressed['data'],
                'url': compressed.get('url'),
                'analysis': {
                    'sharpness': sharpness,
                    'color_count': len(colors),
                    'has_transparency': has_transparency
                }
            }

            logger.info(
                f"Compression intelligente: {filename}",
                format=best_format,
                saved_percentage=compression_stats['percentage']
            )

            return result

        except Exception as e:
            logger.error(f"Erreur compression intelligente: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_responsive_srcset(
        self,
        image_data: bytes,
        filename: str,
        base_url: str = ''
    ) -> Dict[str, Any]:
        """
        Génère un srcset complet pour images responsive

        Args:
            image_data: Données binaires de l'image
            filename: Nom du fichier
            base_url: URL de base pour les images

        Returns:
            Dict avec srcset pour différents formats
        """
        try:
            # Générer tous les thumbnails
            thumbnails_result = self.generate_thumbnails(
                image_data,
                filename,
                formats=['webp', 'jpeg']
            )

            if not thumbnails_result['success']:
                raise Exception(thumbnails_result.get('error'))

            thumbnails = thumbnails_result['thumbnails']

            # Construire les srcsets
            srcsets = {
                'webp': [],
                'jpeg': []
            }

            safe_name = get_safe_filename(filename)
            base_name = Path(safe_name).stem

            for size_name, size_data in thumbnails.items():
                width = size_data.get('webp', size_data.get('jpeg', {})).get(
                    'dimensions', {}
                ).get('width')

                if width:
                    for fmt in ['webp', 'jpeg']:
                        if fmt in size_data:
                            url = f"{base_url}/{base_name}_{size_name}.{fmt}"
                            srcsets[fmt].append(f"{url} {width}w")

            # Générer les chaînes srcset
            result = {
                'success': True,
                'srcset': {
                    'webp': ', '.join(srcsets['webp']),
                    'jpeg': ', '.join(srcsets['jpeg'])
                },
                'sizes': {
                    size: data.get('webp', data.get('jpeg', {})).get('dimensions')
                    for size, data in thumbnails.items()
                },
                'thumbnails': thumbnails
            }

            logger.info(f"Srcset généré pour: {filename}")

            return result

        except Exception as e:
            logger.error(f"Erreur génération srcset: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # Méthodes privées

    def _fix_orientation(self, image: Image.Image) -> Image.Image:
        """
        Corrige l'orientation d'une image selon EXIF
        """
        try:
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                orientation_key = next(
                    (k for k, v in ExifTags.TAGS.items() if v == 'Orientation'),
                    None
                )

                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]

                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)

                    logger.debug(f"Orientation corrigée: {orientation}")

        except Exception as e:
            logger.debug(f"Pas de correction d'orientation: {str(e)}")

        return image

    def _create_thumbnail(
        self,
        image: Image.Image,
        width: int,
        height: int,
        method: str = 'cover'
    ) -> Image.Image:
        """
        Crée un thumbnail avec différentes méthodes de redimensionnement
        """
        if method == 'cover':
            # Crop pour remplir exactement les dimensions
            return ImageOps.fit(
                image,
                (width, height),
                method=Image.Resampling.LANCZOS
            )
        elif method == 'contain':
            # Thumbnail qui tient dans les dimensions
            thumb = image.copy()
            thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
            return thumb
        else:
            # Par défaut: cover
            return ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)

    def _optimize_format(
        self,
        image: Image.Image,
        format: str,
        quality: int
    ) -> Dict[str, Any]:
        """
        Optimise une image dans un format spécifique
        """
        buffer = io.BytesIO()

        # Conversion de mode si nécessaire
        if format in ('jpeg', 'jpg'):
            if image.mode in ('RGBA', 'LA', 'P'):
                # JPEG ne supporte pas la transparence
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            image.save(
                buffer,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )

        elif format == 'webp':
            image.save(
                buffer,
                format='WEBP',
                quality=quality,
                method=6,  # Meilleure compression
                optimize=True
            )

        elif format == 'avif':
            # AVIF nécessite pillow-heif
            image.save(
                buffer,
                format='AVIF',
                quality=quality
            )

        elif format == 'png':
            if image.mode not in ('RGB', 'RGBA', 'P'):
                image = image.convert('RGBA')

            image.save(
                buffer,
                format='PNG',
                optimize=True,
                compress_level=9
            )

        data = buffer.getvalue()

        return {
            'format': format,
            'data': data,
            'size': len(data),
            'quality': quality,
            'compression': estimate_compression_ratio(
                len(image.tobytes()),
                len(data)
            )
        }
