# File: server/src/schemas/assessment.py  # Full file path comment as requested
from pydantic import BaseModel,model_validator,field_validator,ConfigDict,Field # Import Pydantic v2 tools for schema validation and configuration
from typing import Optional,Literal,List # Import typing helpers for strict literal values and optional fields
from datetime import datetime

PHQ9AnswerValue = Literal[0,1,2,3] # Define allowed PHQ-9 answer values where 0=not at all and 3=nearly every day
PHQ9QuestionID = Literal[1,2,3,4,5,6,7,8,9] # Define strict question identifiers for PHQ-9 questions one through nine
PHQ9Severity = Literal["minimal", "mild", "moderate", "moderately_severe", "severe"]  # Define standard PHQ-9 score interpretation bands


"""
#####################################################################################################
This part is where we make the crisis support part where we define the crisis center info
#####################################################################################################
"""

# I need this as it checks if the crisis detected by the hardcoded layer or not and if yes then what will be the matched phases.
class CrisisDetectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    crisis_detected: bool = Field(..., description="Whether any crisis phrase was found in the text")
    matched_phrases: list[str] = Field(default_factory=list, description="Phrases from the crisis list found in the text")

class CrisisResource(BaseModel):  # Define one crisis-support contact/resource returned by safety-aware responses
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # Reject unknown fields and normalize strings for API safety
    name: str = Field(..., min_length=1, description="Crisis support resource name")  # Store the public name of the helpline or emergency resource
    contact: str = Field(..., min_length=1, description="Phone number or emergency contact instruction")  # Store the phone number or contact instruction
    region: str = Field(..., min_length=1, description="Region where this crisis resource applies")  # Store the region so the frontend can label resources clearly

class PHQ9CrisisSupport(BaseModel):  # Define structured safety guidance returned when PHQ-9 item 9 signals risk
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # Reject unknown fields and normalize strings for stable output
    crisis_detected: bool = Field(default=True, description="Whether this response triggered crisis support")  # Tell clients that normal flow should be interrupted
    message: str = Field(..., min_length=1, description="Safety-first message to show immediately")  # Store the main safety message for the user
    resources: List[CrisisResource] = Field(default_factory=list, description="Crisis support resources to surface")  # Store one or more crisis resources for immediate display


class PHQ9QuestionAnswer(BaseModel):  # Define schema for a single PHQ-9 question answer item
    model_config = ConfigDict(extra="forbid",str_strip_whitespace=True)  # Reject unknown fields and strip whitespace from input strings
    question_id:PHQ9QuestionID = Field(..., description="PHQ-9 question number from 1 to 9")  # Require a valid PHQ-9 question identifier
    score: PHQ9AnswerValue = Field(...,description="PHQ-9 score value: 0, 1, 2, or 3")  # Require a valid PHQ-9 per-question score

class PHQ9AssessmentRequest(BaseModel): # Define schema for submitting a complete PHQ-9 screener response
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    answers:List[PHQ9QuestionAnswer] = Field(..., min_length=9, max_length=9, description="Exactly 9 PHQ-9 answers in a single submission") # Require exactly nine answers for a complete PHQ-9 run
    notes: Optional[str] = Field(None, min_length=1, max_length=1000, description="Optional short user note to store with this assessment") # Allow an optional note for additional context
    @field_validator('answers')
    @classmethod
    def validate_answer_length(cls, values:List[PHQ9QuestionAnswer])-> List[PHQ9QuestionAnswer]:
        question_ids = [value.question_id for value in values]
        if set(question_ids) != set(range(1, 10)): # Check that all nine question IDs are unique and present
            raise ValueError("answers must include each PHQ-9 question_id from 1 through 9 exactly once")  # Raise a clear validation error when duplicates or missing IDs exist
        return values  # Return the validated answers list unchanged when it passes checks

