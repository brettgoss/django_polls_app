# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Choice, Question

# Create your tests here.
def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text):
    """
    Creates a choice associated with the given `question` and `choice_text`.
    """
    return Choice.objects.create(question=question, choice_text=choice_text)

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class ChoiceMethodTests(TestCase):
    def test_choice_text_should_be_string(self):
        """
        Choice text should be a string regardless of input type.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question=question, choice_text=333)
        choice = Choice.objects.get(question=question.id)
        self.assertIs(isinstance(choice.choice_text, str), True)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question=question, choice_text="Choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        question = create_question(question_text="Future question.", days=30)
        create_choice(question=question, choice_text="Choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        future_question = create_question(question_text="Future question.", days=30)
        create_choice(question=past_question, choice_text="Past choice 1.")
        create_choice(question=future_question, choice_text="Future choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        first_past_question = create_question(question_text="Past question 1.", days=-30)
        second_past_question = create_question(question_text="Past question 2.", days=-5)
        create_choice(question=first_past_question, choice_text="Choice 1.")
        create_choice(question=second_past_question, choice_text="Choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_index_view_with_question_with_no_choices(self):
        """
        A question should not be displayed if it has no choices.
        """
        create_question(question_text="Past question with no choices.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_question_with_a_choice(self):
        """
        A question should be displayed if it has choices.
        """
        question = create_question(question_text="Past question with choices.", days=-5)
        create_choice(question=question, choice_text="Choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question with choices.>']
        )

class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionIndexResultsView(TestCase):
    def test_results_view_with_a_future_question(self):
        """
        The results view of a quesiton with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """
        The results view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
