import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from flask_migrate import Migrate
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_query(request, items):
    # pagination variables
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    # format items
    format_items = [item.format() for item in items]

    return [format_items[start:end], page]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    migrate = Migrate(app, db)

    # '''
    # CORS allowing '*' for origins.
    # '''
    CORS(app, resources={r"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        '''
        Use the after_request decorator to set Access-Control-Allow
        '''
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def get_categories():
        '''
        Create an endpoint to handle GET requests 
        for all available categories.
        '''
        try:
            category_obj = Category.query.order_by('id').all()
            categories = {cat.id: cat.type for cat in category_obj}
            return jsonify({
                "categories": categories
            })
        except:
            abort(400)

    @app.route('/questions')
    def get_questions():
        # '''
        # Create an endpoint to handle GET requests for questions,
        # including pagination (every 10 questions).
        # This endpoint should return a list of questions,
        # number of total questions, current category, categories.

        # TEST: At this point, when you start the application
        # you should see questions and categories generated,
        # ten questions per page and pagination at the bottom of the screen
        # for three pages.
        # Clicking on the page numbers should update the questions.
        # '''
        try:
            # categories
            cats = Category.query.order_by('id').all()
            categories = {cat.id: cat.type for cat in cats}

            # current_category
            category = request.args.get('category', 7, type=int)
            find_category = Category.query.filter(Category.id == category).one_or_none()
            if find_category:
                current_category = find_category.type
                # questions
                ques = Question.query.filter(Question.category == category).order_by('id').all()
            else:
                current_category = 'all'  # 7 is 'all' category not implemented
                ques = Question.query.order_by('id').all()

            pagQ = paginate_query(request, ques)
            return jsonify({
                "categories": categories,
                "total_questions": len(pagQ[0]),
                "questions": pagQ[0],
                "currentCategory": current_category,
            })
        except:
            print(sys.exc_info())
            abort(404)

    @app.route('/questions/<int:ques_id>', methods=['DELETE'])
    def delete_question(ques_id):
        # '''
        # @TODO:
        # Create an endpoint to DELETE question using a question ID.

        # TEST: When you click the trash icon next to a question, the question will be removed.
        # This removal will persist in the database and when you refresh the page.
        # '''
        # print("ques_id",ques_id)
        error = False
        try:
            ques = Question.query.filter(Question.id == ques_id).one_or_none()
            ques.delete()
        except:
            error = True
            print(sys.exc_info())
        
        if error:
            abort(404)
        else:
            return jsonify({
                "success": True,
                "id": ques_id
            })


        

    # '''
    # @TODO:
    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.

    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last page
    # of the questions list in the "List" tab.
    # '''

    # '''
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # '''

    # '''
    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.
    # '''

    # '''
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # '''

    # '''
    # @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422.
    # '''

    return app
