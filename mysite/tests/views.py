from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse

from .models import Test, TestResult, Question, Answer


def test_list(request):
    tests = Test.objects.all()
    return render(request, 'tests/test_list.html', {'tests': tests})

def test_detail(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    questions = Question.objects.filter(test=test)
    return render(request, 'tests/test_detail.html', {'test': test, 'questions': questions})

def test_result(request, test_id):
    test_result = TestResult.objects.filter(test_id=test_id, user=request.user).first()
    return render(request, 'tests/test_result.html', {'result': test_result})


@login_required
def submit_answers(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    if request.method == 'POST':
        total_score = 0
        questions = Question.objects.filter(test=test)

        # Обробка відповідей користувача
        for question in questions:
            try:
                selected_answer_id = request.POST['question_' + str(question.id)]
                selected_answer = Answer.objects.get(id=selected_answer_id)
                total_score += selected_answer.value
            except (KeyError, Answer.DoesNotExist):
                # Якщо користувач не вибрав відповідь на якесь питання, можна встановити помилку
                messages.error(request, f'You did not select an answer for {question.text}')
                return redirect('test_detail', test_id=test_id)

        # Збереження результату тесту
        result, created = TestResult.objects.update_or_create(
            user=request.user,
            test=test,
            defaults={'total_score': total_score}
        )

        # Перенаправлення на сторінку з результатами
        return HttpResponseRedirect(reverse('tests:test_result', args=[result.id]))
    else:
        return HttpResponseRedirect(reverse('tests:test_detail', args=[test_id]))