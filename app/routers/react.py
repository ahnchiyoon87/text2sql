from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.deps import get_db_connection, get_neo4j_session, get_openai_client
from app.core.sql_exec import SQLExecutor, SQLExecutionError
from app.core.sql_guard import SQLGuard, SQLValidationError
from app.react.agent import AgentOutcome, ReactAgent, ReactStep
from app.react.state import ReactSessionState
from app.react.tools import ToolContext


router = APIRouter(prefix="/react", tags=["ReAct"])

PROMPT_PATH = Path(__file__).resolve().parents[1] / "react" / "prompt.xml"


def _to_cdata(value: str) -> str:
    return f"<![CDATA[{value}]]>"


class SQLCompletenessModel(BaseModel):
    is_complete: bool
    missing_info: str
    confidence_level: str


class ToolCallModel(BaseModel):
    name: str
    raw_parameters_xml: str
    parameters: Dict[str, Any]


class ReactStepModel(BaseModel):
    iteration: int
    reasoning: str
    metadata_xml: str
    partial_sql: str
    sql_completeness: SQLCompletenessModel
    tool_call: ToolCallModel
    tool_result: Optional[str] = None
    llm_output: str


class ExecutionResultModel(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float


class ReactResponse(BaseModel):
    status: Literal["completed", "needs_user_input"]
    final_sql: Optional[str] = None
    validated_sql: Optional[str] = None
    execution_result: Optional[ExecutionResultModel] = None
    steps: List[ReactStepModel] = Field(default_factory=list)
    collected_metadata: str
    partial_sql: str
    remaining_tool_calls: int
    session_state: Optional[str] = None
    question_to_user: Optional[str] = None
    warnings: Optional[List[str]] = None


class ReactRequest(BaseModel):
    question: str = Field(..., description="사용자 자연어 질문")
    dbms: Optional[str] = Field(default=None, description="DBMS 타입 (기본값: 설정값)")
    max_tool_calls: int = Field(default=30, ge=1, le=100)
    execute_final_sql: bool = Field(default=True, description="최종 SQL을 실제로 실행할지 여부")
    max_iterations: Optional[int] = Field(default=None, ge=1, le=20)
    session_state: Optional[str] = Field(default=None, description="이전 세션 상태 토큰")
    user_response: Optional[str] = Field(default=None, description="ask_user 툴에 대한 사용자 응답")


def _step_to_model(step: ReactStep) -> ReactStepModel:
    return ReactStepModel(
        iteration=step.iteration,
        reasoning=step.reasoning,
        metadata_xml=step.metadata_xml,
        partial_sql=step.partial_sql,
        sql_completeness=SQLCompletenessModel(
            is_complete=step.sql_completeness.is_complete,
            missing_info=step.sql_completeness.missing_info,
            confidence_level=step.sql_completeness.confidence_level,
        ),
        tool_call=ToolCallModel(
            name=step.tool_call.name,
            raw_parameters_xml=step.tool_call.raw_parameters_xml,
            parameters=step.tool_call.parsed_parameters,
        ),
        tool_result=step.tool_result,
        llm_output=step.llm_output,
    )


def _ensure_state_from_request(request: ReactRequest) -> ReactSessionState:
    if request.session_state:
        return ReactSessionState.from_token(request.session_state)
    dbms = request.dbms or settings.target_db_type
    return ReactSessionState.new(
        user_query=request.question,
        dbms=dbms,
        remaining_tool_calls=request.max_tool_calls,
    )


@router.post("", response_model=ReactResponse)
async def run_react(
    request: ReactRequest,
    neo4j_session=Depends(get_neo4j_session),
    db_conn=Depends(get_db_connection),
    openai_client=Depends(get_openai_client),
) -> ReactResponse:
    state = _ensure_state_from_request(request)

    tool_context = ToolContext(
        neo4j_session=neo4j_session,
        db_conn=db_conn,
        openai_client=openai_client,
    )

    agent = ReactAgent(PROMPT_PATH)
    outcome = await agent.run(
        state=state,
        tool_context=tool_context,
        max_iterations=request.max_iterations,
        user_response=request.user_response,
    )

    steps = [_step_to_model(step) for step in outcome.steps]
    warnings: List[str] = []

    if outcome.status == "ask_user":
        question = outcome.question_to_user or ""
        state.current_tool_result = (
            "<tool_result>"
            f"<ask_user_question>{_to_cdata(question)}</ask_user_question>"
            "</tool_result>"
        )
        session_token = state.to_token()
        return ReactResponse(
            status="needs_user_input",
            steps=steps,
            collected_metadata=state.metadata.to_xml(),
            partial_sql=state.partial_sql,
            remaining_tool_calls=state.remaining_tool_calls,
            session_state=session_token,
            question_to_user=question,
            warnings=warnings or None,
        )

    if outcome.status != "submit_sql":
        raise HTTPException(status_code=500, detail="Agent did not complete with submit_sql.")

    final_sql = outcome.final_sql or ""
    validated_sql = None
    execution_result = None

    guard = SQLGuard()
    try:
        validated_sql, _ = guard.validate(final_sql)
    except SQLValidationError as exc:
        raise HTTPException(status_code=400, detail=f"SQL validation failed: {exc}") from exc

    if request.execute_final_sql:
        executor = SQLExecutor()
        try:
            raw_result = await executor.execute_query(db_conn, validated_sql)
            formatted = executor.format_results_for_json(raw_result)
            execution_result = ExecutionResultModel(**formatted)
        except SQLExecutionError as exc:
            warnings.append(f"SQL execution failed: {exc}")

    return ReactResponse(
        status="completed",
        final_sql=final_sql,
        validated_sql=validated_sql,
        execution_result=execution_result,
        steps=steps,
        collected_metadata=state.metadata.to_xml(),
        partial_sql=state.partial_sql,
        remaining_tool_calls=state.remaining_tool_calls,
        session_state=None,
        question_to_user=None,
        warnings=warnings or None,
    )
