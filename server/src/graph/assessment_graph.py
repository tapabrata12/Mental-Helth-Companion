"""
#####################################################################################################
Importing the necessary modules
#####################################################################################################
"""
from langgraph.graph import START,END,StateGraph # Build the Graph
from typing import List,Optional,Any,TypedDict,Literal  # To define Graph Schema
from src.schemas.assessment import PHQ9AssessmentRequest
from src.services.crisis_service import build_crisis_support
from src.services.assessment_service import score_phq9_assessment
from src.services.crisis_service import check_for_crisis
"""
#####################################################################################################
This is a simple lookup table. The frontend will show info from this tool dicts
#####################################################################################################
"""
PHQ9_SCORE_OPTIONS:dict[int,str] = {
    0: "Not at all",
    1: "Several Days",
    2: "More that half days",
    3: "Nearly everyday"
}

PHQ9_QUESTIONS: dict[int,str] = {
    1: "Little interest or pleasure in doing things",  # Store PHQ-9 question 1.
    2: "Feeling down, depressed, or hopeless",  # Store PHQ-9 question 2.
    3: "Trouble falling or staying asleep, or sleeping too much",  # Store PHQ-9 question 3.
    4: "Feeling tired or having little energy",  # Store PHQ-9 question 4.
    5: "Poor appetite or overeating",  # Store PHQ-9 question 5.
    6: "Feeling bad about yourself, or that you are a failure",  # Store PHQ-9 question 6.
    7: "Trouble concentrating on things",  # Store PHQ-9 question 7.
    8: "Moving or speaking slowly, or being unusually restless",  # Store PHQ-9 question 8.
    9: "Thoughts that you would be better off dead, or of hurting yourself",  # Store PHQ-9 question 9.
}

"""
#####################################################################################################
LangGraph uses this class as the shared memory that flows through every node. 
Every node receives a copy of this state, makes changes, and returns the changed parts.
#####################################################################################################
"""

class PHQ9ConversationState(TypedDict, total=False):
    answers: list[dict[str,int]]
    assistant_message: str
    score_options: dict[int, str]
    notes: str
    is_complete: bool
    needs_answer: bool
    result: str
    current_question_id: int
    incoming_score: Optional[int]
    result: Optional[dict[str, Any]]
    crisis_support: Optional[dict[str, Any]]
    Error: Optional[str | None]

"""
#####################################################################################################
Helper Methods for the graph schema
#####################################################################################################
"""

def _increase_question_id(answers: Optional[List[dict[int,int]]]) -> int:
    return len(answers) + 1

def _build_question_message(question_id: int)-> str:
    question = PHQ9_QUESTIONS[question_id]
    return f"Over the last 2 weeks, how often have you been bothered by: {question}?"

"""
#####################################################################################################
Nodes for the Graph schema
#####################################################################################################
"""

def record_answer(state: PHQ9ConversationState) -> PHQ9ConversationState:
    """
    :param state:
    :return: state
    :work: Its only job is to look at the raw number the user just clicked (e.g., 2),
    make sure it is a valid choice (0, 1, 2, or 3),
    and save it permanently to the answers list on our clipboard.
    """
    # Step 1: get the answer list from the schema
    answers = state.get("answers", []) # if answer is empty then send the [] list in the `answer` variable
    
    incoming_score = state.get("incoming_score")
    # Check the score given from the user if it is not given by the user then return the same answer
    if incoming_score is None:
        return {"answers": answers, "Error": None}

    # If the given number is not from the Options then return the unedited answer with the error
    if incoming_score not in PHQ9_SCORE_OPTIONS:
        return {"answers": answers, "Error": "Please answer with 0, 1, 2, or 3."}

    # before adding new question id and option check if it is full or not
    if len(answers) >= 9:
        return {"answers": answers, "Error": None}

    # Increase the ID as it starts from 1
    question_id = _increase_question_id(answers)

    # Append the new list
    answers.append({"question_id": question_id, "score": incoming_score})
    return {"answers": answers, "Error": None}

def check_crisis(state: PHQ9ConversationState) -> PHQ9ConversationState:

    notes = state.get("notes")

    if notes is not None:
        crisis_result = check_for_crisis(notes.lower())

        if crisis_result.crisis_detected:
            crisis : dict[str, Any] = build_crisis_support(crisis_result.crisis_detected)
            return {"crisis_support": crisis,"is_complete": True, "needs_answer": False}

    return state

"""
_____________________________________________________________________________________________________
This is not a node this is a conditional function which deside in which node the control goes next
_____________________________________________________________________________________________________
"""
def route_after_answer(state: PHQ9ConversationState)-> Literal["score_assessment", "ask_question"]:
    answers = state.get("answers", [])
    if len(answers) >= 9:
        return "score_assessment"

    return "ask_question"

def ask_question(state: PHQ9ConversationState)-> PHQ9ConversationState:
    answers = state.get('answers', [])
    question_id = _increase_question_id(answers)
    message = _build_question_message(question_id)

    return {
        "current_question_id": question_id,
        "assistant_message": message,
        "score_options": PHQ9_SCORE_OPTIONS,
        "is_complete": False,
        "needs_answer": True,
        "result": None,
        "crisis_support": None,
    }


async def score_assessment(state: PHQ9ConversationState)-> PHQ9ConversationState:
    answers = state.get('answers')
    notes = state.get('notes')
    request = PHQ9AssessmentRequest(
        answers=answers,
        notes=notes
    )
    result = await score_phq9_assessment(request)
    result_data = result.model_dump()

    return {
        "answers": answers,
        "assistant_message": "PHQ-9 assessment complete.",
        "score_options": PHQ9_SCORE_OPTIONS,
        "is_complete": True,
        "needs_answer": False,
        "result": result_data,
        "crisis_support": result_data.get("crisis_support"),
        "Error": None,
    }

def build_phq9_conversation_graph():
    builder = StateGraph(PHQ9ConversationState)

    builder.add_node("record_answer", record_answer)
    builder.add_node("ask_question", ask_question)
    builder.add_node("score_assessment", score_assessment)

    builder.add_edge(START, "record_answer")
    builder.add_conditional_edges("record_answer", route_after_answer)
    builder.add_edge("ask_question", END)
    builder.add_edge("score_assessment", END)

    return builder.compile()

graph = build_phq9_conversation_graph()


"""
#####################################################################################################
START the Graph for conversation
#####################################################################################################
"""

async def start_conversation(notes: Optional[str])-> PHQ9ConversationState:
    return await graph.ainvoke({"answers": [], "incoming_score": None ,"notes": notes})


"""
#####################################################################################################
CONTINUE the Graph for conversation
#####################################################################################################
"""

async def continue_conversation(answers: list[dict[str,int]], notes: Optional[str], incoming_score: int)-> PHQ9ConversationState:
    return await graph.ainvoke({"answers": answers, "incoming_score": incoming_score, "notes": notes})