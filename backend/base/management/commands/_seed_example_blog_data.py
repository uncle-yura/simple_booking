import os
import shutil

from django.conf import settings
from base.services import save_random_avatar_image
from base.services import get_lorem_ipsum
from base.services import get_example_assets_folder
from blog.models import Article, Tag, SocialShare


class ExampleBlogData:
    share_links = (
        "https://www.facebook.com/sharer/sharer.php?u=",
        "https://twitter.com/intent/tweet",
    )
    article_images = ("building.jpg", "work.jpg", "result.jpg")

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def create_social_share(self):
        for index, value in enumerate(("Facebook", "Twitter")):
            share, created = SocialShare.objects.get_or_create(id=index)
            if created:
                share.share_name = value
                share.share_icon = f"fab fa-{value.lower()}"
                share.share_text = f"with {value}"
                share.share_url = self.share_links[index]
                share.save()

    def create_tags(self):
        for index, value in enumerate(("Blog Tag 1", "Blog Tag 2")):
            tag, created = Tag.objects.get_or_create(id=index)
            if created:
                tag.tag_name = value
                tag.tag_slug = f"{value.lower().replace(' ', '_')}"
                tag.save()

    def create_articles(self):
        for index in range(10):
            article, created = Article.objects.get_or_create(id=index)
            if created:
                article.article_title = f"Test title {index}"
                save_random_avatar_image(os.path.join(settings.MEDIA_ROOT, f"blog-{index}.png"))
                article.article_image = f"blog-{index}.png"
                article.article_content = get_lorem_ipsum()
                if index < 5:
                    article.article_tags.set((1,))
                article.article_top_posts = False
                article.article_slug += f"{index}"
                article.save()

        for index, value in enumerate(("Our office", "Our work", "Our result")):
            article, created = Article.objects.get_or_create(id=index + 10)
            if created:
                article.article_title = value
                shutil.copyfile(
                    os.path.join(
                        get_example_assets_folder(),
                        self.article_images[index],
                    ),
                    os.path.join(settings.MEDIA_ROOT, self.article_images[index]),
                )
                article.article_image = self.article_images[index]
                article.article_content = get_lorem_ipsum()
                article.article_tags.set((0,))
                article.article_top_posts = True
                article.article_slug += f"{index}"
                article.save()

    def create_data(self):
        self.create_tags()
        self.create_social_share()
        self.create_articles()
