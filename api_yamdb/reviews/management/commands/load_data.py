from csv import DictReader

from django.core.management import BaseCommand
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)

MODEL = Category
DATA_FILE = 'category.csv'


class Command(BaseCommand):

    def handle(self, *args, **options):

        if MODEL.objects.exists():
            print('Данные уже загружены')
            return

        for row in DictReader(open(
                f'static/data/{DATA_FILE}', encoding='utf-8')
        ):
            if MODEL == Title:
                obj = Title(
                    id=row['id'], name=row['name'],
                    category_id=row['category'], year=row['year']
                )
            elif MODEL == Category:
                obj = Category(
                    id=row['id'], name=row['name'], slug=row['slug']
                )
            elif MODEL == User:
                obj = User(
                    id=row['id'], username=row['username'],
                    email=row['email'], role=row['role'],
                    bio=row['bio'], first_name=row['first_name'],
                    last_name=row['last_name'],
                )
            elif MODEL == Review:
                obj = Review(
                    id=row['id'], text=row['text'], score=row['score'],
                    author_id=row['author'], title_id=row['title_id'],
                    pub_date=row['pub_date']
                )
            elif MODEL == Genre:
                obj = Genre(id=row['id'], name=row['name'], slug=row['slug'])
            elif MODEL == Comment:
                obj = Comment(
                    id=row['id'], text=row['text'], review_id=row['review_id'],
                    author_id=row['author'], pub_date=row['pub_date']
                )
            elif MODEL == TitleGenre:
                obj = TitleGenre(
                    id=row['id'], title_id=row['title_id'],
                    genre_id=row['genre_id']
                )
            obj.save()
