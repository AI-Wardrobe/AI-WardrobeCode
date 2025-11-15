import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """
    Run basic validation checks on the tags DataFrame.

    Returns:
        A list of human-readable issue strings. If empty, data looks OK.
    """
    issues: list[str] = []

    # Required-ish columns (we're flexible with names in the loader)
    # Here we just check that something like filename exists later.
    cols = [c.lower() for c in df.columns]

    # Check row-by-row
    for idx, row in df.iterrows():
        # ---- filename checks ----
        filename = (
            row.get("filename")
            or row.get("image_name")
            or row.get("file")
        )

        if not isinstance(filename, str) or not filename.strip():
            issues.append(f"Row {idx}: missing or invalid filename")

        # ---- dominant_color checks ----
        if "dominant_color" in row or "color" in row:
            color = row.get("dominant_color") or row.get("color")
            if isinstance(color, str):
                # Expect something like rgb(123,45,67)
                if not color.startswith("rgb(") or not color.endswith(")"):
                    issues.append(
                        f"Row {idx}: color '{color}' is not in rgb(R,G,B) format"
                    )

        # ---- formality checks ----
        if "formality" in row and pd.notna(row["formality"]):
            try:
                formality_value = int(row["formality"])
                if formality_value < 0 or formality_value > 5:
                    issues.append(
                        f"Row {idx}: formality {formality_value} out of expected range 0–5"
                    )
            except (TypeError, ValueError):
                issues.append(
                    f"Row {idx}: formality '{row['formality']}' is not an integer"
                )

    return issues
