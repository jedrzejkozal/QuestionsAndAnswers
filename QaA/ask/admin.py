from django.contrib import admin
from .models import *

admin.site.register(UserModel)
admin.site.register(FriendsModel)
admin.site.register(AnswerModel)
admin.site.register(QuestionModel)
