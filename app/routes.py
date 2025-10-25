from flask import Blueprint, render_template, request, send_file, flash, jsonify
from io import BytesIO
import base64
from app.utils.social_qr import (
    generate_facebook_qr,
    generate_instagram_qr,
    generate_linkedin_qr,
    SocialQRGenerator
)

bp = Blueprint('main', __name__)
qr_generator = SocialQRGenerator()


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/social/facebook', methods=['GET', 'POST'])
def facebook_qr():
    if request.method == 'POST':
        try:
            profile_url = request.form.get('profile_url', '').strip()
            display_name = request.form.get('display_name', '').strip()
            use_shortlink = request.form.get('use_shortlink') == 'true'
            rounded_corners = request.form.get('rounded_corners') == 'true'
            corner_radius = int(request.form.get('corner_radius', 40))
            qr_size = int(request.form.get('qr_size', 300))

            if not profile_url or not display_name:
                flash('Моля, попълнете всички полета!', 'error')
                return render_template('social/facebook.html')

            qr_image, shortlink, full_url = generate_facebook_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )

            # Convert to base64 for preview
            img_io = BytesIO()
            qr_image.save(img_io, 'PNG', quality=95)
            img_io.seek(0)
            qr_base64 = base64.b64encode(img_io.getvalue()).decode()

            return render_template('social/facebook.html',
                                   qr_image=qr_base64,
                                   shortlink=shortlink,
                                   full_url=full_url,
                                   success=True)

        except Exception as e:
            flash(f'Грешка при генериране: {str(e)}', 'error')

    return render_template('social/facebook.html')


@bp.route('/social/instagram', methods=['GET', 'POST'])
def instagram_qr():
    if request.method == 'POST':
        try:
            profile_url = request.form.get('profile_url', '').strip()
            display_name = request.form.get('display_name', '').strip()
            use_shortlink = request.form.get('use_shortlink') == 'true'
            rounded_corners = request.form.get('rounded_corners') == 'true'
            corner_radius = int(request.form.get('corner_radius', 40))
            qr_size = int(request.form.get('qr_size', 300))

            if not profile_url or not display_name:
                flash('Моля, попълнете всички полета!', 'error')
                return render_template('social/instagram.html')

            qr_image, shortlink, full_url = generate_instagram_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )

            # Convert to base64 for preview
            img_io = BytesIO()
            qr_image.save(img_io, 'PNG', quality=95)
            img_io.seek(0)
            qr_base64 = base64.b64encode(img_io.getvalue()).decode()

            return render_template('social/instagram.html',
                                   qr_image=qr_base64,
                                   shortlink=shortlink,
                                   full_url=full_url,
                                   success=True)

        except Exception as e:
            flash(f'Грешка при генериране: {str(e)}', 'error')

    return render_template('social/instagram.html')


@bp.route('/social/linkedin', methods=['GET', 'POST'])
def linkedin_qr():
    if request.method == 'POST':
        try:
            profile_url = request.form.get('profile_url', '').strip()
            display_name = request.form.get('display_name', '').strip()
            use_shortlink = request.form.get('use_shortlink') == 'true'
            rounded_corners = request.form.get('rounded_corners') == 'true'
            corner_radius = int(request.form.get('corner_radius', 40))
            qr_size = int(request.form.get('qr_size', 300))

            if not profile_url or not display_name:
                flash('Моля, попълнете всички полета!', 'error')
                return render_template('social/linkedin.html')

            qr_image, shortlink, full_url = generate_linkedin_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )

            # Convert to base64 for preview
            img_io = BytesIO()
            qr_image.save(img_io, 'PNG', quality=95)
            img_io.seek(0)
            qr_base64 = base64.b64encode(img_io.getvalue()).decode()

            return render_template('social/linkedin.html',
                                   qr_image=qr_base64,
                                   shortlink=shortlink,
                                   full_url=full_url,
                                   success=True)

        except Exception as e:
            flash(f'Грешка при генериране: {str(e)}', 'error')

    return render_template('social/linkedin.html')


@bp.route('/download/<platform>', methods=['POST'])
def download_qr(platform):
    try:
        profile_url = request.form.get('profile_url')
        display_name = request.form.get('display_name')
        use_shortlink = request.form.get('use_shortlink') == 'true'
        rounded_corners = request.form.get('rounded_corners') == 'true'
        corner_radius = int(request.form.get('corner_radius', 40))
        qr_size = int(request.form.get('qr_size', 300))

        if platform == 'facebook':
            qr_image, shortlink, full_url = generate_facebook_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        elif platform == 'instagram':
            qr_image, shortlink, full_url = generate_instagram_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        elif platform == 'linkedin':
            qr_image, shortlink, full_url = generate_linkedin_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        else:
            return "Invalid platform", 400

        img_io = BytesIO()
        qr_image.save(img_io, 'PNG', quality=95)
        img_io.seek(0)

        filename = f"qr_{platform}_{display_name.replace(' ', '_')}.png"

        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return f"Error: {str(e)}", 500


@bp.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint for QR generation"""
    try:
        data = request.get_json()
        platform = data.get('platform')
        profile_url = data.get('profile_url')
        display_name = data.get('display_name')
        use_shortlink = data.get('use_shortlink', True)
        rounded_corners = data.get('rounded_corners', False)
        corner_radius = data.get('corner_radius', 40)
        qr_size = data.get('qr_size', 300)

        if platform == 'facebook':
            qr_image, shortlink, full_url = generate_facebook_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        elif platform == 'instagram':
            qr_image, shortlink, full_url = generate_instagram_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        elif platform == 'linkedin':
            qr_image, shortlink, full_url = generate_linkedin_qr(
                profile_url=profile_url,
                display_name=display_name,
                use_shortlink=use_shortlink,
                rounded_corners=rounded_corners,
                corner_radius=corner_radius,
                qr_size=qr_size
            )
        else:
            return jsonify({'error': 'Invalid platform'}), 400

        # Convert to base64
        img_io = BytesIO()
        qr_image.save(img_io, 'PNG')
        img_io.seek(0)
        qr_base64 = base64.b64encode(img_io.getvalue()).decode()

        return jsonify({
            'success': True,
            'qr_image': f"data:image/png;base64,{qr_base64}",
            'shortlink': shortlink,
            'full_url': full_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
