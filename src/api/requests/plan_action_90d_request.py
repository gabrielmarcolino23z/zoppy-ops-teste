from typing import List
from pydantic import BaseModel, Field

class MeetingTranscriptQA(BaseModel):
    """Modelo para uma pergunta e resposta da transcrição da reunião"""
    question: str
    answer: str

class PlanAction90dRequest(BaseModel):
    """
    Modelo de requisição para geração de plano de ação de 90 dias
    """
    company_name: str = Field(..., description="Nome do cliente")
    plan: str = Field(..., description="Plano do cliente")
    commercial_transcript: str = Field(
        ...,
        description="Transcrição completa da reunião comercial"
    )
    onboarding_transcript: str = Field(
        ...,
        description="Transcrição completa da reunião de onboarding"
    )
    discovery_transcript: str = Field(
        ...,
        description="Transcrição completa da reunião de discovery"
    )
    commercial_meeting: List[MeetingTranscriptQA] = Field(
        default=[],
        description="Lista de perguntas e respostas estruturadas da reunião comercial"
    )
    onboarding_meeting: List[MeetingTranscriptQA] = Field(
        default=[],
        description="Lista de perguntas e respostas estruturadas da reunião de onboarding"
    )
    discovery_meeting: List[MeetingTranscriptQA] = Field(
        default=[],
        description="Lista de perguntas e respostas estruturadas da reunião de discovery"
    )