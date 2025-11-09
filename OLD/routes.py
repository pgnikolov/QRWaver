from flask import Blueprint, render_template, request, send_file, flash, jsonify, abort
from io import BytesIO
import base64

from app.config import settings
from app.services.qr_service import QRService
from social_qr import SocialQRGenerator

bp = Blueprint('main', __name__)
qr_service = QRService()
qr_generator = SocialQRGenerator()

SUPPORTED = {'facebook', 'instagram', 'linkedin'}


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/social/<platform>', methods=['GET', 'POST'])
def social_qr(platform: str):
    """
    Handles QR code generation for social media platforms.
    Supports both GET (form display) and POST (QR generation) requests.
    """
    platform = (platform or '').strip().lower()
    if platform not in SUPPORTED:
        abort(404)

    # Default UI state
    rounded_corners = False
    use_shortlink = False
    color_mode = 'color'
    success = False
    qr_base64 = shortlink = full_url = None

    if request.method == 'POST':
        try:
            profile_url = (request.form.get('profile_url') or '').strip()
            display_name = (request.form.get('display_name') or '').strip()

            # Boolean switches
            use_shortlink = 'use_shortlink' in request.form
            rounded_corners = 'rounded_corners' in request.form

            # Numeric values (validated safely)
            try:
                corner_radius = int(request.form.get('corner_radius', settings.DEFAULT_CORNER_RADIUS))
            except ValueError:
                corner_radius = settings.DEFAULT_CORNER_RADIUS
            try:
                qr_size = int(request.form.get('qr_size', settings.DEFAULT_QR_SIZE))
            except ValueError:
                qr_size = settings.DEFAULT_QR_SIZE

            # Color mode (radio buttons)
            color_mode = (request.form.get('color_mode') or 'color').strip().lower()
            if color_mode not in {'color', 'mono'}:
                color_mode = 'color'
            colorful = (color_mode == 'color')

            # Validate inputs
            errors = qr_service.validate_social_input(platform, profile_url, display_name)
            if errors:
                for msg in errors:
                    flash(msg, 'error')
                return render_template(
                    'social/_social.html',
                    platform=platform,
                    rounded_corners=rounded_corners,
                    use_shortlink=use_shortlink,
                    color_mode=color_mode,
                )

            # Generate QR code
            img, shortlink, full_url = qr_generator.generate_social_qr(
                platform=platform,
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size,
                colorful=colorful,
            )

            # Convert image to base64 for preview
            buf = BytesIO()
            img.save(buf, 'PNG', quality=95)
            buf.seek(0)
            qr_base64 = base64.b64encode(buf.getvalue()).decode('ascii')
            success = True

        except Exception as e:
            flash(f'Generation error: {str(e)}', 'error')

    # ✅ FIX: ensure color_mode reflects current POST value
    return render_template(
        'social/_social.html',
        platform=platform,
        success=success,
        qr_image=qr_base64,
        shortlink=shortlink,
        full_url=full_url,
        rounded_corners=rounded_corners,
        use_shortlink=use_shortlink,
        color_mode=request.form.get('color_mode', color_mode),
    )


@bp.route('/download/<platform>', methods=['POST'])
def download_qr(platform: str):
    """
    Handles QR code file download (PNG).
    """
    platform = (platform or '').strip().lower()
    if platform not in SUPPORTED:
        return "Invalid platform", 400

    try:
        profile_url = (request.form.get('profile_url') or '').strip()
        display_name = (request.form.get('display_name') or '').strip()
        use_shortlink = request.form.get('use_shortlink') == 'true'
        rounded_corners = request.form.get('rounded_corners') == 'true'

        # Numeric safety
        try:
            corner_radius = int(request.form.get('corner_radius', settings.DEFAULT_CORNER_RADIUS))
        except ValueError:
            corner_radius = settings.DEFAULT_CORNER_RADIUS
        try:
            qr_size = int(request.form.get('qr_size', settings.DEFAULT_QR_SIZE))
        except ValueError:
            qr_size = settings.DEFAULT_QR_SIZE

        # Fix color mode (radio input)
        color_mode = (request.form.get('color_mode') or 'color').strip().lower()
        if color_mode not in {'color', 'mono'}:
            color_mode = 'color'
        colorful = (color_mode == 'color')

        # Validate inputs
        errors = qr_service.validate_social_input(platform, profile_url, display_name)
        if errors:
            return " | ".join(errors), 400

        # Generate and send file
        img, shortlink, full_url = qr_generator.generate_social_qr(
            platform=platform,
            profile_url=profile_url,
            display_name=display_name,
            use_shortlink=use_shortlink,
            rounded_corners=rounded_corners,
            corner_radius=corner_radius,
            qr_size=qr_size,
            colorful=colorful,
        )

        buf = BytesIO()
        img.save(buf, 'PNG', quality=95)
        buf.seek(0)
        filename = qr_service.generate_filename(platform, display_name)

        return send_file(
            buf,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"Error: {str(e)}", 500


@bp.route('/api/generate', methods=['POST'])
def api_generate():
    """
    JSON API endpoint for programmatic QR generation.
    Returns Base64-encoded image and shortlink metadata.
    """
    try:
        data = request.get_json(force=True) or {}
        platform = (data.get('platform') or '').strip().lower()
        profile_url = (data.get('profile_url') or '').strip()
        display_name = (data.get('display_name') or '').strip()

        if platform not in SUPPORTED:
            return jsonify({'error': 'Invalid platform'}), 400

        use_shortlink = bool(data.get('use_shortlink', False))
        rounded_corners = bool(data.get('rounded_corners', False))
        corner_radius = int(data.get('corner_radius', settings.DEFAULT_CORNER_RADIUS))
        qr_size = int(data.get('qr_size', settings.DEFAULT_QR_SIZE))
        colorful = bool(data.get('colorful', True))

        errors = qr_service.validate_social_input(platform, profile_url, display_name)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        img, shortlink, full_url = qr_generator.generate_social_qr(
            platform=platform,
            profile_url=profile_url,
            display_name=display_name,
            use_shortlink=use_shortlink,
            rounded_corners=rounded_corners,
            corner_radius=corner_radius,
            qr_size=qr_size,
            colorful=colorful,
        )

        # Convert to base64 for API response
        buf = BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        qr_b64 = base64.b64encode(buf.getvalue()).decode('ascii')

        return jsonify({
            'success': True,
            'qr_image': f"data:image/png;base64,{qr_b64}",
            'shortlink': shortlink,
            'full_url': full_url
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
