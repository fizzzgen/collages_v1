import os
import re
import openai
import random
import pprint

from PIL import Image, ImageEnhance

openai.api_key = os.environ['OPENAI_TOKEN']

BACKGROUNDS_PATH = "backgrounds/"
GRAPHICS_PATH = "additional graphics/"
OBJECTS_PATH = "elements/"


class Tokens(object):
    BACKGROUND = "background"
    GRAPHICS = "graphics"
    OBJECTS = "objects"
    DELIMITER = "_"


def _is_image(name):
    return name.lower().endswith((".jpg", ".jpeg", ".png"))


def _tokenize_images(path, main_token):
        result = {}
        for root, _, files in os.walk(path):
            images = [f for f in files if _is_image(f)]
            for image in images:
                tokens = Tokens.DELIMITER.join([main_token] + [
                    token.lower()
                    for token in re.sub('[^0-9a-zA-Z]+', ' ', image.split(".")[0]).split()
                    if token
                ])
                result[os.path.join(root, image)] = tokens
        return result


def gpt_query(query):
    return openai.Completion.create(
        engine="text-davinci-003",
        prompt=query,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.6,
    ).choices[0]["text"].strip().lower()


class ImageSearch(object):
    def __init__(
        self,
        backgrounds_path=BACKGROUNDS_PATH,
        graphics_path=GRAPHICS_PATH,
        objects_path=OBJECTS_PATH,
    ):
        self.images_2_tokens = {}
        # TODO: add download from google drive

        self.images_2_tokens.update(_tokenize_images(backgrounds_path, Tokens.BACKGROUND))
        self.images_2_tokens.update(_tokenize_images(graphics_path, Tokens.GRAPHICS))
        self.images_2_tokens.update(_tokenize_images(objects_path, Tokens.OBJECTS))

    def search(
        self,
        query,
        background_count=1,
        graphics_count=6,
        objects_count=3,
    ):
        query = f"Please select {background_count} background, \
        {graphics_count} graphics, {objects_count} \
        objects for query '{query}' from this set: {self.images_2_tokens.values()}"
        query_result = gpt_query(query)

        result_images = [path for path in self.images_2_tokens.keys() if self.images_2_tokens[path] in query_result]

        result = {
            Tokens.BACKGROUND: [p for p in result_images if self.images_2_tokens[p].startswith(Tokens.BACKGROUND)],
            Tokens.GRAPHICS: [p for p in result_images if self.images_2_tokens[p].startswith(Tokens.GRAPHICS)],
            Tokens.OBJECTS: [p for p in result_images if self.images_2_tokens[p].startswith(Tokens.OBJECTS)],
        }
        for token in [Tokens.GRAPHICS, Tokens.OBJECTS]:
            random.shuffle(result[Tokens.GRAPHICS])

        return result


def create_collage(
    query,
    image_searcher,

    background_count=1,

    graphics_count=3,
    graphics_square_percentage=0.8,
    graphics_max_size_differ=3,

    objects_count=3,
    objects_square_percentage=0.5,
    objects_max_size_differ=3,

    size=(1000, 1000),
):

    def _get_sizes(count, square_percentage, max_size_differ):
        result = [
            int(random.randint(100, int(100 * max_size_differ)) / 100 / count * square_percentage * size[0])
            for i in range(count)
        ]
        result.sort()
        return result

    def _paste_images(collage, images, img_sizes, imgs_token):
        for i in range(min(len(images[imgs_token]), len(img_sizes))):
            img = Image.open(images[imgs_token][i])
            imgsize = (int(img_sizes[i]), int(img_sizes[i] * img.size[1] / img.size[0]))
            imgpos = (random.randint(0, size[0] - imgsize[0]), random.randint(0, size[1] - imgsize[1]))
            img = img.resize(imgsize)
            collage.paste(img, imgpos, mask=img)

    images = image_searcher.search(query, graphics_count=graphics_count*2, objects_count=objects_count)

    collage = Image.new("RGBA", size)
    collage.paste(Image.open(images[Tokens.BACKGROUND][0]).resize(size))

    graphics_sizes = _get_sizes(graphics_count, graphics_square_percentage, graphics_max_size_differ)
    objects_sizes = _get_sizes(objects_count, objects_square_percentage, objects_max_size_differ)

    _paste_images(collage, images, graphics_sizes, Tokens.GRAPHICS)
    _paste_images(collage, images, objects_sizes, Tokens.OBJECTS)

    return collage

if __name__ == "__main__":
    searcher = ImageSearch()
    collage = create_collage("heaven", searcher)
    collage.show()
