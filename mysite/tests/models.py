from django.conf import settings
from django.db import models

class Test(models.Model):
    TYPE_CHOICES = (
        ('a', 'Тести на тип особистості'),
        ('b', 'Тести на тип привязуваності'),
        ('c', 'Тести на профорієнтацію'),
        ('d', 'Тести на стрес та тривожність'),
        ('e', 'Тести на емоційний розум'),
        ('f', 'Тести на когнітивні вміння'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField(default='No description provided')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='other')

    def __str__(self):
        return self.name

class Question(models.Model):
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    value = models.IntegerField()

    def __str__(self):
        return self.text

class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='test_results', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    total_score = models.IntegerField()


    def __str__(self):
        return f"{self.user.email}'s score on {self.test.name}: {self.total_score}"

class UserTest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_tests', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='completed_tests', on_delete=models.CASCADE)
    result = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email}'s result on {self.test.name} is {self.result}"
