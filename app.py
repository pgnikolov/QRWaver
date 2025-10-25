import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import qrcode
from PIL import Image, ImageDraw
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qrweaver-secret-key-2023'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


class QRWeaverGenerator:
    """Основен клас за генериране на QR кодове"""

    @staticmethod
    def create_qr(data, size=300, fill_color="#6A5ACD", back_color="#FFFFFF", style="modern"):
        """Създава QR код с различни стилове"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Прилагане на стилове
            if style == "modern":
                fill_color = "#6A5ACD"  # SlateBlue
                back_color = "#FFFFFF"
            elif style == "vibrant":
                fill_color = "#ED8936"  # Orange
                back_color = "#F7FAFC"
            elif style == "professional":
                fill_color = "#2D3748"  # Dark Gray
                back_color = "#FFFFFF"
            elif style == "creative":
                fill_color = "#48BB78"  # Emerald
                back_color = "#FFF5F5"

            qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)
            qr_img = qr_img.resize((size, size))

            return qr_img
        except Exception as e:
            raise Exception(f"Грешка при генериране на QR код: {str(e)}")


# Инициализация на генератора
qr_weaver = QRWeaverGenerator()


@app.route('/')
def index():
    """Начална страница"""
    return render_template('index.html',
                           title="QRWeaver - Weaving Digital Connections",
                           styles=["modern", "vibrant", "professional", "creative"])


@app.route('/generate', methods=['POST'])
def generate_qr():
    """Генериране на QR код"""
    try:
        # Вземане на данни от формата
        qr_data = request.form.get('qr_data', '').strip()
        qr_style = request.form.get('style', 'modern')
        qr_size = int(request.form.get('size', 300))

        # Валидация
        if not qr_data:
            flash('⚠️ Моля, въведете данни за QR кода!', 'error')
            return redirect(url_for('index'))

        if len(qr_data) > 1000:
            flash('⚠️ Данните са твърде дълги! Максимум 1000 символа.', 'error')
            return redirect(url_for('index'))

        # Генериране на QR код
        qr_image = qr_weaver.create_qr(
            data=qr_data,
            size=qr_size,
            style=qr_style
        )

        # Конвертиране към base64 за показване в браузъра
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Информация за генерирания QR код
        qr_info = {
            'data': qr_data[:100] + "..." if len(qr_data) > 100 else qr_data,
            'style': qr_style,
            'size': qr_size,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return render_template('index.html',
                               qr_image=qr_base64,
                               qr_info=qr_info,
                               styles=["modern", "vibrant", "professional", "creative"],
                               title="QR кодът е готов!")

    except Exception as e:
        flash(f'❌ Грешка при генериране: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/download', methods=['POST'])
def download_qr():
    """Изтегляне на QR кода като файл"""
    try:
        qr_data = request.form.get('download_data', '')
        qr_style = request.form.get('download_style', 'modern')
        qr_size = int(request.form.get('download_size', 300))

        if not qr_data:
            flash('⚠️ Няма данни за изтегляне!', 'error')
            return redirect(url_for('index'))

        # Генериране на QR код
        qr_image = qr_weaver.create_qr(
            data=qr_data,
            size=qr_size,
            style=qr_style
        )

        # Създаване на файл в паметта
        img_io = BytesIO()
        qr_image.save(img_io, 'PNG', quality=100)
        img_io.seek(0)

        # Генериране на име на файла
        filename = f"qrweaver_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        flash(f'❌ Грешка при изтегляне: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/about')
def about():
    """Страница за проекта"""
    return render_template('index.html',
                           about_page=True,
                           title="Относно QRWeaver",
                           styles=["modern", "vibrant", "professional", "creative"])


@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html',
                           error="Страницата не е намерена!",
                           title="404 - Страницата не е намерена"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html',
                           error="Вътрешна грешка в сървъра!",
                           title="500 - Грешка в сървъра"), 500


if __name__ == '__main__':
    # Създаване на необходимите папки
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    print("🚀 Стартиране на QRWeaver...")
    print("📍 Достъпен на: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)