from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime


class GeneState(str, Enum):
    MUTATED = "MUTATED"
    NOT_MUTATED = "NOT_MUTATED"


class Gender(str, Enum):
    Male = "Male"
    Female = "Female"


class Race(str, Enum):
    white = "white"
    asian = "asian"
    black = "black or african american"


class PrimaryDiagnosis(str, Enum):
    Oligodendroglioma_NOS = "Oligodendroglioma, NOS"
    Mixed_glioma = "Mixed glioma"
    Astrocytoma_NOS = "Astrocytoma, NOS"
    Astrocytoma_anaplastic = "Astrocytoma, anaplastic"
    Oligodendroglioma_anaplastic = "Oligodendroglioma, anaplastic"
    Glioblastoma = "Glioblastoma"


class GliomaClassifierInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    Gender: Gender
    Age_at_diagnosis: int
    Primary_Diagnosis: PrimaryDiagnosis
    Race: Race
    IDH1: GeneState
    TP53: GeneState
    ATRX: GeneState
    PTEN: GeneState
    EGFR: GeneState
    CIC: GeneState
    MUC16: GeneState
    PIK3CA: GeneState
    NF1: GeneState
    PIK3R1: GeneState
    FUBP1: GeneState
    RB1: GeneState
    NOTCH1: GeneState
    BCOR: GeneState
    CSMD3: GeneState
    SMARCA4: GeneState
    GRIN2A: GeneState
    IDH2: GeneState
    FAT4: GeneState
    PDGFRA: GeneState


class Grade(str, Enum):
    LGG = "LGG"
    GBM = "GBM"


class PredictionBase(GliomaClassifierInput):
    pass


class PredictionCreateSchema(PredictionBase):
    pass


class PredictionOutSchema(GliomaClassifierInput):
    result: Optional[str]
    rq_status: Optional[str]
    started_at: datetime
    model_id: int


class PreductionCreationOutput(BaseModel):
    id: int
