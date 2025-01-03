from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """用户配置文件"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('手机号', max_length=20, blank=True)
    department = models.CharField('部门', max_length=50, blank=True)
    position = models.CharField('职位', max_length=50, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户配置文件'
        verbose_name_plural = '用户配置文件'
        db_table = 'muggle_user_profile'

    def __str__(self):
        return f"{self.user.username}的配置文件"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """当创建新用户时自动创建用户配置文件"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时同时保存用户配置文件"""
    instance.profile.save()
