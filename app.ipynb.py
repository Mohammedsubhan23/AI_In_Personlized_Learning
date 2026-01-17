import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.user_profile import UserProfile
from src.models.quiz_content import Quiz, DifficultyLevel
from src.ai.adaptation_engine import AdaptationEngine
from src.ai.content_recommender import ContentRecommender
from src.data.content_database import ContentDatabase
from src.utils.data_generator import DataGenerator

st.set_page_config(
    page_title="AI Personalized Learning System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI-Powered Personalized Learning System")

st.markdown("""
This system adapts educational content to individual learners based on their performance, 
learning style, and progress. Experience personalized learning with real-time adaptation!
""")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Take Quiz", "Analytics", "About"])

if page == "Dashboard":
    st.header("📊 Learning Dashboard")
    
    st.subheader("Student Profile")
    
    user_id = st.text_input("Enter Student ID", value="student_1")
    
    if st.button("Load Profile"):
        with st.spinner("Loading profile..."):
            user_profile = DataGenerator.create_user_profile(
                user_id=user_id,
                name="Demo Student",
                grade_level=10,
                learning_style="visual",
                difficulty_preference="intermediate"
            )
            
            st.session_state['user_profile'] = user_profile
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Accuracy", f"{user_profile.overall_accuracy:.1%}")
                st.metric("Engagement Score", f"{user_profile.engagement_score:.1%}")
            
            with col2:
                st.metric("Avg Response Time", f"{user_profile.avg_response_time:.1f}s")
                st.metric("Learning Style", user_profile.learning_style.title())
            
            with col3:
                st.metric("Preferred Difficulty", user_profile.preferred_difficulty.title())
                st.metric("Quizzes Completed", user_profile.total_quizzes_completed)
            
            st.subheader("Personalized Recommendations")
            
            content_db = ContentDatabase()
            recommender = ContentRecommender()
            
            available_quizzes = content_db.get_all_quizzes()
            recommendations = recommender.recommend_quiz(user_profile, available_quizzes, top_n=3)
            
            for quiz, score in recommendations:
                with st.expander(f"📝 {quiz.title} - Match Score: {score:.1%}"):
                    st.write(f"**Subject:** {quiz.subject.title()}")
                    st.write(f"**Topic:** {quiz.topic.title()}")
                    st.write(f"**Difficulty:** {quiz.difficulty.value.title()}")
                    st.write(f"**Questions:** {len(quiz.questions)}")
                    st.write(f"**Estimated Time:** {quiz.estimated_time} minutes")

elif page == "Take Quiz":
    st.header("📝 Interactive Quiz")
    
    if 'user_profile' not in st.session_state:
        st.warning("Please load your profile from the Dashboard first!")
    else:
        user_profile = st.session_state['user_profile']
        
        content_db = ContentDatabase()
        adaptation_engine = AdaptationEngine()
        
        available_quizzes = content_db.get_all_quizzes()
        
        if not available_quizzes:
            st.warning("No quizzes available at the moment.")
        else:
            selected_quiz = st.selectbox(
                "Select a Quiz",
                options=available_quizzes,
                format_func=lambda x: f"{x.title} ({x.difficulty.value})"
            )
            
            if st.button("Start Quiz"):
                st.session_state['current_quiz'] = selected_quiz
                st.session_state['question_index'] = 0
                st.session_state['answers'] = {}
                st.session_state['start_time'] = None
            
            if 'current_quiz' in st.session_state:
                quiz = st.session_state['current_quiz']
                q_index = st.session_state.get('question_index', 0)
                
                if q_index < len(quiz.questions):
                    question = quiz.questions[q_index]
                    
                    st.subheader(f"Question {q_index + 1} of {len(quiz.questions)}")
                    st.write(f"**{question.content}**")
                    
                    if question.options:
                        answer = st.radio("Select your answer:", question.options)
                    else:
                        answer = st.text_input("Your answer:")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Submit Answer"):
                            if 'start_time' not in st.session_state:
                                st.session_state['start_time'] = q_index
                            
                            is_correct = answer == question.correct_answer
                            st.session_state['answers'][q_index] = {
                                'answer': answer,
                                'is_correct': is_correct,
                                'question_id': question.question_id
                            }
                            
                            if is_correct:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Incorrect")
                            
                            feedback = adaptation_engine.generate_personalized_feedback(
                                user_profile, question, is_correct, 30.0
                            )
                            st.info(feedback)
                            
                            if st.button("Next Question"):
                                st.session_state['question_index'] = q_index + 1
                                st.rerun()
                    
                    with col2:
                        if st.button("Show Hint"):
                            if question.hints:
                                st.warning(f"💡 Hint: {question.hints[0]}")
                            else:
                                st.info("No hints available for this question.")
                
                else:
                    st.success("🎉 Quiz Completed!")
                    
                    answers = st.session_state.get('answers', {})
                    total_questions = len(quiz.questions)
                    correct_count = sum(1 for a in answers.values() if a['is_correct'])
                    accuracy = correct_count / total_questions if total_questions > 0 else 0
                    
                    st.metric("Accuracy", f"{accuracy:.1%}")
                    st.metric("Correct Answers", f"{correct_count}/{total_questions}")
                    
                    if st.button("Return to Dashboard"):
                        del st.session_state['current_quiz']
                        del st.session_state['question_index']
                        st.rerun()

elif page == "Analytics":
    st.header("📈 Learning Analytics")
    
    st.subheader("Performance Over Time")
    
    st.info("📊 Analytics dashboard showing learning progress, performance trends, and adaptation patterns.")
    
    st.write("""
    This section would include:
    - Performance charts and graphs
    - Learning progress visualization
    - Difficulty adaptation history
    - Topic mastery tracking
    - Engagement metrics
    """)

elif page == "About":
    st.header("ℹ️ About This System")
    
    st.markdown("""
    ## AI Personalized Learning System
    
    This is a demonstration of an AI-powered adaptive learning platform that personalizes 
    educational content based on individual learner characteristics and performance.
    
    ### Key Features:
    
    1. **Adaptive Content Delivery**: Automatically adjusts difficulty and content based on learner performance
    2. **Learner Profiling**: Tracks learning styles, pace, and preferences
    3. **Real-time Feedback**: Provides personalized hints and explanations
    4. **Smart Recommendations**: Suggests optimal learning paths based on performance data
    5. **Performance Analytics**: Monitors progress and identifies areas needing support
    
    ### AI Techniques Used:
    
    - **Adaptive Learning Algorithms**: Dynamic content selection based on performance metrics
    - **Learning Pattern Recognition**: Identifies learner behaviors and preferences
    - **Content-based Filtering**: Recommends content matching learner profiles
    - **Performance Prediction**: Anticipates learner needs and challenges
    
    ### Built With:
    - Python & Streamlit for the web interface
    - Custom AI adaptation engine
    - Personalized recommendation system
    - Real-time feedback generation
    """)
    
    st.markdown("---")
    st.markdown("**Developed as part of AI in Personalized Learning Project**")

st.sidebar.markdown("---")
st.sidebar.info("🎯 This is a demonstration prototype showcasing AI-powered personalized learning concepts.")