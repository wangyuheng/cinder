"""
Soul API - REST endpoints for Soul configuration management.
"""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cinder_cli.config import Config
from cinder_cli.database.questionnaire_dao import QuestionnaireDAO
from cinder_cli.database.user_dao import UserDAO
from cinder_cli.question_guide import QUESTIONS, TRAITS

router = APIRouter()


class SoulTraits(BaseModel):
    """Soul traits model."""

    risk_tolerance: int = 50
    structure: int = 50
    detail_orientation: int = 50
    communication_style: str = "balanced"


class SoulConfig(BaseModel):
    """Soul configuration model."""

    traits: SoulTraits = SoulTraits()


def get_soul_path() -> tuple[Any, str]:
    """Get soul configuration path and data."""
    config = Config()
    soul_path = config.get("soul_path", "soul.md")
    meta_path = soul_path.replace(".md", ".meta.yaml")

    try:
        with open(meta_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {"traits": SoulTraits().model_dump()}

    return data, meta_path


@router.get("")
async def get_soul() -> dict[str, Any]:
    """Get current Soul configuration."""
    data, _ = get_soul_path()
    return data


@router.put("")
async def update_soul(config: SoulConfig) -> dict[str, Any]:
    """Update Soul configuration."""
    data, meta_path = get_soul_path()

    data["traits"] = config.traits.model_dump()

    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)

    return {"status": "updated", "traits": config.traits.model_dump()}


@router.post("/init")
async def init_soul() -> dict[str, Any]:
    """Initialize Soul configuration with defaults."""
    _, meta_path = get_soul_path()

    default_config = SoulConfig()
    data = {"traits": default_config.traits.model_dump()}

    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)

    return {"status": "initialized", "traits": default_config.traits.model_dump()}


class QuestionOption(BaseModel):
    """Question option model."""
    
    key: str
    text: str
    summary: str


class QuestionResponse(BaseModel):
    """Question response model."""
    
    key: str
    title: str
    prompt: str
    dimension: str
    options: list[QuestionOption]


class SubmitAnswerRequest(BaseModel):
    """Submit answer request model."""
    
    user_id: int
    question_key: str
    choice: str
    reason: str = ""


class AnswerResponse(BaseModel):
    """Answer response model."""
    
    question_key: str
    choice: str
    reason: str


class ProgressResponse(BaseModel):
    """Progress response model."""
    
    completed: int
    total: int
    answers: dict[str, Any]


@router.get("/questionnaire", response_model=list[QuestionResponse])
async def get_questionnaire() -> list[dict[str, Any]]:
    """Get all questionnaire questions."""
    questions = []
    for q in QUESTIONS:
        questions.append({
            "key": q.key,
            "title": q.title,
            "prompt": q.prompt,
            "dimension": q.dimension,
            "options": [
                {"key": opt.key, "text": opt.text, "summary": opt.summary}
                for opt in q.options
            ],
        })
    return questions


@router.post("/questionnaire", response_model=AnswerResponse)
async def submit_answer(request: SubmitAnswerRequest) -> dict[str, Any]:
    """Submit a questionnaire answer."""
    dao = QuestionnaireDAO()
    answer = dao.save_answer(
        request.user_id,
        request.question_key,
        request.choice,
        request.reason,
    )
    
    return {
        "question_key": answer.question_key,
        "choice": answer.choice,
        "reason": answer.reason,
    }


@router.get("/questionnaire/progress", response_model=ProgressResponse)
async def get_progress(user_id: int) -> dict[str, Any]:
    """Get questionnaire progress."""
    dao = QuestionnaireDAO()
    progress = dao.get_progress(user_id)
    
    return {
        "completed": progress["completed"],
        "total": progress["total"],
        "answers": progress["answers"],
    }


@router.delete("/questionnaire/progress")
async def clear_progress(user_id: int) -> dict[str, Any]:
    """Clear questionnaire progress."""
    dao = QuestionnaireDAO()
    dao.clear_progress(user_id)
    
    return {"status": "cleared"}


@router.post("/questionnaire/complete")
async def complete_questionnaire(user_id: int) -> dict[str, Any]:
    """Complete questionnaire and generate soul profile."""
    dao = QuestionnaireDAO()
    answers = dao.get_all_answers(user_id)
    
    if len(answers) < 6:
        raise HTTPException(status_code=400, detail="Not all questions answered")
    
    scores = {trait: 50 for trait in TRAITS}
    
    for answer in answers:
        question = next((q for q in QUESTIONS if q.key == answer.question_key), None)
        if question:
            option = next((opt for opt in question.options if opt.key == answer.choice), None)
            if option:
                for trait, delta in option.effects.items():
                    scores[trait] = max(0, min(100, scores[trait] + delta))
    
    user_dao = UserDAO()
    user = user_dao.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    config = Config()
    soul_path = config.get("soul_path", "soul.md")
    meta_path = soul_path.replace(".md", ".meta.yaml")
    
    data = {
        "version": 2,
        "source": "web_questionnaire",
        "question_count": 6,
        "confidence": "medium",
        "name": user.name,
        "raw_answers": {
            ans.question_key: {
                "dimension": next((q.dimension for q in QUESTIONS if q.key == ans.question_key), ""),
                "choice": ans.choice,
                "reason": ans.reason,
            }
            for ans in answers
        },
        "traits": scores,
        "core_traits": [],
        "decision_profile": {},
        "agent_directives": {},
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)
    
    user_dao.update_soul_path(user_id, meta_path)
    user_dao.update_onboarding_status(user_id, True)
    
    return {"status": "completed", "soul_path": meta_path, "traits": scores}
