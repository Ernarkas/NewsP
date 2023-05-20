from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.core.mail import send_mass_mail
from .models import Post, Category
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import  timedelta
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance=None, created=False, **kwargs):
    if created:
        common_group = Group.objects.get_or_create(name='common')[0]
        instance.groups.add(common_group)



@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        categories = instance.category.all()
        for category in categories:
            for subscriber in category.subscribers.all():
                send_mail(
                    subject=f"Новая статья в категории {category.category_title}",
                    message=f"Проверьте новую статью: {instance.title}. {instance.content[:50]}... Прочитать статью можно по ссылке: {instance.get_absolute_url()}",
                    from_email='spartak_pvl@mail.ru',
                    recipient_list=[subscriber.email],
                    fail_silently=False,
                )

@receiver(pre_save, sender=Post)
def limit_posts_per_day(sender, instance, **kwargs):
    last_day_posts = Post.objects.filter(author=instance.author,
                                         add_time__gt=timezone.now()-timedelta(days=1))
    if instance.pk not in last_day_posts.values_list('id', flat=True) and last_day_posts.count() >=3:
        raise ValidationError("You can't post more than 3 posts per day!")
