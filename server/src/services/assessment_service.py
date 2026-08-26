# File: server/src/services/assessment_service.py
from fastapi import HTTPException,status
from src.core.config import settings
from src.db import mongodb
from src.schemas.assessment import PHQ9Severity,PHQ9AssessmentHistoryItem,PHQ9AssessmentRequest,PHQ9AssessmentResult,PHQ9AssessmentResponse,PHQ9AssessmentState
from src.models.assessment import create_phq9_assessment_document
from src.services.crisis_service import build_crisis_support
from typing import Tuple,List
from datetime import datetime

"""
#####################################################################################################
This part is the calculation part where we try to calculate every field about PHQ-9 assessment
#####################################################################################################
"""

def _determine_phq9_severity(total_score: int) -> PHQ9Severity:  # Create helper that maps PHQ-9 total score to standard severity band
    """
        :param total_score: int
        :return String: PHQ9Severity
        :Workings: It takes the total PHQ-9 score and returns message according to that score
        """
    if 0 <= total_score <= 4:  # Check minimal depression score range
        return "minimal"  # Return minimal severity label
    if 5 <= total_score <= 9:  # Check mild depression score range
        return "mild"  # Return mild severity label
    if 10 <= total_score <= 14:  # Check moderate depression score range
        return "moderate"  # Return moderate severity label
    if 15 <= total_score <= 19:  # Check moderately severe depression score range
        return "moderately_severe"  # Return moderately severe label
    return "severe"  # Return severe label for scores 20 through 27

def _evaluate_follow_up_flags(question:PHQ9AssessmentRequest, total_score:int) -> Tuple[bool,bool]:  # Create helper that computes follow-up and crisis flags from request answers
    """
    :param question:
    :param total_score:
    :return Tuple[bool,bool]:
    Working: It basically takes the list of dictionary and extract the 9th dictionary question score
            If score is greater than 0 then one value of Tuple should be true Tuple[??,True]
            After that we check the total score if score is greater than 10 then Tuple[True,True]
    """
    question_9_answer = next((value.score for value in question.answers if value.question_id == 9)) # Read score from PHQ-9 item 9 or default to zero if missing unexpectedly
    crisis_detection_flag = question_9_answer > 0 # Mark crisis flag true when self-harm item is not answered as "not at all"
    follow_up = total_score >= 10 or crisis_detection_flag # Mark follow-up true for moderate-or-higher total score or any crisis signal
    return follow_up,crisis_detection_flag # Return both derived flags together

def _build_recommendation_message(severity:PHQ9Severity, crisis_detection_flag:bool, follow_up: bool,) -> str:
    """
    :param severity:
    :param crisis_detection_flag:
    :param follow_up:
    :return:
    """
    if crisis_detection_flag:
        return "Your responses suggest possible immediate safety concerns. Please contact local emergency services or a crisis helpline now, and share this screening with a trusted clinician."  # Return safety-first recommendation message

    if follow_up:  # Handle non-crisis but clinically meaningful follow-up path
        return f"Your PHQ-9 result falls in the {severity.replace('_', ' ')} range. Please schedule a professional mental health follow-up and continue regular check-ins."  # Return structured clinical follow-up recommendation
    return "Your responses are currently in a lower-severity range. Keep practicing daily self-care and repeat this check-in if symptoms increase."  # Return lower-risk self-monitoring recommendation



async def score_phq9_assessment(request_data:PHQ9AssessmentRequest)-> PHQ9AssessmentResult:
    total_score = sum(x.score for x in request_data.answers)
    severity = _determine_phq9_severity(total_score=total_score)
    needs_follow,crisis_detection_flag = _evaluate_follow_up_flags(request_data,total_score)
    recommendation = _build_recommendation_message(severity,crisis_detection_flag,needs_follow)
    crisis_support = build_crisis_support(crisis_detection_flag)
    return PHQ9AssessmentResult(
        total_score=total_score,
        severity=severity,
        needs_to_follow=needs_follow,
        clinical_risk=crisis_detection_flag,
        recommendation=recommendation,
        crisis_support=crisis_support
    )

async def run_phq9_assessment(request_data: PHQ9AssessmentRequest)-> PHQ9AssessmentResponse:
    result = await score_phq9_assessment(request_data)
    return PHQ9AssessmentResponse(result=result)

async def build_phq9_graph_state(request_data:PHQ9AssessmentRequest) -> PHQ9AssessmentState:
    result = await score_phq9_assessment(request_data=request_data)
    return PHQ9AssessmentState(
        request=request_data,
        total_score=result.total_score,
        severity=result.severity,
        needs_to_follow=result.needs_to_follow,
        clinical_risk=result.clinical_risk,
        recommendation=result.recommendation,
        crisis_support=result.crisis_support
    )


"""
#####################################################################################################
This part is where we try to save every field about PHQ-9 assessment into MONGODB
#####################################################################################################
"""

async def run_phq9_assessment_and_save(user_id:str,request:PHQ9AssessmentRequest)-> PHQ9AssessmentResponse:


    if not isinstance(user_id,str) or not user_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User id is invalid or empty")

    result = await score_phq9_assessment(request_data=request)
    mongodb_model = create_phq9_assessment_document(user_id=user_id,request=request,result=result)
    if mongodb.db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Database connection is not initialized")  # Raise explicit 500 when DB is unavailable.

    insert_result = await mongodb.db[settings.ASSESSMENT_COLLECTION_NAME].insert_one(mongodb_model)
    if not insert_result.inserted_id:  # Validate insert acknowledgment includes inserted document id.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to save assessment")  # Raise explicit 500 when insert is not acknowledged correctly.

    return PHQ9AssessmentResponse(result=result)

"""
#####################################################################################################
This part is where we try fetch all the calculated history from the DataBase
#####################################################################################################
"""
async def get_phq9_history(
    user_id: str,
    limit: int = 20,
    skip: int = 0
) -> List[PHQ9AssessmentHistoryItem]:
    from src.core.config import settings
    from src.db import mongodb

    # Validate user_id
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User id is invalid or empty"
        )

    # Validate limit
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )

    # Validate skip
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip must be 0 or greater"
        )

    # Check DB connection
    if mongodb.db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection is not initialized"
        )

    # Build query
    query = {
        "user_id": user_id,
        "assessment_type": "phq9"
    }

    # Fetch documents
    documents = await (
        mongodb.db[settings.ASSESSMENT_COLLECTION_NAME]
        .find(query)
        .sort("document_created", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )

    # Transform documents into API-safe response
    history_items: List[PHQ9AssessmentHistoryItem] = []

    for doc in documents:

        created_at = doc.get("document_created")  # Read creation timestamp from the saved MongoDB document.

        history_items.append(PHQ9AssessmentHistoryItem(
            assessment_id=str(doc.get("_id")),
            assessment_type=doc.get("assessment_type", "phq9"),
            total_score=doc.get("total_score"),
            severity=doc.get("severity"),
            needs_to_follow=doc.get("needs_to_follow"),
            clinical_risk=doc.get("clinical_risk"),
            recommendation=doc.get("recommendation"),
            notes=doc.get("notes"),
            crisis_support=doc.get("crisis_support"),
            created_at=(
                datetime.fromisoformat(created_at)
                if isinstance(created_at, str)  # Convert stored ISO string timestamps into datetime objects for Pydantic serialization.
                else created_at  # Keep datetime or None values unchanged when MongoDB already returned them in that shape.
            )
        ))

    return history_items
