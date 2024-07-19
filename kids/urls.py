from django.urls import path
from . import views

urlpatterns = [
    path('', views.KidProfileList.as_view(), name='kid-profile-list'),
    path('<slug:slug>/', views.KidProfileDetail.as_view(), name='kid-profile-detail'),
    path('<slug:slug>/quests', views.KidsQuestList.as_view(), name='kids-quest-list'),
    path('<slug:slug>/quests/<quest_key>', views.KidsQuestDetail.as_view(), name='kids-quest-detail'),
    path('<slug:slug>/earns', views.KidsEarnsList.as_view(), name='kids-earns-list'),
    path('<slug:slug>/earns/<int:pk>', views.KidsEarnsDetail.as_view(), name='kids-earns-detail'),
    path('<slug:slug>/expenses', views.KidsExpensesList.as_view(), name='kids-expenses-list'),
    path('<slug:slug>/expenses/<int:pk>', views.KidsExpensesDetail.as_view(), name='kids-expenses-detail'),
    path('<slug:slug>/buttons', views.KidsButtonsDetail.as_view(), name='kids-buttons-detail'),
]
