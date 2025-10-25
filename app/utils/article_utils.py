from typing import Dict, List

import pandas as pd


def deduplicate(new_records: List[Dict], existing_df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates from new_records based on 'article_id' against existing_df."""
    new_df = pd.DataFrame(new_records)
    if existing_df.empty:
        return new_df

    deduped_df = new_df[~new_df["article_id"].isin(existing_df["article_id"])]
    return deduped_df
