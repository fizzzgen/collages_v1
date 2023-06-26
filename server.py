from io import BytesIO

from flask import Flask
from flask import send_file
from flask import request
from flask import Flask

from collage import create_collage
from search import ImageSearch


_image_searcher = ImageSearch()
app = Flask(__name__)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/get_image')
def get_image():
    query = request.args.get('query')
    return serve_pil_image(create_collage(query, _image_searcher))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
