import pandera as pa
from pandera import Column, DataFrameSchema, Check


EquitiesSchema = DataFrameSchema(
    {
        "Date": Column(pa.DateTime, nullable=False),
        "Open": Column(float, Check.ge(0)),
        "High": Column(float, Check.ge(0)),
        "Low": Column(float, Check.ge(0)),
        "Close": Column(float, Check.ge(0)),
        "Adj Close": Column(float, Check.ge(0)),
        "Volume": Column(int, Check.ge(0)),

    },
    checks=[
        Check(
            lambda df: df["High"] >= df["Low"],
            error="High price must be >= Low price",
        ),
        Check(
            lambda df: df["Date"].is_unique,
            error="Duplicate timestamps detected",
        ),
    ],
    strict=True,
)