class PHQ9AssessmentResult(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    total_score: int = Field(..., ge=0, le=27, description="Total score for this PHQ-9 assessment")
    severity: PHQ9Severity = Field(..., description="Severity for this PHQ-9 assessment")
    needs_to_follow: bool = Field(..., description="Whether this PHQ-9 assessment needs to followup")
    clinical_risk: bool = Field(..., description="Whether this PHQ-9 assessment has a clinical risk")
    recommendation: str = Field(..., min_length=1, description="Recommendation for this PHQ-9 assessment")
    crisis_support: Optional[PHQ9CrisisSupport] = Field(default=None, description="Structured crisis resources when clinical_risk is true")

class PHQ9AssessmentResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    assessment_type: Literal["phq9"] = Field(default="phq9",description="Assessment type identifier")  # Mark this response as a PHQ-9 assessment result
    result: PHQ9AssessmentResult = Field(..., description="Results for this PHQ-9 assessment")

class PHQ9AssessmentState(BaseModel):  # Define normalized state shape used by the LangGraph PHQ-9 flow
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request:PHQ9AssessmentRequest = Field(..., description="Request for this PHQ-9 assessment")
    total_score: int = Field(..., ge=0, le=27, description="Total score for this PHQ-9 assessment")
    severity: PHQ9Severity = Field(..., description="Severity for this PHQ-9 assessment")
    needs_to_follow: bool = Field(..., description="Whether this PHQ-9 assessment needs to followup")
    clinical_risk: bool = Field(..., description="Whether this PHQ-9 assessment has a clinical risk")
    recommendation: str = Field(..., min_length=1, description="Recommendation for this PHQ-9 assessment")
    crisis_support: Optional[PHQ9CrisisSupport] = Field(default=None, description="Structured crisis resources when clinical_risk is true")
    @model_validator(mode='after')
    def calculate_sum(self)-> 'PHQ9AssessmentState':
        computed_total = sum(item.score for item in self.request.answers)
        if self.total_score != computed_total:
            raise ValueError("Total score for this PHQ-9 assessment must equal the sum of all answer scores")
        return self
"""
#####################################################################################################
This part is where we make the schema about the History of PHQ-9 assessment
#####################################################################################################
"""

class PHQ9AssessmentHistoryItem(BaseModel):  # Define one safe PHQ-9 history item returned to the frontend.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # Reject unknown output fields and normalize string whitespace.
    assessment_id: str = Field(..., min_length=1, description="MongoDB assessment document id converted to a string")  # Expose the MongoDB id safely as a plain string.
    assessment_type: Literal["phq9"] = Field(default="phq9", description="Assessment type identifier")  # Mark each history item as a PHQ-9 record.
    total_score: int = Field(..., ge=0, le=27, description="Total score for this saved PHQ-9 assessment")  # Return the saved PHQ-9 total score.
    severity: PHQ9Severity = Field(..., description="Saved severity band for this PHQ-9 assessment")  # Return the saved PHQ-9 severity label.
    needs_to_follow: bool = Field(..., description="Whether this saved PHQ-9 assessment needs professional follow-up")  # Return the saved follow-up flag.
    clinical_risk: bool = Field(..., description="Whether this saved PHQ-9 assessment triggered a clinical risk flag")  # Return the saved crisis or clinical-risk flag.
    recommendation: str = Field(..., min_length=1, description="Saved recommendation for this PHQ-9 assessment")  # Return the saved recommendation text.
    notes: Optional[str] = Field(default=None, description="Optional user note saved with this PHQ-9 assessment")  # Return the saved note when the user submitted one.
    crisis_support: Optional[PHQ9CrisisSupport] = Field(default=None, description="Saved crisis resources for this assessment when present")  # Return saved safety resources when the assessment triggered them.
    created_at: Optional[datetime] = Field(None, description="UTC creation timestamp for this saved PHQ-9 assessment")  # Return the saved creation timestamp when available.

class PHQ9AssessmentHistoryResponse(BaseModel):  # Define paginated PHQ-9 history response returned by the history endpoint.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # Reject unknown output fields and normalize string whitespace.
    assessment_type: Literal["phq9"] = Field(default="phq9", description="Assessment type identifier for this history response")  # Mark the full response as PHQ-9 history.
    count: int = Field(..., ge=0, description="Number of history items returned in this response")  # Tell the frontend how many items came back.
    limit: int = Field(..., ge=1, le=100, description="Maximum number of history items requested")  # Echo the requested page size.
    skip: int = Field(..., ge=0, description="Number of history items skipped before this page")  # Echo the requested pagination offset.
    items: List[PHQ9AssessmentHistoryItem] = Field(default_factory=list, description="Saved PHQ-9 assessment history items")  # Return the actual history items.

"""
#####################################################################################################
This part is where we make the schema about the PHQ9 Conversation Schema
#####################################################################################################
"""

class PHQ9ConversationStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    notes: Optional[str] = Field(default=None, min_length=1, max_length=1000, description="Optional note to attach to this conversation")

class PHQ9ConversationContinueRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    answers: List[PHQ9QuestionAnswer] = Field(default_factory=list, description= "The score (0-3) for the question just answered")
    incoming_score: PHQ9AnswerValue = Field(...,
                                            description="The score (0-3) for the question just answered")
    notes: Optional[str] = Field(default=None, min_length=1, max_length=1000,description="Optional note to attach to this conversation")

class PHQ9ConversationResponse(BaseModel):  # Define the safe, validated shape sent back for every /start and /continue call
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # Reject unknown fields, same safety rule as every other schema
    assistant_message: Optional[str] = Field(default=None, description="The next question to show the user, or a completion message")  # The question text (or final message) the frontend displays
    score_options: Optional[dict[int, str]] = Field(default=None, description="Valid answer choices to display, e.g. 0=Not at all")  # The 0-3 options dict, so the frontend can render answer buttons
    current_question_id: Optional[int] = Field(default=None, ge=1, le=9, description="Which PHQ-9 question number is being asked right now")  # Tells the frontend which question (1-9) is currently active
    answers: List[PHQ9QuestionAnswer] = Field(default_factory=list, description="All answers collected so far in this conversation")  # The running history, so the frontend can pass it back into the next /continue call
    is_complete: bool = Field(default=False, description="Whether all 9 PHQ-9 questions have been answered")  # Tells the frontend whether to keep asking or show the result
    needs_answer: bool = Field(default=False, description="Whether the frontend should currently show an answer prompt")  # Tells the frontend whether to render the answer buttons right now
    result: Optional[PHQ9AssessmentResult] = Field(default=None, description="Final scored PHQ-9 result, only present once is_complete is true")  # The final score/severity/recommendation, only filled in at the very end
    crisis_support: Optional[PHQ9CrisisSupport] = Field(default=None, description="Crisis resources, only present if item 9 signaled risk")  # Safety resources, only filled in if needed
    Error: Optional[str] = Field(default=None, description="Validation error message, e.g. if an invalid score was submitted")  # Tells the frontend if something went wrong with the last answer

"""
#####################################################################################################
This part is where we make the schema about the Report generation part by the LLM
#####################################################################################################
"""
class PHQ9ReportResult(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    insight_report: str = Field(..., description="Report generated by LLM")
    remedies: list[str] = Field(default_factory=list, description="Remedies generated by LLM")
    sources: list[str] = Field(default_factory=list, description="Sources generated by LLM")