import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localtime


def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1] #获取文件扩展名
    filename = f'{uuid.uuid4().hex[:10]}.{ext}' #生成一个随机的文件名，保留扩展名
    return f'user/photos/{instance.user_id}_{filename}' #返回上传路径

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #一一对应的数据库表
    photo = models.ImageField(default='user/photos/default.png', upload_to=photo_upload_to) #用户头像，默认图片为default.png，上传路径为profile_pics
    profile = models.TextField(default='谢谢你的关注！', max_length=500) #用户简介，默认为“谢谢你的关注！”
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.user.username} - {localtime(self.create_time).strftime("%Y-%m-%d %H:%M:%S")}' #返回用户名和创建时间的字符串表示


