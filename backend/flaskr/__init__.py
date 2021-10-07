import os
from flask import Flask, json, request, abort, jsonify
from sqlalchemy.sql.expression import select
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
            find_category = Category.query.filter(
                Category.id == category).one_or_none()
            if find_category:
                current_category = find_category.type
                # questions
                ques = Question.query.filter(
                    Question.category == category).order_by('id').all()
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

    @app.route('/question', methods=['POST'])
    def create_question():
        # '''
        # @TODO:
        # Create an endpoint to POST a new question,
        # which will require the question and answer text,
        # category, and difficulty score.

        # TEST: When you submit a question on the "Add" tab,
        # the form will clear and the question will appear at the end of the last page
        # of the questions list in the "List" tab.
        # '''
        body = request.get_json()
        pre_q = body.get('previous_questions')
        quiz_cat = body.get('quiz_category')
        if (quiz_cat['id'] == 0):
            ques = Question.query.all()
        else:
            ques = Question.query.filter_by(category=quiz_cat['id']).all()

        def q_random(item): return ques[random.randrange(0, len(item))]

        print("q_random >>>> ", q_random(ques).format())
        return jsonify({
            'question': q_random(ques).format()
        })

    # ------------------- INCOMPLETE ¬ -------------------------

    @app.route('/questions', methods=['POST'])
    def post_questions_handler():
        # '''
        # @TODO:
        # Create a POST endpoint to get questions based on a search term.
        # It should return any questions for whom the search term
        # is a substring of the question.

        # TEST: Search by any phrase. The questions list will update to include
        # only question that include that string within their question.
        # Try using the word "title" to start.
        # '''
        body = request.get_json()
        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')
            find_term = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            result = [item.format() for item in find_term]
            # for item in result:
            #     category = Category.query.filter_by(id=item['category']).one_or_none()
            #     item['category'] = category.type

            print("category >>>> ", result)
            return jsonify({
                'questions': result,
                'totalQuestions': len(result),
            })

        else:
            
            new_ques = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_cat = body.get('category')

            if ((new_ques is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_cat is None)):
                abort(422)

            try:
                question = Question(question=new_ques, answer=new_answer,
                                    difficulty=new_difficulty, category=new_cat)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_query(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                # abort unprocessable if exception
                abort(422)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        # '''
        # @TODO:
        # Create a GET endpoint to get questions based on category.

        # TEST: In the "List" tab / main screen, clicking on one of the
        # categories in the left column will cause only questions of that
        # category to be shown.
        # '''
        cat = Category.query.filter_by(id=id).one_or_none()

        if (cat is None):
            abort(400)

        selected = Question.query.filter_by(category=cat.id).all()

        paginate = paginate_query(request, selected)
        for item in paginate[0]:
            category = Category.query.filter_by(id=item['category']).one_or_none()
            item['category'] = category.type

        return jsonify({
            'success': True,
            'questions': paginate,
            'total_questions': len(Question.query.all())
        })

    @app.route('/')
    def random_questions():
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

        body = request.get_json()

        prev_q = body.get('previous_questions')

        cat = body.get('quiz_category')

        if ((cat is None) or (prev_q is None)):
            abort(400)

        if (cat['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=cat['id']).all()

        total = len(questions)

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        def check_if_used(question):
            used = False
            for q in prev_q:
                if (q == question.id):
                    used = True

            return used

        question = get_random_question()

        while (check_if_used(question)):
            question = get_random_question()

            if (len(prev_q) == total):
                return jsonify({
                    'success': True
                })
                
        return jsonify({
            'question': question.format()
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            "status": 404,
            "error": error,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success":False,
            "status":404,
            "error":error,
            "message":"Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success":False,
            "status":422,
            "error":error,
            "message":"Unprocessable"
        }), 422

        
    # '''
    # @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422.
    # '''

    return app
