from django.core.mail import send_mass_mail
from .models import Post, Category
from django.utils import timezone
from datetime import timedelta

def weekly_digest():
    week_ago = timezone.now() - timedelta(weeks=1)

    categories = Category.objects.prefetch_related('subscribers')
    new_posts = Post.objects.filter(add_time__gt=week_ago).select_related('category')

    for category in categories:
        category_new_posts = new_posts.filter(category=category)
        if category_new_posts:
            messages = []
            for subscriber in category.subscribers.all():
                message = (
                    "Weekly digest",
                    f"News posts in {category.category_title}:\n" +
                    "\n".join([f"{post.title}: {post.get_absolute_url()}" for post in category_new_posts]),
                    'spartak_pvl@mail.ru',
                    [subscriber.email],
                )
                messages.append(message)

            send_mass_mail(messages)
