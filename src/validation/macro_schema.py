import pandera as pa
from pandera import Column, DataFrameSchema, Check


MacroSchema = DataFrameSchema(
    {
        "date": Column(pa.DateTime, nullable=False),
        "DFF": Column(float, Check.ge(0)),  # Fed Funds Rate >= 0
    },
    checks=[
        Check(
            lambda df: df["date"].is_unique,
            error="Duplicate macro timestamps detected",
        )
    ],
    strict=True,
)
